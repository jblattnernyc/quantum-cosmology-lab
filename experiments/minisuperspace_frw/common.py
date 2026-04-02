"""Shared utilities for the reduced FRW minisuperspace experiment."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any

import numpy as np

from qclab.backends.base import ExecutionTier
from qclab.utils.configuration import ModelConfiguration, load_model_configuration


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")


@dataclass(frozen=True)
class MinisuperspaceFRWParameters:
    """Effective two-state parameters for the reduced FRW toy model."""

    scale_factor_small: float
    scale_factor_large: float
    diagonal_bias: float
    tunneling_strength: float

    def __post_init__(self) -> None:
        if self.scale_factor_small <= 0:
            raise ValueError("scale_factor_small must be strictly positive.")
        if self.scale_factor_large <= self.scale_factor_small:
            raise ValueError(
                "scale_factor_large must be greater than scale_factor_small."
            )
        if self.tunneling_strength <= 0:
            raise ValueError("tunneling_strength must be strictly positive.")

    @property
    def scale_factor_mean(self) -> float:
        return 0.5 * (self.scale_factor_small + self.scale_factor_large)

    @property
    def scale_factor_z_coefficient(self) -> float:
        return 0.5 * (self.scale_factor_small - self.scale_factor_large)

    @property
    def volume_small(self) -> float:
        return self.scale_factor_small**3

    @property
    def volume_large(self) -> float:
        return self.scale_factor_large**3


@dataclass(frozen=True)
class NoiseModelSpecification:
    """Serializable Aer noise-model settings for the experiment."""

    one_qubit_depolarizing_probability: float
    readout_error_probability: float
    method: str = "density_matrix"

    def __post_init__(self) -> None:
        for name, value in (
            ("one_qubit_depolarizing_probability", self.one_qubit_depolarizing_probability),
            ("readout_error_probability", self.readout_error_probability),
        ):
            if not 0 <= value < 1:
                raise ValueError(f"{name} must lie in [0, 1).")


@dataclass(frozen=True)
class MinisuperspaceArtifactPaths:
    """Artifact locations for experiment outputs."""

    benchmark_json: Path
    exact_local_json: Path
    exact_local_comparisons_json: Path
    noisy_local_json: Path
    noisy_local_comparisons_json: Path
    ibm_runtime_json: Path
    ibm_runtime_comparisons_json: Path
    ibm_runtime_metadata_json: Path
    ibm_runtime_report_markdown: Path
    analysis_summary_json: Path
    analysis_report_markdown: Path
    observable_summary_table_markdown: Path
    comparison_figure: Path


@dataclass(frozen=True)
class MinisuperspaceFRWExperiment:
    """Fully resolved experiment definition loaded from configuration."""

    configuration: ModelConfiguration
    parameters: MinisuperspaceFRWParameters
    noise_model: NoiseModelSpecification
    artifacts: MinisuperspaceArtifactPaths


def _resolve_artifact_path(raw_path: str | Path) -> Path:
    """Resolve artifact paths relative to the repository root."""

    candidate = Path(raw_path).expanduser()
    if candidate.is_absolute():
        return candidate
    return (REPO_ROOT / candidate).resolve()


def _required_float(mapping: dict[str, Any], key: str) -> float:
    """Extract a required float-valued parameter."""

    if key not in mapping:
        raise KeyError(f"Missing required experiment parameter: {key}")
    return float(mapping[key])


def _artifact_paths_from_metadata(metadata: dict[str, Any]) -> MinisuperspaceArtifactPaths:
    """Build artifact paths from configuration metadata."""

    raw_paths = dict(metadata.get("artifacts", {}))
    defaults = {
        "benchmark_json": "data/processed/minisuperspace_frw/benchmark.json",
        "exact_local_json": "data/processed/minisuperspace_frw/exact_local.json",
        "exact_local_comparisons_json": (
            "data/processed/minisuperspace_frw/exact_local_comparisons.json"
        ),
        "noisy_local_json": "data/processed/minisuperspace_frw/noisy_local.json",
        "noisy_local_comparisons_json": (
            "data/processed/minisuperspace_frw/noisy_local_comparisons.json"
        ),
        "ibm_runtime_json": "data/processed/minisuperspace_frw/ibm_runtime.json",
        "ibm_runtime_comparisons_json": (
            "data/processed/minisuperspace_frw/ibm_runtime_comparisons.json"
        ),
        "ibm_runtime_metadata_json": "data/raw/minisuperspace_frw/ibm_runtime_metadata.json",
        "ibm_runtime_report_markdown": (
            "results/reports/minisuperspace_frw/ibm_runtime_report.md"
        ),
        "analysis_summary_json": "results/reports/minisuperspace_frw/analysis_summary.json",
        "analysis_report_markdown": (
            "results/reports/minisuperspace_frw/analysis_report.md"
        ),
        "observable_summary_table_markdown": (
            "results/tables/minisuperspace_frw/observable_summary.md"
        ),
        "comparison_figure": "results/figures/minisuperspace_frw/observable_comparison.png",
    }
    resolved = {
        key: _resolve_artifact_path(raw_paths.get(key, default))
        for key, default in defaults.items()
    }
    return MinisuperspaceArtifactPaths(**resolved)


def load_experiment_definition(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> MinisuperspaceFRWExperiment:
    """Load the experiment configuration and resolve typed parameters."""

    configuration = load_model_configuration(config_path)
    parameters = MinisuperspaceFRWParameters(
        scale_factor_small=_required_float(
            configuration.parameters, "scale_factor_small"
        ),
        scale_factor_large=_required_float(
            configuration.parameters, "scale_factor_large"
        ),
        diagonal_bias=_required_float(configuration.parameters, "diagonal_bias"),
        tunneling_strength=_required_float(
            configuration.parameters, "tunneling_strength"
        ),
    )
    noise_metadata = dict(configuration.metadata.get("noise_model", {}))
    noise_model = NoiseModelSpecification(
        one_qubit_depolarizing_probability=float(
            noise_metadata.get("one_qubit_depolarizing_probability", 0.004)
        ),
        readout_error_probability=float(
            noise_metadata.get("readout_error_probability", 0.02)
        ),
        method=str(noise_metadata.get("method", "density_matrix")),
    )
    artifacts = _artifact_paths_from_metadata(configuration.metadata)
    return MinisuperspaceFRWExperiment(
        configuration=configuration,
        parameters=parameters,
        noise_model=noise_model,
        artifacts=artifacts,
    )


def effective_hamiltonian_matrix(
    parameters: MinisuperspaceFRWParameters,
) -> np.ndarray:
    """Return the two-state effective Hamiltonian matrix.

    The reduced model uses a single-qubit truncation with

    H_eff = diagonal_bias * Z - tunneling_strength * X.
    """

    return np.array(
        [
            [parameters.diagonal_bias, -parameters.tunneling_strength],
            [-parameters.tunneling_strength, -parameters.diagonal_bias],
        ],
        dtype=float,
    )


def scale_factor_matrix(parameters: MinisuperspaceFRWParameters) -> np.ndarray:
    """Return the truncated scale-factor operator."""

    return np.diag([parameters.scale_factor_small, parameters.scale_factor_large]).astype(
        float
    )


def volume_matrix(parameters: MinisuperspaceFRWParameters) -> np.ndarray:
    """Return the truncated volume proxy operator."""

    return np.diag([parameters.volume_small, parameters.volume_large]).astype(float)


def large_scale_factor_projector(
    parameters: MinisuperspaceFRWParameters,
) -> np.ndarray:
    """Return the projector onto the larger scale-factor bin."""

    del parameters
    return np.diag([0.0, 1.0]).astype(float)


def canonicalize_real_statevector(statevector: np.ndarray) -> np.ndarray:
    """Fix the global phase of a real two-state vector for circuit preparation."""

    normalized = np.asarray(statevector, dtype=complex).reshape(2)
    pivot_index = int(np.argmax(np.abs(normalized)))
    pivot = normalized[pivot_index]
    if pivot == 0:
        raise ValueError("Statevector cannot be canonicalized from the zero vector.")
    normalized = normalized * np.exp(-1j * np.angle(pivot))
    if np.max(np.abs(normalized.imag)) < 1e-12:
        normalized = normalized.real
    if float(normalized[pivot_index].real) < 0:
        normalized = -normalized
    return np.asarray(normalized, dtype=float)


def ground_state_data(
    parameters: MinisuperspaceFRWParameters,
) -> tuple[float, np.ndarray]:
    """Return the benchmark ground-state energy and statevector."""

    eigenvalues, eigenvectors = np.linalg.eigh(effective_hamiltonian_matrix(parameters))
    ground_state = canonicalize_real_statevector(eigenvectors[:, 0])
    return float(eigenvalues[0]), ground_state


def ground_state_rotation_angle(parameters: MinisuperspaceFRWParameters) -> float:
    """Return the single-qubit RY angle that prepares the benchmark ground state."""

    _, statevector = ground_state_data(parameters)
    return float(2.0 * math.atan2(statevector[1], statevector[0]))


def diagonal_operator_pauli_coefficients(
    lower_value: float,
    upper_value: float,
) -> dict[str, float]:
    """Return the Pauli coefficients for diag(lower_value, upper_value)."""

    return {
        "I": 0.5 * (lower_value + upper_value),
        "Z": 0.5 * (lower_value - upper_value),
    }


def default_backend_request_kwargs(
    experiment: MinisuperspaceFRWExperiment,
    tier: ExecutionTier,
) -> dict[str, Any]:
    """Translate configuration data into backend-request keyword arguments."""

    execution_configuration = experiment.configuration.execution_for_tier(tier)
    default_backend_names = {
        ExecutionTier.EXACT_LOCAL: "statevector_estimator",
        ExecutionTier.NOISY_LOCAL: "aer_estimator",
        ExecutionTier.IBM_HARDWARE: "ibm_backend_required",
    }
    return {
        "tier": tier,
        "backend_name": execution_configuration.backend_name
        or default_backend_names[tier],
        "shots": execution_configuration.shots,
        "seed": execution_configuration.seed,
        "precision": execution_configuration.precision,
        "optimization_level": execution_configuration.optimization_level,
        "options": dict(execution_configuration.options),
    }
