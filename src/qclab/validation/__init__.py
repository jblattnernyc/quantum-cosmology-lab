"""Validation lineage, acceptance assessments, and hardware progression gates."""

from qclab.validation.assessment import (
    assess_observable_values,
    build_validation_context,
    parse_tier_validation_policy,
)
from qclab.validation.fingerprints import (
    BENCHMARK_FLOAT_DECIMAL_PLACES,
    COMPUTED_EVIDENCE_ABSOLUTE_TOLERANCE,
    COMPUTED_EVIDENCE_RELATIVE_TOLERANCE,
    benchmark_fingerprint,
    canonical_json,
    canonicalize_computed_numbers,
    computed_payloads_equivalent,
    configuration_fingerprint,
    lineage_fingerprint,
    model_fingerprint,
    observable_fingerprint,
    sha256_fingerprint,
)
from qclab.validation.gate import validate_hardware_prerequisites
from qclab.validation.lineage import (
    ArtifactLineageClassification,
    ArtifactLineageStatus,
    classify_artifact_lineage,
)
from qclab.validation.records import (
    HardwarePreflightResult,
    HardwareValidationGateError,
    ObservableAssessment,
    ObservableTolerancePolicy,
    TierAssessment,
    TierValidationPolicy,
    ValidationContext,
)

__all__ = [
    "HardwarePreflightResult",
    "HardwareValidationGateError",
    "ArtifactLineageClassification",
    "ArtifactLineageStatus",
    "ObservableAssessment",
    "ObservableTolerancePolicy",
    "TierAssessment",
    "TierValidationPolicy",
    "ValidationContext",
    "BENCHMARK_FLOAT_DECIMAL_PLACES",
    "COMPUTED_EVIDENCE_ABSOLUTE_TOLERANCE",
    "COMPUTED_EVIDENCE_RELATIVE_TOLERANCE",
    "assess_observable_values",
    "benchmark_fingerprint",
    "build_validation_context",
    "canonical_json",
    "canonicalize_computed_numbers",
    "classify_artifact_lineage",
    "computed_payloads_equivalent",
    "configuration_fingerprint",
    "lineage_fingerprint",
    "model_fingerprint",
    "observable_fingerprint",
    "parse_tier_validation_policy",
    "sha256_fingerprint",
    "validate_hardware_prerequisites",
]
