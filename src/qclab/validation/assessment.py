"""Policy parsing and deterministic observable assessments."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
from typing import Any

from qclab.observables import ObservableDefinition, ObservableEvaluation
from qclab.utils.configuration import ModelConfiguration
from qclab.validation.fingerprints import (
    benchmark_fingerprint,
    configuration_fingerprint,
    lineage_fingerprint,
    model_fingerprint,
    observable_fingerprint,
)
from qclab.validation.records import (
    ObservableAssessment,
    ObservableTolerancePolicy,
    TierAssessment,
    TierValidationPolicy,
    ValidationContext,
)


def build_validation_context(
    configuration: ModelConfiguration,
    benchmark_payload: Mapping[str, Any],
    observables: Sequence[ObservableDefinition],
) -> ValidationContext:
    """Build the validation lineage for the current configured experiment."""

    configuration_digest = configuration_fingerprint(configuration)
    model_digest = model_fingerprint(configuration)
    observable_digest = observable_fingerprint(observables)
    benchmark_digest = benchmark_fingerprint(benchmark_payload)
    return ValidationContext(
        experiment_name=configuration.experiment_name,
        configuration_fingerprint=configuration_digest,
        model_fingerprint=model_digest,
        observable_fingerprint=observable_digest,
        benchmark_fingerprint=benchmark_digest,
        lineage_id=lineage_fingerprint(
            configuration_digest=configuration_digest,
            model_digest=model_digest,
            observable_digest=observable_digest,
            benchmark_digest=benchmark_digest,
        ),
    )


def _tolerance_policy_from_mapping(
    mapping: Mapping[str, Any],
) -> ObservableTolerancePolicy:
    """Normalize one observable acceptance policy."""

    bounds = mapping.get("bounds")
    lower_bound = mapping.get("lower_bound")
    upper_bound = mapping.get("upper_bound")
    if bounds is not None:
        if (
            not isinstance(bounds, Sequence)
            or isinstance(bounds, (str, bytes))
            or len(bounds) != 2
        ):
            raise ValueError("Validation bounds must contain [lower, upper].")
        lower_bound, upper_bound = bounds
    return ObservableTolerancePolicy(
        absolute_tolerance=float(mapping.get("absolute_tolerance", 0.0)),
        relative_tolerance=float(mapping.get("relative_tolerance", 0.0)),
        lower_bound=None if lower_bound is None else float(lower_bound),
        upper_bound=None if upper_bound is None else float(upper_bound),
        required_sign=(
            None
            if mapping.get("required_sign") is None
            else str(mapping.get("required_sign"))
        ),
    )


def parse_tier_validation_policy(
    validation_configuration: Mapping[str, Any],
    tier: str,
) -> TierValidationPolicy:
    """Parse one tier from the shared validation configuration schema."""

    schema_version = int(validation_configuration.get("schema_version", 1))
    if schema_version != 1:
        raise ValueError(
            f"Unsupported validation policy schema version: {schema_version}."
        )
    raw_tiers = validation_configuration.get("tiers", validation_configuration)
    if not isinstance(raw_tiers, Mapping):
        raise TypeError("Validation tiers must be a mapping.")
    raw_policy = raw_tiers.get(tier)
    if not isinstance(raw_policy, Mapping):
        raise KeyError(f"No validation policy is configured for tier {tier!r}.")
    raw_default = raw_policy.get("default")
    if raw_default is not None and not isinstance(raw_default, Mapping):
        raise TypeError(f"Validation default for tier {tier!r} must be a mapping.")
    raw_observables = raw_policy.get("observables", {})
    if not isinstance(raw_observables, Mapping):
        raise TypeError(f"Validation observables for tier {tier!r} must be a mapping.")
    invalid_policy_names = [
        str(name)
        for name, observable_policy in raw_observables.items()
        if not isinstance(observable_policy, Mapping)
    ]
    if invalid_policy_names:
        raise TypeError(
            f"Validation policies for tier {tier!r} must be mappings: "
            + ", ".join(sorted(invalid_policy_names))
        )
    return TierValidationPolicy(
        tier=tier,
        default=(
            None if raw_default is None else _tolerance_policy_from_mapping(raw_default)
        ),
        observables={
            str(name): _tolerance_policy_from_mapping(policy)
            for name, policy in raw_observables.items()
        },
        maximum_standardized_residual=(
            None
            if raw_policy.get("maximum_standardized_residual") is None
            else float(raw_policy["maximum_standardized_residual"])
        ),
    )


def _evaluation_values(
    evaluation: ObservableEvaluation | Mapping[str, Any],
) -> tuple[str, float, float]:
    """Normalize an in-memory or serialized observable evaluation."""

    if isinstance(evaluation, ObservableEvaluation):
        return (
            evaluation.observable.name,
            float(evaluation.value),
            float(evaluation.uncertainty),
        )
    return (
        str(evaluation["observable_name"]),
        float(evaluation["value"]),
        float(evaluation.get("uncertainty", 0.0) or 0.0),
    )


def _sign_check(value: float, required_sign: str | None) -> bool:
    """Evaluate an optional sign constraint."""

    if required_sign is None:
        return True
    if required_sign == "positive":
        return value > 0.0
    if required_sign == "negative":
        return value < 0.0
    if required_sign == "nonnegative":
        return value >= 0.0
    return value <= 0.0


def assess_observable_values(
    *,
    tier: str,
    lineage_id: str,
    evaluations: Sequence[ObservableEvaluation | Mapping[str, Any]],
    benchmark_values: Mapping[str, float],
    validation_configuration: Mapping[str, Any],
) -> TierAssessment:
    """Assess scalar observable evaluations against declared benchmark policy."""

    policy = parse_tier_validation_policy(validation_configuration, tier)
    normalized: dict[str, tuple[float, float]] = {}
    errors: list[str] = []
    for evaluation in evaluations:
        name, value, uncertainty = _evaluation_values(evaluation)
        if name in normalized:
            errors.append(f"Duplicate evaluation for observable {name!r}.")
            continue
        normalized[name] = (value, uncertainty)

    expected_names = set(benchmark_values)
    received_names = set(normalized)
    for name in sorted(expected_names - received_names):
        errors.append(f"Missing evaluation for observable {name!r}.")
    for name in sorted(received_names - expected_names):
        errors.append(f"Unexpected evaluation for observable {name!r}.")

    assessments: list[ObservableAssessment] = []
    for name in sorted(expected_names & received_names):
        benchmark_value = float(benchmark_values[name])
        candidate_value, uncertainty = normalized[name]
        try:
            observable_policy = policy.policy_for(name)
        except KeyError as exc:
            errors.append(str(exc))
            continue

        absolute_error = abs(candidate_value - benchmark_value)
        allowed_error = (
            observable_policy.absolute_tolerance
            + observable_policy.relative_tolerance * abs(benchmark_value)
        )
        finite = all(
            math.isfinite(value)
            for value in (benchmark_value, candidate_value, uncertainty)
        )
        tolerance_check = finite and absolute_error <= allowed_error
        bounds_check = finite
        if observable_policy.lower_bound is not None:
            bounds_check = (
                bounds_check and candidate_value >= observable_policy.lower_bound
            )
        if observable_policy.upper_bound is not None:
            bounds_check = (
                bounds_check and candidate_value <= observable_policy.upper_bound
            )
        sign_check = finite and _sign_check(
            candidate_value, observable_policy.required_sign
        )

        standardized_residual: float | None = None
        uncertainty_check = uncertainty >= 0.0 and math.isfinite(uncertainty)
        standardized_residual_check = True
        if policy.maximum_standardized_residual is not None:
            if uncertainty <= 0.0 or not math.isfinite(uncertainty):
                standardized_residual_check = False
            else:
                standardized_residual = absolute_error / uncertainty
                standardized_residual_check = (
                    standardized_residual <= policy.maximum_standardized_residual
                )

        checks = {
            "finite": finite,
            "tolerance": tolerance_check,
            "bounds": bounds_check,
            "sign": sign_check,
            "uncertainty": uncertainty_check,
            "standardized_residual": standardized_residual_check,
        }
        reasons = tuple(
            reason
            for check_name, reason in (
                ("finite", "Benchmark, candidate, and uncertainty must be finite."),
                ("tolerance", "Absolute/relative tolerance was exceeded."),
                ("bounds", "The declared physical bounds were violated."),
                ("sign", "The declared sign constraint was violated."),
                ("uncertainty", "Uncertainty must be finite and non-negative."),
                (
                    "standardized_residual",
                    "The standardized residual limit was exceeded or uncertainty was zero.",
                ),
            )
            if not checks[check_name]
        )
        assessments.append(
            ObservableAssessment(
                observable_name=name,
                benchmark_value=benchmark_value,
                candidate_value=candidate_value,
                uncertainty=uncertainty,
                absolute_error=absolute_error,
                allowed_error=allowed_error,
                standardized_residual=standardized_residual,
                checks=checks,
                passed=all(checks.values()),
                reasons=reasons,
            )
        )

    passed = (
        not errors
        and len(assessments) == len(expected_names)
        and all(assessment.passed for assessment in assessments)
    )
    return TierAssessment(
        tier=tier,
        lineage_id=lineage_id,
        passed=passed,
        observables=tuple(assessments),
        errors=tuple(errors),
    )
