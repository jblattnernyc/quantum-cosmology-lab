"""Shared utilities for the reduced Grand-Unification-Epoch-context toy model."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from qclab.backends.base import ExecutionTier
from qclab.utils.configuration import ModelConfiguration, load_model_configuration


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")


@dataclass(frozen=True)
class GrandUnificationToyParameters:
    """Typed parameters for the reduced two-site Z2 symmetry-breaking toy model."""

    alignment_coupling: float
    transverse_mixing: float
    symmetry_breaking_bias: float

    def __post_init__(self) -> None:
        if self.alignment_coupling <= 0:
            raise ValueError("alignment_coupling must be strictly positive.")
        if self.transverse_mixing < 0:
            raise ValueError("transverse_mixing must be non-negative.")


@dataclass(frozen=True)
class NoiseModelSpecification:
    """Serializable noisy-local settings for the experiment."""

    readout_error_probability: float
    method: str = "density_matrix"

    def __post_init__(self) -> None:
        if not 0 <= self.readout_error_probability < 1:
            raise ValueError("readout_error_probability must lie in [0, 1).")


@dataclass(frozen=True)
class GrandUnificationToyArtifactPaths:
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
class GrandUnificationToyExperiment:
    """Fully resolved experiment definition loaded from configuration."""

    configuration: ModelConfiguration
    parameters: GrandUnificationToyParameters
    noise_model: NoiseModelSpecification
    artifacts: GrandUnificationToyArtifactPaths


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


def _artifact_paths_from_metadata(
    metadata: dict[str, Any],
) -> GrandUnificationToyArtifactPaths:
    """Build artifact paths from configuration metadata."""

    raw_paths = dict(metadata.get("artifacts", {}))
    defaults = {
        "benchmark_json": "data/processed/grand_unification_epoch_toy/benchmark.json",
        "exact_local_json": "data/processed/grand_unification_epoch_toy/exact_local.json",
        "exact_local_comparisons_json": (
            "data/processed/grand_unification_epoch_toy/exact_local_comparisons.json"
        ),
        "noisy_local_json": "data/processed/grand_unification_epoch_toy/noisy_local.json",
        "noisy_local_comparisons_json": (
            "data/processed/grand_unification_epoch_toy/noisy_local_comparisons.json"
        ),
        "ibm_runtime_json": "data/processed/grand_unification_epoch_toy/ibm_runtime.json",
        "ibm_runtime_comparisons_json": (
            "data/processed/grand_unification_epoch_toy/ibm_runtime_comparisons.json"
        ),
        "ibm_runtime_metadata_json": (
            "data/raw/grand_unification_epoch_toy/ibm_runtime_metadata.json"
        ),
        "ibm_runtime_report_markdown": (
            "results/reports/grand_unification_epoch_toy/ibm_runtime_report.md"
        ),
        "analysis_summary_json": (
            "results/reports/grand_unification_epoch_toy/analysis_summary.json"
        ),
        "analysis_report_markdown": (
            "results/reports/grand_unification_epoch_toy/analysis_report.md"
        ),
        "observable_summary_table_markdown": (
            "results/tables/grand_unification_epoch_toy/observable_summary.md"
        ),
        "comparison_figure": (
            "results/figures/grand_unification_epoch_toy/observable_comparison.png"
        ),
    }
    resolved = {
        key: _resolve_artifact_path(raw_paths.get(key, default))
        for key, default in defaults.items()
    }
    return GrandUnificationToyArtifactPaths(**resolved)


def load_experiment_definition(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> GrandUnificationToyExperiment:
    """Load the experiment configuration and resolve typed parameters."""

    configuration = load_model_configuration(config_path)
    parameters = GrandUnificationToyParameters(
        alignment_coupling=_required_float(configuration.parameters, "alignment_coupling"),
        transverse_mixing=_required_float(configuration.parameters, "transverse_mixing"),
        symmetry_breaking_bias=_required_float(
            configuration.parameters,
            "symmetry_breaking_bias",
        ),
    )
    noise_metadata = dict(configuration.metadata.get("noise_model", {}))
    noise_model = NoiseModelSpecification(
        readout_error_probability=float(
            noise_metadata.get("readout_error_probability", 0.015)
        ),
        method=str(noise_metadata.get("method", "density_matrix")),
    )
    return GrandUnificationToyExperiment(
        configuration=configuration,
        parameters=parameters,
        noise_model=noise_model,
        artifacts=_artifact_paths_from_metadata(configuration.metadata),
    )


def _identity() -> np.ndarray:
    return np.eye(4, dtype=float)


def _pauli_z_site_0() -> np.ndarray:
    return np.diag([1.0, -1.0, 1.0, -1.0]).astype(float)


def _pauli_z_site_1() -> np.ndarray:
    return np.diag([1.0, 1.0, -1.0, -1.0]).astype(float)


def _pauli_x_site_0() -> np.ndarray:
    return np.array(
        [
            [0.0, 1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0, 0.0],
        ],
        dtype=float,
    )


def _pauli_x_site_1() -> np.ndarray:
    return np.array(
        [
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
        ],
        dtype=float,
    )


def _pauli_zz() -> np.ndarray:
    return np.diag([1.0, -1.0, -1.0, 1.0]).astype(float)


def order_parameter_operator(parameters: GrandUnificationToyParameters) -> np.ndarray:
    """Return the reduced two-site order-parameter operator."""

    del parameters
    return 0.5 * (_pauli_z_site_0() + _pauli_z_site_1())


def domain_wall_operator(parameters: GrandUnificationToyParameters) -> np.ndarray:
    """Return the projector onto anti-aligned two-site configurations."""

    del parameters
    return 0.5 * (_identity() - _pauli_zz())


def transverse_coherence_operator(
    parameters: GrandUnificationToyParameters,
) -> np.ndarray:
    """Return the reduced transverse-coherence operator."""

    del parameters
    return 0.5 * (_pauli_x_site_0() + _pauli_x_site_1())


def effective_hamiltonian_terms(
    parameters: GrandUnificationToyParameters,
) -> dict[str, float]:
    """Return the Pauli terms of the declared toy Hamiltonian."""

    return {
        "ZZ": -parameters.alignment_coupling,
        "IX": -0.5 * parameters.transverse_mixing,
        "XI": -0.5 * parameters.transverse_mixing,
        "IZ": -0.5 * parameters.symmetry_breaking_bias,
        "ZI": -0.5 * parameters.symmetry_breaking_bias,
    }


def effective_hamiltonian_matrix(
    parameters: GrandUnificationToyParameters,
) -> np.ndarray:
    """Return the reduced two-site Z2 toy Hamiltonian matrix."""

    return (
        -parameters.alignment_coupling * _pauli_zz()
        - parameters.transverse_mixing * transverse_coherence_operator(parameters)
        - parameters.symmetry_breaking_bias * order_parameter_operator(parameters)
    )


def canonicalize_real_statevector(statevector: np.ndarray) -> np.ndarray:
    """Fix the global phase of a real statevector for circuit preparation."""

    normalized = np.asarray(statevector, dtype=complex).reshape(-1)
    pivot_index = int(np.argmax(np.abs(normalized)))
    pivot = normalized[pivot_index]
    if pivot == 0:
        raise ValueError("Statevector cannot be canonicalized from the zero vector.")
    normalized = normalized * np.exp(-1j * np.angle(pivot))
    if np.max(np.abs(normalized.imag)) < 1e-12:
        normalized = normalized.real
    if float(np.real(normalized[pivot_index])) < 0:
        normalized = -normalized
    return np.asarray(normalized, dtype=float)


def ground_state_data(
    parameters: GrandUnificationToyParameters,
) -> tuple[np.ndarray, np.ndarray]:
    """Return the benchmark spectrum and canonicalized ground-state vector."""

    spectrum, eigenvectors = np.linalg.eigh(effective_hamiltonian_matrix(parameters))
    ground_state = canonicalize_real_statevector(eigenvectors[:, 0])
    return np.asarray(spectrum, dtype=float), ground_state


def default_backend_request_kwargs(
    experiment: GrandUnificationToyExperiment,
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

