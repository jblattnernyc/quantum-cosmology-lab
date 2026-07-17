"""Content-based prerequisites for progression to IBM hardware execution."""

from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path
from typing import Any

from qclab.validation.assessment import assess_observable_values
from qclab.validation.fingerprints import benchmark_fingerprint
from qclab.validation.records import (
    HardwarePreflightResult,
    HardwareValidationGateError,
    TierAssessment,
    ValidationContext,
)


def _load_json_object(path: str | Path, *, label: str) -> dict[str, Any]:
    """Load one required JSON artifact as a mapping."""

    resolved_path = Path(path).expanduser().resolve()
    if not resolved_path.is_file():
        raise HardwareValidationGateError(
            f"{label} artifact does not exist: {resolved_path}"
        )
    try:
        payload = json.loads(resolved_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HardwareValidationGateError(
            f"{label} artifact is not readable JSON: {resolved_path}"
        ) from exc
    if not isinstance(payload, dict):
        raise HardwareValidationGateError(
            f"{label} artifact must contain a JSON object."
        )
    return payload


def _artifact_context(
    payload: Mapping[str, Any],
    *,
    label: str,
) -> ValidationContext:
    """Parse the required context from an artifact."""

    raw_context = payload.get("validation_context")
    if not isinstance(raw_context, dict):
        raise HardwareValidationGateError(
            f"{label} artifact lacks a validation_context and is legacy or incomplete."
        )
    try:
        return ValidationContext.from_mapping(raw_context)
    except ValueError as exc:
        raise HardwareValidationGateError(
            f"{label} artifact has an invalid validation_context."
        ) from exc


def _require_matching_context(
    artifact_context: ValidationContext,
    current_context: ValidationContext,
    *,
    label: str,
) -> None:
    """Reject evidence from any other configuration or benchmark lineage."""

    if artifact_context != current_context:
        raise HardwareValidationGateError(
            f"{label} artifact lineage does not match the current configuration. "
            "Regenerate the benchmark, exact-local, and noisy-local artifacts."
        )


def _assess_execution_artifact(
    *,
    payload: Mapping[str, Any],
    label: str,
    tier: str,
    current_context: ValidationContext,
    benchmark_values: Mapping[str, float],
    validation_configuration: Mapping[str, Any],
) -> TierAssessment:
    """Recompute and verify one persisted local-tier assessment."""

    _require_matching_context(
        _artifact_context(payload, label=label),
        current_context,
        label=label,
    )
    request = payload.get("request")
    provenance = payload.get("provenance")
    if not isinstance(request, Mapping) or request.get("tier") != tier:
        raise HardwareValidationGateError(
            f"{label} artifact request tier is not {tier!r}."
        )
    if not isinstance(provenance, Mapping) or provenance.get("tier") != tier:
        raise HardwareValidationGateError(
            f"{label} artifact provenance tier is not {tier!r}."
        )
    evaluations = payload.get("evaluations")
    if not isinstance(evaluations, list):
        raise HardwareValidationGateError(
            f"{label} artifact evaluations must be a list."
        )
    try:
        assessment = assess_observable_values(
            tier=tier,
            lineage_id=current_context.lineage_id,
            evaluations=evaluations,
            benchmark_values=benchmark_values,
            validation_configuration=validation_configuration,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise HardwareValidationGateError(
            f"{label} artifact could not be assessed under the current policy."
        ) from exc
    stored_assessment = payload.get("validation_assessment")
    if stored_assessment != assessment.to_serializable():
        raise HardwareValidationGateError(
            f"{label} stored assessment is missing or does not match a fresh assessment."
        )
    if not assessment.passed:
        raise HardwareValidationGateError(
            f"{label} artifact fails the configured observable acceptance policy."
        )
    return assessment


def validate_hardware_prerequisites(
    *,
    current_context: ValidationContext,
    benchmark_values: Mapping[str, float],
    validation_configuration: Mapping[str, Any],
    benchmark_path: str | Path,
    exact_local_path: str | Path,
    noisy_local_path: str | Path,
    additional_assessments: tuple[TierAssessment, ...] = (),
) -> HardwarePreflightResult:
    """Require current, passing benchmark, local, and additional evidence."""

    for assessment in additional_assessments:
        if assessment.lineage_id != current_context.lineage_id:
            raise HardwareValidationGateError(
                f"{assessment.tier} assessment lineage does not match the current "
                "configuration."
            )
        if not assessment.passed:
            raise HardwareValidationGateError(
                f"{assessment.tier} assessment fails its configured acceptance policy."
            )

    benchmark_payload = _load_json_object(benchmark_path, label="Benchmark")
    _require_matching_context(
        _artifact_context(benchmark_payload, label="Benchmark"),
        current_context,
        label="Benchmark",
    )
    base_benchmark_payload = dict(benchmark_payload)
    base_benchmark_payload.pop("validation_context", None)
    if (
        benchmark_fingerprint(base_benchmark_payload)
        != current_context.benchmark_fingerprint
    ):
        raise HardwareValidationGateError(
            "Benchmark artifact content does not match its validation fingerprint."
        )

    exact_payload = _load_json_object(exact_local_path, label="Exact-local")
    noisy_payload = _load_json_object(noisy_local_path, label="Noisy-local")
    exact_assessment = _assess_execution_artifact(
        payload=exact_payload,
        label="Exact-local",
        tier="exact_local",
        current_context=current_context,
        benchmark_values=benchmark_values,
        validation_configuration=validation_configuration,
    )
    noisy_assessment = _assess_execution_artifact(
        payload=noisy_payload,
        label="Noisy-local",
        tier="noisy_local",
        current_context=current_context,
        benchmark_values=benchmark_values,
        validation_configuration=validation_configuration,
    )
    return HardwarePreflightResult(
        experiment_name=current_context.experiment_name,
        lineage_id=current_context.lineage_id,
        exact_local_assessment=exact_assessment,
        noisy_local_assessment=noisy_assessment,
        additional_assessments=additional_assessments,
    )
