"""Typed records for validation policies, assessments, and hardware gates."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any


@dataclass(frozen=True)
class ValidationContext:
    """Deterministic scientific lineage attached to generated artifacts."""

    experiment_name: str
    configuration_fingerprint: str
    model_fingerprint: str
    observable_fingerprint: str
    benchmark_fingerprint: str
    lineage_id: str
    schema_version: int = 1

    def to_serializable(self) -> dict[str, Any]:
        """Return a JSON-safe mapping."""

        return {
            "schema_version": self.schema_version,
            "experiment_name": self.experiment_name,
            "configuration_fingerprint": self.configuration_fingerprint,
            "model_fingerprint": self.model_fingerprint,
            "observable_fingerprint": self.observable_fingerprint,
            "benchmark_fingerprint": self.benchmark_fingerprint,
            "lineage_id": self.lineage_id,
        }

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any]) -> "ValidationContext":
        """Create and validate a context from serialized content."""

        try:
            context = cls(
                schema_version=int(mapping["schema_version"]),
                experiment_name=str(mapping["experiment_name"]),
                configuration_fingerprint=str(mapping["configuration_fingerprint"]),
                model_fingerprint=str(mapping["model_fingerprint"]),
                observable_fingerprint=str(mapping["observable_fingerprint"]),
                benchmark_fingerprint=str(mapping["benchmark_fingerprint"]),
                lineage_id=str(mapping["lineage_id"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Invalid validation_context payload.") from exc
        if context.schema_version != 1:
            raise ValueError(
                f"Unsupported validation context schema version: {context.schema_version}."
            )
        if not context.experiment_name.strip():
            raise ValueError("Validation context experiment_name must be non-empty.")
        for name, digest in (
            ("configuration_fingerprint", context.configuration_fingerprint),
            ("model_fingerprint", context.model_fingerprint),
            ("observable_fingerprint", context.observable_fingerprint),
            ("benchmark_fingerprint", context.benchmark_fingerprint),
            ("lineage_id", context.lineage_id),
        ):
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError(f"Validation context {name} is not a SHA-256 digest.")
        return context


@dataclass(frozen=True)
class ObservableTolerancePolicy:
    """Acceptance policy for one scalar observable."""

    absolute_tolerance: float
    relative_tolerance: float = 0.0
    lower_bound: float | None = None
    upper_bound: float | None = None
    required_sign: str | None = None

    def __post_init__(self) -> None:
        if (
            not math.isfinite(self.absolute_tolerance)
            or not math.isfinite(self.relative_tolerance)
            or self.absolute_tolerance < 0
            or self.relative_tolerance < 0
        ):
            raise ValueError("Validation tolerances must be finite and non-negative.")
        if self.lower_bound is not None and not math.isfinite(self.lower_bound):
            raise ValueError("Validation lower_bound must be finite when set.")
        if self.upper_bound is not None and not math.isfinite(self.upper_bound):
            raise ValueError("Validation upper_bound must be finite when set.")
        if (
            self.lower_bound is not None
            and self.upper_bound is not None
            and self.lower_bound > self.upper_bound
        ):
            raise ValueError("Validation lower_bound cannot exceed upper_bound.")
        if self.required_sign not in {
            None,
            "positive",
            "negative",
            "nonnegative",
            "nonpositive",
        }:
            raise ValueError("required_sign must be a supported sign constraint.")

    def to_serializable(self) -> dict[str, Any]:
        """Return a JSON-safe mapping."""

        return {
            "absolute_tolerance": self.absolute_tolerance,
            "relative_tolerance": self.relative_tolerance,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "required_sign": self.required_sign,
        }


@dataclass(frozen=True)
class TierValidationPolicy:
    """Acceptance policies for all observables in an execution tier."""

    tier: str
    default: ObservableTolerancePolicy | None = None
    observables: dict[str, ObservableTolerancePolicy] = field(default_factory=dict)
    maximum_standardized_residual: float | None = None

    def __post_init__(self) -> None:
        if self.maximum_standardized_residual is not None and (
            not math.isfinite(self.maximum_standardized_residual)
            or self.maximum_standardized_residual < 0
        ):
            raise ValueError(
                "maximum_standardized_residual must be finite and non-negative."
            )

    def policy_for(self, observable_name: str) -> ObservableTolerancePolicy:
        """Return the specific or default policy for an observable."""

        policy = self.observables.get(observable_name, self.default)
        if policy is None:
            raise KeyError(
                f"No validation policy is configured for observable {observable_name!r} "
                f"in tier {self.tier!r}."
            )
        return policy


@dataclass(frozen=True)
class ObservableAssessment:
    """Deterministic acceptance assessment for one observable value."""

    observable_name: str
    benchmark_value: float
    candidate_value: float
    uncertainty: float
    absolute_error: float
    allowed_error: float
    standardized_residual: float | None
    checks: dict[str, bool]
    passed: bool
    reasons: tuple[str, ...] = ()

    def to_serializable(self) -> dict[str, Any]:
        """Return a JSON-safe mapping."""

        return {
            "observable_name": self.observable_name,
            "benchmark_value": self.benchmark_value,
            "candidate_value": self.candidate_value,
            "uncertainty": self.uncertainty,
            "absolute_error": self.absolute_error,
            "allowed_error": self.allowed_error,
            "standardized_residual": self.standardized_residual,
            "checks": dict(self.checks),
            "passed": self.passed,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class TierAssessment:
    """Aggregate validation result for one execution tier."""

    tier: str
    lineage_id: str
    passed: bool
    observables: tuple[ObservableAssessment, ...]
    errors: tuple[str, ...] = ()
    schema_version: int = 1

    def to_serializable(self) -> dict[str, Any]:
        """Return a JSON-safe mapping."""

        return {
            "schema_version": self.schema_version,
            "tier": self.tier,
            "lineage_id": self.lineage_id,
            "passed": self.passed,
            "observables": [item.to_serializable() for item in self.observables],
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class HardwarePreflightResult:
    """Successful content-based validation of hardware prerequisites."""

    experiment_name: str
    lineage_id: str
    exact_local_assessment: TierAssessment
    noisy_local_assessment: TierAssessment
    additional_assessments: tuple[TierAssessment, ...] = ()

    @property
    def passed(self) -> bool:
        """Return whether every required validation assessment passed."""

        return (
            self.exact_local_assessment.passed
            and self.noisy_local_assessment.passed
            and all(assessment.passed for assessment in self.additional_assessments)
        )

    def assessment_for(self, tier: str) -> TierAssessment:
        """Return one named assessment from the preflight record."""

        assessments = (
            self.exact_local_assessment,
            self.noisy_local_assessment,
            *self.additional_assessments,
        )
        for assessment in assessments:
            if assessment.tier == tier:
                return assessment
        raise KeyError(f"No preflight assessment exists for tier {tier!r}.")


class HardwareValidationGateError(RuntimeError):
    """Raised when local evidence is stale, incomplete, or outside policy."""
