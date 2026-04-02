"""Shared utilities for the reduced two-link Z2 gauge toy experiment."""

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
class GutToyGaugeParameters:
    """Typed parameters for the reduced two-link Z2 gauge toy model."""

    electric_field_bias: float
    pair_flip_coupling: float
    gauge_penalty: float

    def __post_init__(self) -> None:
        if self.pair_flip_coupling <= 0:
            raise ValueError("pair_flip_coupling must be strictly positive.")
        if self.gauge_penalty <= 0:
            raise ValueError("gauge_penalty must be strictly positive.")


@dataclass(frozen=True)
class NoiseModelSpecification:
    """Serializable Aer noise-model settings for the experiment."""

    one_qubit_depolarizing_probability: float
    two_qubit_depolarizing_probability: float
    readout_error_probability: float
    method: str = "density_matrix"

    def __post_init__(self) -> None:
        for name, value in (
            ("one_qubit_depolarizing_probability", self.one_qubit_depolarizing_probability),
            ("two_qubit_depolarizing_probability", self.two_qubit_depolarizing_probability),
            ("readout_error_probability", self.readout_error_probability),
        ):
            if not 0 <= value < 1:
                raise ValueError(f"{name} must lie in [0, 1).")


@dataclass(frozen=True)
class GutToyGaugeArtifactPaths:
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
class GutToyGaugeExperiment:
    """Fully resolved experiment definition loaded from configuration."""

    configuration: ModelConfiguration
    parameters: GutToyGaugeParameters
    noise_model: NoiseModelSpecification
    artifacts: GutToyGaugeArtifactPaths


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


def _artifact_paths_from_metadata(metadata: dict[str, Any]) -> GutToyGaugeArtifactPaths:
    """Build artifact paths from configuration metadata."""

    raw_paths = dict(metadata.get("artifacts", {}))
    defaults = {
        "benchmark_json": "data/processed/gut_toy_gauge/benchmark.json",
        "exact_local_json": "data/processed/gut_toy_gauge/exact_local.json",
        "exact_local_comparisons_json": (
            "data/processed/gut_toy_gauge/exact_local_comparisons.json"
        ),
        "noisy_local_json": "data/processed/gut_toy_gauge/noisy_local.json",
        "noisy_local_comparisons_json": (
            "data/processed/gut_toy_gauge/noisy_local_comparisons.json"
        ),
        "ibm_runtime_json": "data/processed/gut_toy_gauge/ibm_runtime.json",
        "ibm_runtime_comparisons_json": (
            "data/processed/gut_toy_gauge/ibm_runtime_comparisons.json"
        ),
        "ibm_runtime_metadata_json": "data/raw/gut_toy_gauge/ibm_runtime_metadata.json",
        "ibm_runtime_report_markdown": (
            "results/reports/gut_toy_gauge/ibm_runtime_report.md"
        ),
        "analysis_summary_json": "results/reports/gut_toy_gauge/analysis_summary.json",
        "analysis_report_markdown": (
            "results/reports/gut_toy_gauge/analysis_report.md"
        ),
        "observable_summary_table_markdown": (
            "results/tables/gut_toy_gauge/observable_summary.md"
        ),
        "comparison_figure": "results/figures/gut_toy_gauge/observable_comparison.png",
    }
    resolved = {
        key: _resolve_artifact_path(raw_paths.get(key, default))
        for key, default in defaults.items()
    }
    return GutToyGaugeArtifactPaths(**resolved)


def load_experiment_definition(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> GutToyGaugeExperiment:
    """Load the experiment configuration and resolve typed parameters."""

    configuration = load_model_configuration(config_path)
    parameters = GutToyGaugeParameters(
        electric_field_bias=_required_float(
            configuration.parameters,
            "electric_field_bias",
        ),
        pair_flip_coupling=_required_float(
            configuration.parameters,
            "pair_flip_coupling",
        ),
        gauge_penalty=_required_float(configuration.parameters, "gauge_penalty"),
    )
    noise_metadata = dict(configuration.metadata.get("noise_model", {}))
    noise_model = NoiseModelSpecification(
        one_qubit_depolarizing_probability=float(
            noise_metadata.get("one_qubit_depolarizing_probability", 0.002)
        ),
        two_qubit_depolarizing_probability=float(
            noise_metadata.get("two_qubit_depolarizing_probability", 0.008)
        ),
        readout_error_probability=float(
            noise_metadata.get("readout_error_probability", 0.015)
        ),
        method=str(noise_metadata.get("method", "density_matrix")),
    )
    artifacts = _artifact_paths_from_metadata(configuration.metadata)
    return GutToyGaugeExperiment(
        configuration=configuration,
        parameters=parameters,
        noise_model=noise_model,
        artifacts=artifacts,
    )


def _identity() -> np.ndarray:
    return np.eye(4, dtype=float)


def _pauli_z_first_qubit() -> np.ndarray:
    return np.diag([1.0, -1.0, 1.0, -1.0]).astype(float)


def _pauli_z_second_qubit() -> np.ndarray:
    return np.diag([1.0, 1.0, -1.0, -1.0]).astype(float)


def _pauli_zz() -> np.ndarray:
    return np.diag([1.0, -1.0, -1.0, 1.0]).astype(float)


def _pauli_xx() -> np.ndarray:
    return np.array(
        [
            [0.0, 0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )


def link_alignment_operator(parameters: GutToyGaugeParameters) -> np.ndarray:
    """Return the reduced link-alignment operator."""

    del parameters
    return 0.5 * (_pauli_z_first_qubit() + _pauli_z_second_qubit())


def wilson_line_operator(parameters: GutToyGaugeParameters) -> np.ndarray:
    """Return the reduced two-link Wilson-line correlator proxy."""

    del parameters
    return _pauli_xx()


def gauge_violation_operator(parameters: GutToyGaugeParameters) -> np.ndarray:
    """Return the projector onto the odd-parity, gauge-violating sector."""

    del parameters
    return 0.5 * (_identity() - _pauli_zz())


def physical_sector_projector(parameters: GutToyGaugeParameters) -> np.ndarray:
    """Return the projector onto the gauge-invariant sector."""

    del parameters
    return 0.5 * (_identity() + _pauli_zz())


def full_hamiltonian_matrix(parameters: GutToyGaugeParameters) -> np.ndarray:
    """Return the full two-link toy Hamiltonian matrix."""

    return (
        parameters.electric_field_bias * link_alignment_operator(parameters)
        - parameters.pair_flip_coupling * wilson_line_operator(parameters)
        + parameters.gauge_penalty * gauge_violation_operator(parameters)
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


def ground_state_data(parameters: GutToyGaugeParameters) -> tuple[np.ndarray, np.ndarray]:
    """Return the benchmark spectrum and canonicalized ground-state vector."""

    spectrum, eigenvectors = np.linalg.eigh(full_hamiltonian_matrix(parameters))
    ground_state = canonicalize_real_statevector(eigenvectors[:, 0])
    return np.asarray(spectrum, dtype=float), ground_state


def ground_state_rotation_angle(parameters: GutToyGaugeParameters) -> float:
    """Return the single-parameter angle used in the state-preparation circuit."""

    _, statevector = ground_state_data(parameters)
    if abs(float(statevector[1])) > 1e-12 or abs(float(statevector[2])) > 1e-12:
        raise ValueError(
            "The chosen benchmark ground state has support outside the gauge-invariant "
            "two-state subspace and cannot be prepared by the reduced circuit."
        )
    return float(2.0 * math.atan2(float(statevector[3]), float(statevector[0])))


def default_backend_request_kwargs(
    experiment: GutToyGaugeExperiment,
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
