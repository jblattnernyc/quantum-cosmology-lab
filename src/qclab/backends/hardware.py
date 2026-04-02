"""IBM Runtime hardware policy, provenance capture, and report helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
from pathlib import Path
import re
from typing import TYPE_CHECKING, Any

from qclab.utils.optional import require_dependency
from qclab.utils.paths import repository_relative_path

if TYPE_CHECKING:
    from qclab.analysis.comparison import ComparisonRecord
    from qclab.backends.execution import EstimatorExecutionResult


class BackendSelectionStrategy(str, Enum):
    """Supported IBM backend-selection strategies."""

    EXPLICIT = "explicit"
    LEAST_BUSY = "least_busy"


@dataclass(frozen=True)
class BackendSelectionPolicy:
    """Inspectable IBM backend-selection policy."""

    strategy: BackendSelectionStrategy = BackendSelectionStrategy.EXPLICIT
    min_num_qubits: int | None = None
    operational: bool = True
    simulator: bool = False
    dynamic_circuits: bool | None = None
    use_fractional_gates: bool | None = False
    calibration_id: str | None = None
    filters: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.min_num_qubits is not None and self.min_num_qubits <= 0:
            raise ValueError(
                "BackendSelectionPolicy.min_num_qubits must be positive when set."
            )
        if (
            self.strategy is BackendSelectionStrategy.LEAST_BUSY
            and self.calibration_id is not None
        ):
            raise ValueError(
                "BackendSelectionPolicy.calibration_id is only supported for explicit backend selection."
            )


@dataclass(frozen=True)
class MitigationPolicy:
    """Inspectable mitigation policy for IBM Runtime estimator execution."""

    resilience_level: int = 0
    measure_mitigation: bool | None = None
    twirling_enable_gates: bool | None = None
    twirling_enable_measure: bool | None = None
    dynamical_decoupling_enable: bool | None = None
    dynamical_decoupling_sequence_type: str | None = None

    def __post_init__(self) -> None:
        if self.resilience_level not in {0, 1, 2}:
            raise ValueError(
                "MitigationPolicy.resilience_level must be one of {0, 1, 2}."
            )


def _json_safe(value: Any) -> Any:
    """Convert common runtime payloads into JSON-safe structures."""

    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except TypeError:
            pass
    if hasattr(value, "tolist"):
        return _json_safe(value.tolist())
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if hasattr(value, "to_dict"):
        try:
            return _json_safe(value.to_dict())
        except TypeError:
            pass
    if hasattr(value, "value") and isinstance(getattr(value, "value"), str):
        return value.value
    return repr(value)


def _deep_merge(base: dict[str, Any], update: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively merge ``update`` into ``base`` and return the merged mapping."""

    merged = dict(base)
    for key, value in update.items():
        if (
            isinstance(value, Mapping)
            and isinstance(merged.get(key), Mapping)
        ):
            merged[key] = _deep_merge(dict(merged[key]), value)
        else:
            merged[key] = _json_safe(value)
    return merged


def _mapping_from_value(value: Mapping[str, Any] | None) -> dict[str, Any]:
    """Normalize an optional mapping into a mutable dictionary."""

    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError("Expected a mapping for IBM Runtime policy configuration.")
    return dict(value)


def backend_selection_policy_from_mapping(
    value: Mapping[str, Any] | None,
) -> BackendSelectionPolicy:
    """Build a backend-selection policy from execution configuration metadata."""

    mapping = _mapping_from_value(value)
    strategy = BackendSelectionStrategy(str(mapping.get("strategy", "explicit")))
    filters = mapping.get("filters", {})
    if filters is None:
        filters = {}
    if not isinstance(filters, Mapping):
        raise TypeError("Backend selection filters must be provided as a mapping.")
    return BackendSelectionPolicy(
        strategy=strategy,
        min_num_qubits=(
            None
            if mapping.get("min_num_qubits") is None
            else int(mapping.get("min_num_qubits"))
        ),
        operational=bool(mapping.get("operational", True)),
        simulator=bool(mapping.get("simulator", False)),
        dynamic_circuits=(
            None
            if mapping.get("dynamic_circuits") is None
            else bool(mapping.get("dynamic_circuits"))
        ),
        use_fractional_gates=(
            None
            if mapping.get("use_fractional_gates") is None
            else bool(mapping.get("use_fractional_gates"))
        ),
        calibration_id=(
            None
            if mapping.get("calibration_id") is None
            else str(mapping.get("calibration_id"))
        ),
        filters=dict(filters),
    )


def mitigation_policy_from_mapping(
    value: Mapping[str, Any] | None,
    *,
    default_enabled: bool = False,
) -> MitigationPolicy:
    """Build a mitigation policy from execution configuration metadata."""

    mapping = _mapping_from_value(value)
    if not mapping and default_enabled:
        return MitigationPolicy(
            resilience_level=1,
            measure_mitigation=True,
            twirling_enable_measure=True,
        )
    return MitigationPolicy(
        resilience_level=int(mapping.get("resilience_level", 0)),
        measure_mitigation=(
            None
            if mapping.get("measure_mitigation") is None
            else bool(mapping.get("measure_mitigation"))
        ),
        twirling_enable_gates=(
            None
            if mapping.get("twirling_enable_gates") is None
            else bool(mapping.get("twirling_enable_gates"))
        ),
        twirling_enable_measure=(
            None
            if mapping.get("twirling_enable_measure") is None
            else bool(mapping.get("twirling_enable_measure"))
        ),
        dynamical_decoupling_enable=(
            None
            if mapping.get("dynamical_decoupling_enable") is None
            else bool(mapping.get("dynamical_decoupling_enable"))
        ),
        dynamical_decoupling_sequence_type=(
            None
            if mapping.get("dynamical_decoupling_sequence_type") is None
            else str(mapping.get("dynamical_decoupling_sequence_type"))
        ),
    )


def mitigation_policy_to_serializable(policy: MitigationPolicy) -> dict[str, Any]:
    """Return a JSON-safe mitigation-policy record."""

    return _json_safe(asdict(policy))


def backend_selection_policy_to_serializable(
    policy: BackendSelectionPolicy,
) -> dict[str, Any]:
    """Return a JSON-safe backend-selection-policy record."""

    payload = asdict(policy)
    payload["strategy"] = policy.strategy.value
    return _json_safe(payload)


def parse_ibm_runtime_options(
    raw_options: Mapping[str, Any] | None,
    *,
    shots: int | None = None,
    mitigation_enabled: bool = False,
) -> tuple[BackendSelectionPolicy, MitigationPolicy, dict[str, Any]]:
    """Split raw request options into policy objects and primitive options."""

    options = _mapping_from_value(raw_options)
    selection_policy = backend_selection_policy_from_mapping(
        options.pop("selection_policy", None)
    )
    mitigation_policy = mitigation_policy_from_mapping(
        options.pop("mitigation_policy", None),
        default_enabled=mitigation_enabled,
    )
    runtime_options = _mapping_from_value(options.pop("runtime_options", None))
    merged_options = _deep_merge(options, runtime_options)
    if shots is not None:
        merged_options.setdefault("default_shots", shots)
    merged_options.setdefault("resilience_level", mitigation_policy.resilience_level)
    if mitigation_policy.measure_mitigation is not None:
        merged_options.setdefault("resilience", {})
        merged_options["resilience"].setdefault(
            "measure_mitigation",
            mitigation_policy.measure_mitigation,
        )
    if mitigation_policy.twirling_enable_gates is not None:
        merged_options.setdefault("twirling", {})
        merged_options["twirling"].setdefault(
            "enable_gates",
            mitigation_policy.twirling_enable_gates,
        )
    if mitigation_policy.twirling_enable_measure is not None:
        merged_options.setdefault("twirling", {})
        merged_options["twirling"].setdefault(
            "enable_measure",
            mitigation_policy.twirling_enable_measure,
        )
    if mitigation_policy.dynamical_decoupling_enable is not None:
        merged_options.setdefault("dynamical_decoupling", {})
        merged_options["dynamical_decoupling"].setdefault(
            "enable",
            mitigation_policy.dynamical_decoupling_enable,
        )
    if mitigation_policy.dynamical_decoupling_sequence_type is not None:
        merged_options.setdefault("dynamical_decoupling", {})
        merged_options["dynamical_decoupling"].setdefault(
            "sequence_type",
            mitigation_policy.dynamical_decoupling_sequence_type,
        )
    return selection_policy, mitigation_policy, merged_options


def _safe_attribute(value: Any, attribute_name: str) -> Any:
    """Return an attribute value, invoking it when callable."""

    attribute = getattr(value, attribute_name, None)
    if attribute is None:
        return None
    try:
        return attribute() if callable(attribute) else attribute
    except Exception as exc:  # pragma: no cover - defensive capture
        return f"{type(exc).__name__}: {exc}"


def _backend_name(backend: Any) -> str | None:
    """Return a backend name when available."""

    name = _safe_attribute(backend, "name")
    if name is None:
        return None
    return str(name)


def instantiate_local_testing_backend(backend_class_name: str) -> Any:
    """Instantiate a fake backend for IBM Runtime local testing mode."""

    fake_provider = require_dependency(
        "qiskit_ibm_runtime.fake_provider",
        "instantiate a local-testing backend without credentials",
    )
    backend_class = getattr(fake_provider, backend_class_name, None)
    if backend_class is None:
        raise ValueError(
            f"Unknown local-testing backend class: {backend_class_name!r}."
        )
    return backend_class()


def resolve_ibm_backend(
    *,
    request_backend_name: str,
    service: Any | None,
    policy: BackendSelectionPolicy,
    instance: str | None = None,
    provided_backend: Any | None = None,
) -> tuple[Any, dict[str, Any]]:
    """Resolve the backend used for an IBM Runtime execution."""

    if provided_backend is not None:
        selected_backend_name = _backend_name(provided_backend) or request_backend_name
        return provided_backend, {
            "strategy": policy.strategy.value,
            "requested_backend_name": request_backend_name,
            "selected_backend_name": selected_backend_name,
            "instance": instance,
            "local_testing_mode": True,
            "selection_filters": backend_selection_policy_to_serializable(policy),
        }
    if service is None:
        raise ValueError("An IBM Runtime service is required when no backend is provided.")
    if policy.strategy is BackendSelectionStrategy.LEAST_BUSY:
        least_busy_kwargs: dict[str, Any] = {
            "instance": instance,
            "operational": policy.operational,
            "simulator": policy.simulator,
        }
        if policy.min_num_qubits is not None:
            least_busy_kwargs["min_num_qubits"] = policy.min_num_qubits
        if policy.dynamic_circuits is not None:
            least_busy_kwargs["dynamic_circuits"] = policy.dynamic_circuits
        least_busy_kwargs.update(policy.filters)
        backend = service.least_busy(**least_busy_kwargs)
        selected_backend_name = _backend_name(backend) or request_backend_name
        return backend, {
            "strategy": policy.strategy.value,
            "requested_backend_name": request_backend_name,
            "selected_backend_name": selected_backend_name,
            "instance": instance,
            "local_testing_mode": False,
            "selection_filters": _json_safe(least_busy_kwargs),
        }
    explicit_backend_name = request_backend_name.strip()
    if not explicit_backend_name or explicit_backend_name == "ibm_backend_required":
        raise ValueError(
            "An explicit backend name is required by the configured backend-selection policy."
        )
    backend_kwargs = {"instance": instance}
    if policy.use_fractional_gates is not None:
        backend_kwargs["use_fractional_gates"] = policy.use_fractional_gates
    if policy.calibration_id is not None:
        backend_kwargs["calibration_id"] = policy.calibration_id
    backend = service.backend(explicit_backend_name, **backend_kwargs)
    selected_backend_name = _backend_name(backend) or explicit_backend_name
    return backend, {
        "strategy": policy.strategy.value,
        "requested_backend_name": explicit_backend_name,
        "selected_backend_name": selected_backend_name,
        "instance": instance,
        "local_testing_mode": False,
        "selection_filters": _json_safe(backend_kwargs),
    }


def summarize_backend(backend: Any) -> dict[str, Any]:
    """Return a compact backend summary for execution provenance."""

    if backend is None:
        return {}
    properties = None
    properties_method = getattr(backend, "properties", None)
    if callable(properties_method):
        try:
            properties = properties_method(refresh=False)
        except TypeError:
            properties = properties_method()
        except Exception as exc:  # pragma: no cover - defensive capture
            properties = f"{type(exc).__name__}: {exc}"
    status = _safe_attribute(backend, "status")
    coupling_map = _safe_attribute(backend, "coupling_map")
    coupling_edges = None
    if coupling_map is not None and hasattr(coupling_map, "get_edges"):
        try:
            coupling_edges = len(coupling_map.get_edges())
        except Exception:  # pragma: no cover - defensive capture
            coupling_edges = None
    elif isinstance(coupling_map, Sequence):
        coupling_edges = len(coupling_map)
    last_update_date = getattr(properties, "last_update_date", None)
    status_payload: dict[str, Any] | None = None
    if status is not None and not isinstance(status, str):
        status_payload = {
            "backend_name": _json_safe(getattr(status, "backend_name", None)),
            "backend_version": _json_safe(getattr(status, "backend_version", None)),
            "operational": _json_safe(getattr(status, "operational", None)),
            "pending_jobs": _json_safe(getattr(status, "pending_jobs", None)),
            "status_msg": _json_safe(getattr(status, "status_msg", None)),
        }
    elif status is not None:
        status_payload = {"status": _json_safe(status)}
    return {
        "backend_name": _backend_name(backend),
        "backend_class": type(backend).__name__,
        "num_qubits": _json_safe(getattr(backend, "num_qubits", None)),
        "version": _json_safe(_safe_attribute(backend, "version")),
        "operation_names": _json_safe(_safe_attribute(backend, "operation_names")),
        "coupling_edge_count": coupling_edges,
        "max_circuits": _json_safe(getattr(backend, "max_circuits", None)),
        "calibration_id": _json_safe(_safe_attribute(backend, "calibration_id")),
        "status": status_payload,
        "properties_last_update_date": _json_safe(last_update_date),
    }


def capture_backend_calibration(backend: Any) -> dict[str, Any]:
    """Return a fuller backend calibration snapshot for raw metadata capture."""

    if backend is None:
        return {}
    payload = {"summary": summarize_backend(backend)}
    properties = None
    properties_method = getattr(backend, "properties", None)
    if callable(properties_method):
        try:
            properties = properties_method(refresh=False)
        except TypeError:
            properties = properties_method()
        except Exception as exc:  # pragma: no cover - defensive capture
            properties = f"{type(exc).__name__}: {exc}"
    payload["properties"] = _json_safe(properties)
    payload["target"] = {
        "instruction_names": _json_safe(_safe_attribute(backend, "operation_names")),
        "num_qubits": _json_safe(getattr(backend, "num_qubits", None)),
    }
    return payload


def summarize_runtime_job(job: Any) -> dict[str, Any]:
    """Return a compact runtime-job summary for execution provenance."""

    if job is None:
        return {}
    status = _safe_attribute(job, "status")
    creation_date = _safe_attribute(job, "creation_date")
    return {
        "job_id": _json_safe(_safe_attribute(job, "job_id")),
        "status": _json_safe(status),
        "creation_date": _json_safe(creation_date),
        "session_id": _json_safe(_safe_attribute(job, "session_id")),
        "primitive_id": _json_safe(_safe_attribute(job, "primitive_id")),
        "usage_estimation": _json_safe(_safe_attribute(job, "usage_estimation")),
    }


def capture_runtime_job_payload(job: Any) -> dict[str, Any]:
    """Return a fuller runtime-job payload for raw metadata capture."""

    if job is None:
        return {}
    payload = summarize_runtime_job(job)
    payload.update(
        {
            "usage": _json_safe(_safe_attribute(job, "usage")),
            "metrics": _json_safe(_safe_attribute(job, "metrics")),
            "inputs": _json_safe(_safe_attribute(job, "inputs")),
            "tags": _json_safe(_safe_attribute(job, "tags")),
            "instance": _json_safe(_safe_attribute(job, "instance")),
            "backend": _json_safe(_safe_attribute(job, "backend")),
            "error_message": _json_safe(_safe_attribute(job, "error_message")),
        }
    )
    return payload


def ibm_hardware_metadata_bundle_from_result(
    result: EstimatorExecutionResult,
) -> dict[str, Any]:
    """Construct a raw hardware-metadata bundle from an execution result."""

    provenance_metadata = (
        {} if result.provenance.metadata is None else dict(result.provenance.metadata)
    )
    return {
        "request": {
            "tier": result.request.tier.value,
            "backend_name": result.request.backend_name,
            "shots": result.request.shots,
            "seed": result.request.seed,
            "precision": result.request.precision,
            "optimization_level": result.request.optimization_level,
            "options": _json_safe(result.request.options),
        },
        "provenance": {
            "tier": result.provenance.tier.value,
            "backend_name": result.provenance.backend_name,
            "primitive_name": result.provenance.primitive_name,
            "job_id": result.provenance.job_id,
            "timestamp_utc": result.provenance.timestamp_utc,
        },
        "service": _json_safe(provenance_metadata.get("service", {})),
        "backend_selection": _json_safe(
            provenance_metadata.get("backend_selection", {})
        ),
        "mitigation_policy": _json_safe(
            provenance_metadata.get("mitigation_policy", {})
        ),
        "backend_summary": _json_safe(
            provenance_metadata.get("backend_summary", {})
        ),
        "backend_calibration": capture_backend_calibration(result.raw_backend),
        "runtime_job_summary": _json_safe(
            provenance_metadata.get("runtime_job_summary", {})
        ),
        "runtime_job_payload": capture_runtime_job_payload(result.raw_job),
        "primitive_result_metadata": _json_safe(result.job_metadata),
    }


def write_ibm_hardware_metadata_json(
    result: EstimatorExecutionResult,
    path: str | Path,
) -> Path:
    """Write the raw IBM hardware metadata bundle to disk as formatted JSON."""

    resolved_path = Path(path).expanduser().resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(
        json.dumps(
            ibm_hardware_metadata_bundle_from_result(result),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return resolved_path


def _write_json_payload(
    payload: Any,
    path: str | Path,
    *,
    overwrite: bool = True,
) -> Path:
    """Write a JSON payload to disk as formatted UTF-8 text."""

    resolved_path = Path(path).expanduser().resolve()
    if resolved_path.exists() and not overwrite:
        raise FileExistsError(
            f"Refusing to overwrite existing IBM archive artifact: {resolved_path}"
        )
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return resolved_path


def _write_text_payload(
    text: str,
    path: str | Path,
    *,
    overwrite: bool = True,
) -> Path:
    """Write a text payload to disk as UTF-8."""

    resolved_path = Path(path).expanduser().resolve()
    if resolved_path.exists() and not overwrite:
        raise FileExistsError(
            f"Refusing to overwrite existing IBM archive artifact: {resolved_path}"
        )
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(text, encoding="utf-8")
    return resolved_path


def _safe_filename_component(value: str | None, *, fallback: str) -> str:
    """Sanitize a value for use in an archive filename component."""

    if value is None:
        return fallback
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    sanitized = sanitized.strip("._-")
    return sanitized or fallback


def _archive_timestamp_label(timestamp_utc: str | None) -> str:
    """Normalize a provenance timestamp into a compact UTC filename label."""

    if timestamp_utc:
        try:
            parsed = datetime.fromisoformat(timestamp_utc)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        except ValueError:
            sanitized = re.sub(r"[^0-9TZ]", "", timestamp_utc.upper())
            if sanitized:
                return sanitized
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _archive_path_for_canonical(canonical_path: str | Path, archive_key: str) -> Path:
    """Return the timestamped archive path paired with a canonical artifact."""

    resolved = Path(canonical_path).expanduser().resolve()
    return resolved.with_name(f"{resolved.stem}_{archive_key}{resolved.suffix}")


def _local_testing_path_for_canonical(canonical_path: str | Path) -> Path:
    """Return the local-testing variant of a canonical IBM artifact path."""

    resolved = Path(canonical_path).expanduser().resolve()
    return resolved.with_name(f"{resolved.stem}_local_testing{resolved.suffix}")


def _append_jsonl_record(
    payload: Mapping[str, Any],
    path: str | Path,
) -> Path:
    """Append a JSON-safe record to a JSON Lines manifest."""

    resolved_path = Path(path).expanduser().resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    with resolved_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_json_safe(dict(payload)), sort_keys=True) + "\n")
    return resolved_path


def resolve_ibm_runtime_artifact_paths(
    *,
    execution_json_path: str | Path,
    comparison_json_path: str | Path,
    metadata_json_path: str | Path,
    report_markdown_path: str | Path,
    local_testing_mode: bool = False,
) -> dict[str, Path]:
    """Resolve canonical IBM artifact paths, optionally to local-testing variants."""

    canonical_paths = {
        "execution_json_path": Path(execution_json_path).expanduser().resolve(),
        "comparison_json_path": Path(comparison_json_path).expanduser().resolve(),
        "metadata_json_path": Path(metadata_json_path).expanduser().resolve(),
        "report_markdown_path": Path(report_markdown_path).expanduser().resolve(),
    }
    if not local_testing_mode:
        return canonical_paths
    return {
        name: _local_testing_path_for_canonical(path)
        for name, path in canonical_paths.items()
    }


def write_ibm_runtime_artifacts(
    *,
    experiment_name: str,
    scientific_question: str,
    result: EstimatorExecutionResult,
    comparison_records: Sequence[ComparisonRecord],
    benchmark_complete: bool,
    exact_local_complete: bool,
    noisy_local_complete: bool,
    execution_json_path: str | Path,
    comparison_json_path: str | Path,
    metadata_json_path: str | Path,
    report_markdown_path: str | Path,
    archive_live_runs: bool = True,
    archive_local_testing_mode: bool = False,
    runs_manifest_path: str | Path | None = None,
) -> dict[str, Path]:
    """Write canonical IBM artifacts and archive completed live hardware runs.

    The canonical paths remain the repository's "latest result" interface.
    For completed live IBM hardware runs, this helper also writes immutable
    timestamped archive copies and appends a JSON Lines manifest entry.
    """

    from qclab.analysis import comparison_records_to_serializable
    from qclab.backends.execution import execution_result_to_serializable

    execution_payload = execution_result_to_serializable(result)
    comparison_payload = comparison_records_to_serializable(comparison_records)
    metadata_payload = ibm_hardware_metadata_bundle_from_result(result)
    report_text = hardware_report_markdown(
        experiment_name=experiment_name,
        scientific_question=scientific_question,
        result=result,
        comparison_records=comparison_records,
        benchmark_complete=benchmark_complete,
        exact_local_complete=exact_local_complete,
        noisy_local_complete=noisy_local_complete,
        metadata_json_path=metadata_json_path,
    )

    execution_path = _write_json_payload(execution_payload, execution_json_path)
    comparison_path = _write_json_payload(comparison_payload, comparison_json_path)
    metadata_path = _write_json_payload(metadata_payload, metadata_json_path)
    report_path = _write_text_payload(report_text, report_markdown_path)

    outputs: dict[str, Path] = {
        "ibm_runtime_json": execution_path,
        "ibm_runtime_comparisons_json": comparison_path,
        "ibm_runtime_metadata_json": metadata_path,
        "ibm_runtime_report_markdown": report_path,
    }

    provenance_metadata = (
        {} if result.provenance.metadata is None else dict(result.provenance.metadata)
    )
    service_metadata = dict(provenance_metadata.get("service", {}))
    local_testing_mode = bool(service_metadata.get("local_testing_mode", False))
    archive_enabled = archive_live_runs and (
        archive_local_testing_mode or not local_testing_mode
    )
    if not archive_enabled:
        return outputs

    archive_key = "_".join(
        [
            _archive_timestamp_label(result.provenance.timestamp_utc),
            _safe_filename_component(result.provenance.backend_name, fallback="backend"),
            _safe_filename_component(result.provenance.job_id, fallback="no_job_id"),
        ]
    )
    archive_paths = {
        "ibm_runtime_archive_json": _archive_path_for_canonical(
            execution_path, archive_key
        ),
        "ibm_runtime_archive_comparisons_json": _archive_path_for_canonical(
            comparison_path, archive_key
        ),
        "ibm_runtime_archive_metadata_json": _archive_path_for_canonical(
            metadata_path, archive_key
        ),
        "ibm_runtime_archive_report_markdown": _archive_path_for_canonical(
            report_path, archive_key
        ),
    }
    archive_report_text = hardware_report_markdown(
        experiment_name=experiment_name,
        scientific_question=scientific_question,
        result=result,
        comparison_records=comparison_records,
        benchmark_complete=benchmark_complete,
        exact_local_complete=exact_local_complete,
        noisy_local_complete=noisy_local_complete,
        metadata_json_path=archive_paths["ibm_runtime_archive_metadata_json"],
    )
    outputs["ibm_runtime_archive_json"] = _write_json_payload(
        execution_payload,
        archive_paths["ibm_runtime_archive_json"],
        overwrite=False,
    )
    outputs["ibm_runtime_archive_comparisons_json"] = _write_json_payload(
        comparison_payload,
        archive_paths["ibm_runtime_archive_comparisons_json"],
        overwrite=False,
    )
    outputs["ibm_runtime_archive_metadata_json"] = _write_json_payload(
        metadata_payload,
        archive_paths["ibm_runtime_archive_metadata_json"],
        overwrite=False,
    )
    outputs["ibm_runtime_archive_report_markdown"] = _write_text_payload(
        archive_report_text,
        archive_paths["ibm_runtime_archive_report_markdown"],
        overwrite=False,
    )

    resolved_manifest_path = (
        Path(runs_manifest_path).expanduser().resolve()
        if runs_manifest_path is not None
        else metadata_path.parent / "ibm_runtime_runs.jsonl"
    )
    manifest_entry = {
        "experiment_name": experiment_name,
        "scientific_question": scientific_question,
        "timestamp_utc": result.provenance.timestamp_utc,
        "archive_timestamp_label": _archive_timestamp_label(result.provenance.timestamp_utc),
        "backend_name": result.provenance.backend_name,
        "job_id": result.provenance.job_id,
        "local_testing_mode": local_testing_mode,
        "service": service_metadata,
        "backend_selection": provenance_metadata.get("backend_selection", {}),
        "mitigation_policy": provenance_metadata.get("mitigation_policy", {}),
        "canonical_artifacts": {
            "execution_json": repository_relative_path(execution_path),
            "comparison_json": repository_relative_path(comparison_path),
            "metadata_json": repository_relative_path(metadata_path),
            "report_markdown": repository_relative_path(report_path),
        },
        "archived_artifacts": {
            "execution_json": repository_relative_path(outputs["ibm_runtime_archive_json"]),
            "comparison_json": repository_relative_path(
                outputs["ibm_runtime_archive_comparisons_json"]
            ),
            "metadata_json": repository_relative_path(
                outputs["ibm_runtime_archive_metadata_json"]
            ),
            "report_markdown": repository_relative_path(
                outputs["ibm_runtime_archive_report_markdown"]
            ),
        },
    }
    outputs["ibm_runtime_runs_manifest_jsonl"] = _append_jsonl_record(
        manifest_entry,
        resolved_manifest_path,
    )
    return outputs


def _format_float(value: float | None) -> str:
    """Format a scalar value for the hardware report."""

    if value is None:
        return "n/a"
    return f"{value:.6f}"


def hardware_report_markdown(
    *,
    experiment_name: str,
    scientific_question: str,
    result: EstimatorExecutionResult,
    comparison_records: Sequence[ComparisonRecord],
    benchmark_complete: bool,
    exact_local_complete: bool,
    noisy_local_complete: bool,
    metadata_json_path: str | Path | None = None,
) -> str:
    """Render a hardware report in repository-standard Markdown form."""

    provenance_metadata = (
        {} if result.provenance.metadata is None else dict(result.provenance.metadata)
    )
    service_metadata = dict(provenance_metadata.get("service", {}))
    selection_metadata = dict(provenance_metadata.get("backend_selection", {}))
    mitigation_metadata = dict(provenance_metadata.get("mitigation_policy", {}))
    backend_summary = dict(provenance_metadata.get("backend_summary", {}))
    job_summary = dict(provenance_metadata.get("runtime_job_summary", {}))
    evaluation_by_name = {
        evaluation.observable.name: evaluation for evaluation in result.evaluations
    }
    lines = [
        "# IBM Runtime Hardware Report",
        "",
        "## Purpose",
        "",
        (
            "This report records the operational context of an IBM Runtime "
            "execution tier. It does not establish scientific meaning in "
            "isolation from the benchmark, exact-local, and noisy-local tiers."
        ),
        "",
        "## Experiment Context",
        "",
        f"- Experiment: `{experiment_name}`",
        f"- Scientific question: {scientific_question.strip()}",
        f"- Execution tier: `{result.provenance.tier.value}`",
        f"- Primitive: `{result.provenance.primitive_name}`",
        f"- Report timestamp (UTC): `{result.provenance.timestamp_utc}`",
        "",
        "## Validation Gate",
        "",
        f"- Benchmark available: `{benchmark_complete}`",
        f"- Exact local validation available: `{exact_local_complete}`",
        f"- Noisy local validation available: `{noisy_local_complete}`",
        "",
        "## Backend Selection",
        "",
        f"- Strategy: `{selection_metadata.get('strategy', 'unspecified')}`",
        f"- Requested backend: `{selection_metadata.get('requested_backend_name', result.request.backend_name)}`",
        f"- Selected backend: `{selection_metadata.get('selected_backend_name', result.provenance.backend_name)}`",
        f"- Service channel: `{service_metadata.get('channel')}`",
        f"- Service instance: `{service_metadata.get('instance')}`",
        f"- Local testing mode: `{service_metadata.get('local_testing_mode', False)}`",
        "",
        "## Mitigation Policy",
        "",
        f"- Resilience level: `{mitigation_metadata.get('resilience_level', 'unspecified')}`",
        f"- Measurement mitigation: `{mitigation_metadata.get('measure_mitigation')}`",
        f"- Gate twirling: `{mitigation_metadata.get('twirling_enable_gates')}`",
        f"- Measurement twirling: `{mitigation_metadata.get('twirling_enable_measure')}`",
        f"- Dynamical decoupling: `{mitigation_metadata.get('dynamical_decoupling_enable')}`",
        f"- Requested precision: `{result.request.precision}`",
        f"- Requested shots: `{result.request.shots}`",
        f"- Optimization level: `{result.request.optimization_level}`",
        "",
        "## Backend and Calibration Summary",
        "",
        f"- Backend class: `{backend_summary.get('backend_class')}`",
        f"- Backend qubits: `{backend_summary.get('num_qubits')}`",
        f"- Calibration id: `{backend_summary.get('calibration_id')}`",
        f"- Properties last update: `{backend_summary.get('properties_last_update_date')}`",
        f"- Pending jobs at capture: `{backend_summary.get('status', {}).get('pending_jobs') if isinstance(backend_summary.get('status'), Mapping) else None}`",
        f"- Backend operational: `{backend_summary.get('status', {}).get('operational') if isinstance(backend_summary.get('status'), Mapping) else None}`",
        "",
        "## Runtime Job Summary",
        "",
        f"- Job id: `{job_summary.get('job_id', result.provenance.job_id)}`",
        f"- Job status: `{job_summary.get('status')}`",
        f"- Job creation date: `{job_summary.get('creation_date')}`",
        f"- Session id: `{job_summary.get('session_id')}`",
        f"- Usage estimation: `{job_summary.get('usage_estimation')}`",
        "",
        "## Observable Comparison",
        "",
        "| Observable | Benchmark | Hardware | Abs. error | Rel. error | Uncertainty |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for record in comparison_records:
        evaluation = evaluation_by_name.get(record.observable_name)
        uncertainty = None if evaluation is None else evaluation.uncertainty
        lines.append(
            "| "
            + f"{record.observable_name} | "
            + f"{_format_float(record.benchmark_value)} | "
            + f"{_format_float(record.candidate_value)} | "
            + f"{_format_float(record.absolute_error)} | "
            + f"{_format_float(record.relative_error)} | "
            + f"{_format_float(uncertainty)} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Constraint",
            "",
            (
                "Hardware output must be read only as a benchmarked execution "
                "tier for the declared observables. It does not by itself "
                "justify cosmological or field-theoretic interpretation."
            ),
        ]
    )
    if metadata_json_path is not None:
        lines.extend(
            [
                "",
                "## Metadata Artifact",
                "",
                (
                    "- Raw hardware metadata JSON: "
                    f"`{repository_relative_path(Path(metadata_json_path).expanduser().resolve())}`"
                ),
            ]
        )
    if service_metadata.get("local_testing_mode"):
        lines.extend(
            [
                "",
                "## Local Testing Note",
                "",
                (
                    "This execution used IBM Runtime local testing mode through "
                    "a fake backend or local simulator pathway. It validates the "
                    "repository hardware wrapper and provenance path, but it is "
                    "not a real QPU result."
                ),
            ]
        )
    lines.append("")
    return "\n".join(lines)


def write_hardware_report_markdown(
    *,
    experiment_name: str,
    scientific_question: str,
    result: EstimatorExecutionResult,
    comparison_records: Sequence[ComparisonRecord],
    benchmark_complete: bool,
    exact_local_complete: bool,
    noisy_local_complete: bool,
    path: str | Path,
    metadata_json_path: str | Path | None = None,
) -> Path:
    """Write a repository-standard IBM Runtime hardware report to disk."""

    resolved_path = Path(path).expanduser().resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(
        hardware_report_markdown(
            experiment_name=experiment_name,
            scientific_question=scientific_question,
            result=result,
            comparison_records=comparison_records,
            benchmark_complete=benchmark_complete,
            exact_local_complete=exact_local_complete,
            noisy_local_complete=noisy_local_complete,
            metadata_json_path=metadata_json_path,
        ),
        encoding="utf-8",
    )
    return resolved_path
