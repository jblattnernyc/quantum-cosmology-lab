"""Core package for the Quantum Cosmology Lab.

The package currently provides repository-wide scientific infrastructure for
configuration loading, model and observable specifications, benchmark
interfaces, backend execution policy, and analysis helpers. Official
experiment implementations remain separate under ``experiments/`` and must be
benchmarked and documented before scientific interpretation.
"""

from qclab.analysis.comparison import (
    ComparisonRecord,
    compare_scalar_observable,
    comparison_within_tolerance,
)
from qclab.analysis.reporting import execution_result_to_rows
from qclab.backends.base import (
    BackendAvailability,
    BackendRequest,
    ExecutionTier,
    detect_backend_availability,
    validate_execution_progression,
)
from qclab.backends.execution import (
    AerEstimatorExecutor,
    EstimatorExecutionResult,
    ExactLocalEstimatorExecutor,
    ExecutionProvenance,
    IBMRuntimeEstimatorExecutor,
    execution_result_to_serializable,
    write_execution_result_json,
)
from qclab.backends.hardware import (
    BackendSelectionPolicy,
    BackendSelectionStrategy,
    MitigationPolicy,
    hardware_report_markdown,
    ibm_hardware_metadata_bundle_from_result,
    instantiate_local_testing_backend,
    write_hardware_report_markdown,
    write_ibm_hardware_metadata_json,
)
from qclab.benchmarks.base import BenchmarkResult
from qclab.benchmarks.scalar import CallableScalarBenchmark
from qclab.circuits.base import CircuitArtifact
from qclab.encodings.base import EncodingSpecification
from qclab.models.specifications import ModelSpecification, TruncationSpecification
from qclab.observables.base import (
    ObservableDefinition,
    ObservableEvaluation,
    PauliTerm,
)
from qclab.observables.pauli import make_pauli_observable
from qclab.utils.configuration import (
    ExecutionConfiguration,
    ModelConfiguration,
    load_model_configuration,
    validate_model_configuration,
)
from qclab.utils.foundation import FoundationPipelineResult, run_foundation_smoke_example

__all__ = [
    "AerEstimatorExecutor",
    "BackendAvailability",
    "BackendRequest",
    "BackendSelectionPolicy",
    "BackendSelectionStrategy",
    "BenchmarkResult",
    "CallableScalarBenchmark",
    "CircuitArtifact",
    "ComparisonRecord",
    "EncodingSpecification",
    "EstimatorExecutionResult",
    "ExecutionConfiguration",
    "ExecutionTier",
    "ExecutionProvenance",
    "ExactLocalEstimatorExecutor",
    "FoundationPipelineResult",
    "IBMRuntimeEstimatorExecutor",
    "MitigationPolicy",
    "ModelConfiguration",
    "ModelSpecification",
    "ObservableDefinition",
    "ObservableEvaluation",
    "PauliTerm",
    "TruncationSpecification",
    "compare_scalar_observable",
    "comparison_within_tolerance",
    "detect_backend_availability",
    "execution_result_to_serializable",
    "execution_result_to_rows",
    "hardware_report_markdown",
    "ibm_hardware_metadata_bundle_from_result",
    "instantiate_local_testing_backend",
    "load_model_configuration",
    "make_pauli_observable",
    "run_foundation_smoke_example",
    "validate_model_configuration",
    "validate_execution_progression",
    "write_hardware_report_markdown",
    "write_ibm_hardware_metadata_json",
    "write_execution_result_json",
]

__version__ = "1.0.0"
