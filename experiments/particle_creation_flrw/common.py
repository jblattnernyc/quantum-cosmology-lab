"""Shared utilities for the reduced FLRW particle-creation experiment."""

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
class ParticleCreationFLRWParameters:
    """Typed parameters for the reduced FLRW particle-creation toy model."""

    comoving_momentum: float
    mass: float
    scale_factor_initial: float
    scale_factor_final: float
    time_extent: float
    time_steps: int

    def __post_init__(self) -> None:
        if self.comoving_momentum <= 0:
            raise ValueError("comoving_momentum must be strictly positive.")
        if self.mass < 0:
            raise ValueError("mass must be non-negative.")
        if self.scale_factor_initial <= 0:
            raise ValueError("scale_factor_initial must be strictly positive.")
        if self.scale_factor_final <= self.scale_factor_initial:
            raise ValueError(
                "scale_factor_final must be greater than scale_factor_initial."
            )
        if self.time_extent <= 0:
            raise ValueError("time_extent must be strictly positive.")
        if self.time_steps <= 0:
            raise ValueError("time_steps must be a positive integer.")

    @property
    def delta_eta(self) -> float:
        return self.time_extent / self.time_steps


@dataclass(frozen=True)
class EvolutionSlice:
    """One discrete slice of the reduced time-dependent evolution."""

    index: int
    scale_factor_start: float
    scale_factor_end: float
    mode_frequency_start: float
    mode_frequency_end: float
    midpoint_frequency: float
    phase_angle: float
    squeezing_angle: float


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
class ParticleCreationArtifactPaths:
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
class ParticleCreationFLRWExperiment:
    """Fully resolved experiment definition loaded from configuration."""

    configuration: ModelConfiguration
    parameters: ParticleCreationFLRWParameters
    noise_model: NoiseModelSpecification
    artifacts: ParticleCreationArtifactPaths


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


def _required_int(mapping: dict[str, Any], key: str) -> int:
    """Extract a required integer-valued parameter."""

    if key not in mapping:
        raise KeyError(f"Missing required experiment parameter: {key}")
    return int(mapping[key])


def _artifact_paths_from_metadata(metadata: dict[str, Any]) -> ParticleCreationArtifactPaths:
    """Build artifact paths from configuration metadata."""

    raw_paths = dict(metadata.get("artifacts", {}))
    defaults = {
        "benchmark_json": "data/processed/particle_creation_flrw/benchmark.json",
        "exact_local_json": "data/processed/particle_creation_flrw/exact_local.json",
        "exact_local_comparisons_json": (
            "data/processed/particle_creation_flrw/exact_local_comparisons.json"
        ),
        "noisy_local_json": "data/processed/particle_creation_flrw/noisy_local.json",
        "noisy_local_comparisons_json": (
            "data/processed/particle_creation_flrw/noisy_local_comparisons.json"
        ),
        "ibm_runtime_json": "data/processed/particle_creation_flrw/ibm_runtime.json",
        "ibm_runtime_comparisons_json": (
            "data/processed/particle_creation_flrw/ibm_runtime_comparisons.json"
        ),
        "ibm_runtime_metadata_json": (
            "data/raw/particle_creation_flrw/ibm_runtime_metadata.json"
        ),
        "ibm_runtime_report_markdown": (
            "results/reports/particle_creation_flrw/ibm_runtime_report.md"
        ),
        "analysis_summary_json": "results/reports/particle_creation_flrw/analysis_summary.json",
        "analysis_report_markdown": (
            "results/reports/particle_creation_flrw/analysis_report.md"
        ),
        "observable_summary_table_markdown": (
            "results/tables/particle_creation_flrw/observable_summary.md"
        ),
        "comparison_figure": "results/figures/particle_creation_flrw/observable_comparison.png",
    }
    resolved = {
        key: _resolve_artifact_path(raw_paths.get(key, default))
        for key, default in defaults.items()
    }
    return ParticleCreationArtifactPaths(**resolved)


def load_experiment_definition(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> ParticleCreationFLRWExperiment:
    """Load the experiment configuration and resolve typed parameters."""

    configuration = load_model_configuration(config_path)
    parameters = ParticleCreationFLRWParameters(
        comoving_momentum=_required_float(configuration.parameters, "comoving_momentum"),
        mass=_required_float(configuration.parameters, "mass"),
        scale_factor_initial=_required_float(
            configuration.parameters, "scale_factor_initial"
        ),
        scale_factor_final=_required_float(
            configuration.parameters, "scale_factor_final"
        ),
        time_extent=_required_float(configuration.parameters, "time_extent"),
        time_steps=_required_int(configuration.parameters, "time_steps"),
    )
    noise_metadata = dict(configuration.metadata.get("noise_model", {}))
    noise_model = NoiseModelSpecification(
        one_qubit_depolarizing_probability=float(
            noise_metadata.get("one_qubit_depolarizing_probability", 0.001)
        ),
        two_qubit_depolarizing_probability=float(
            noise_metadata.get("two_qubit_depolarizing_probability", 0.003)
        ),
        readout_error_probability=float(
            noise_metadata.get("readout_error_probability", 0.01)
        ),
        method=str(noise_metadata.get("method", "density_matrix")),
    )
    artifacts = _artifact_paths_from_metadata(configuration.metadata)
    return ParticleCreationFLRWExperiment(
        configuration=configuration,
        parameters=parameters,
        noise_model=noise_model,
        artifacts=artifacts,
    )


def scale_factor_edges(parameters: ParticleCreationFLRWParameters) -> np.ndarray:
    """Return the discrete scale-factor samples."""

    return np.linspace(
        parameters.scale_factor_initial,
        parameters.scale_factor_final,
        parameters.time_steps + 1,
        dtype=float,
    )


def mode_frequency(
    scale_factor: float,
    parameters: ParticleCreationFLRWParameters,
) -> float:
    """Return the reduced effective mode frequency."""

    return math.sqrt(
        parameters.comoving_momentum**2 + (parameters.mass * scale_factor) ** 2
    )


def mode_frequency_edges(parameters: ParticleCreationFLRWParameters) -> np.ndarray:
    """Return the discrete mode-frequency samples."""

    return np.array(
        [mode_frequency(scale_factor, parameters) for scale_factor in scale_factor_edges(parameters)],
        dtype=float,
    )


def evolution_slices(
    parameters: ParticleCreationFLRWParameters,
) -> tuple[EvolutionSlice, ...]:
    """Construct the slice-by-slice evolution parameters."""

    scale_factors = scale_factor_edges(parameters)
    frequencies = mode_frequency_edges(parameters)
    delta_eta = parameters.delta_eta
    slices: list[EvolutionSlice] = []
    for index in range(parameters.time_steps):
        frequency_start = float(frequencies[index])
        frequency_end = float(frequencies[index + 1])
        midpoint_frequency = 0.5 * (frequency_start + frequency_end)
        squeezing_angle = 0.5 * math.log(frequency_end / frequency_start)
        phase_angle = midpoint_frequency * delta_eta
        slices.append(
            EvolutionSlice(
                index=index,
                scale_factor_start=float(scale_factors[index]),
                scale_factor_end=float(scale_factors[index + 1]),
                mode_frequency_start=frequency_start,
                mode_frequency_end=frequency_end,
                midpoint_frequency=midpoint_frequency,
                phase_angle=phase_angle,
                squeezing_angle=squeezing_angle,
            )
        )
    return tuple(slices)


def apply_evolution_slice(
    even_state: np.ndarray,
    evolution_slice: EvolutionSlice,
) -> np.ndarray:
    """Apply one discrete evolution slice in the even-parity subspace."""

    state = np.asarray(even_state, dtype=complex).reshape(2)
    c00, c11 = state
    phase = evolution_slice.phase_angle
    c00 *= np.exp(1j * phase)
    c11 *= np.exp(-1j * phase)
    cosine = math.cos(evolution_slice.squeezing_angle)
    sine = math.sin(evolution_slice.squeezing_angle)
    return np.array(
        [
            cosine * c00 - 1j * sine * c11,
            -1j * sine * c00 + cosine * c11,
        ],
        dtype=complex,
    )


def evolve_even_subspace_state(
    parameters: ParticleCreationFLRWParameters,
) -> np.ndarray:
    """Return the final even-parity statevector `(c_00, c_11)`."""

    state = np.array([1.0 + 0.0j, 0.0 + 0.0j], dtype=complex)
    for evolution_slice in evolution_slices(parameters):
        state = apply_evolution_slice(state, evolution_slice)
    return state


def full_statevector_from_even_subspace(even_state: np.ndarray) -> np.ndarray:
    """Embed the even-parity state into the full two-qubit basis."""

    state = np.asarray(even_state, dtype=complex).reshape(2)
    return np.array([state[0], 0.0 + 0.0j, 0.0 + 0.0j, state[1]], dtype=complex)


def canonicalize_statevector(statevector: np.ndarray) -> np.ndarray:
    """Fix the global phase of a complex statevector."""

    normalized = np.asarray(statevector, dtype=complex).reshape(-1)
    pivot_index = int(np.argmax(np.abs(normalized)))
    pivot = normalized[pivot_index]
    if pivot == 0:
        raise ValueError("Statevector cannot be canonicalized from the zero vector.")
    normalized = normalized * np.exp(-1j * np.angle(pivot))
    if normalized[pivot_index].real < 0:
        normalized = -normalized
    return normalized


def default_backend_request_kwargs(
    experiment: ParticleCreationFLRWExperiment,
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
