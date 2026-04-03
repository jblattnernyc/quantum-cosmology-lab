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
class FocusBinObservableSpecification:
    """Optional probability observable for one retained scale-factor bin."""

    index: int
    name: str
    physical_meaning: str


@dataclass(frozen=True)
class MinisuperspaceFRWParameters:
    """Effective parameters for reduced FRW minisuperspace models."""

    scale_factor_bins: tuple[float, ...]
    model_variant: str = "two_bin_bias"
    diagonal_bias: float | None = None
    tunneling_strength: float | None = None
    nearest_neighbor_tunneling: float | None = None
    quadratic_potential_strength: float | None = None
    inverse_square_barrier_strength: float | None = None
    focus_bin_observable: FocusBinObservableSpecification | None = None

    def __post_init__(self) -> None:
        if len(self.scale_factor_bins) < 2:
            raise ValueError("At least two scale-factor bins are required.")
        if len(self.scale_factor_bins) & (len(self.scale_factor_bins) - 1):
            raise ValueError(
                "The retained scale-factor basis size must be a power of two."
            )
        if any(value <= 0 for value in self.scale_factor_bins):
            raise ValueError("All retained scale-factor bins must be strictly positive.")
        if any(
            upper <= lower
            for lower, upper in zip(self.scale_factor_bins, self.scale_factor_bins[1:])
        ):
            raise ValueError("Scale-factor bins must increase strictly.")
        if self.model_variant == "two_bin_bias":
            if len(self.scale_factor_bins) != 2:
                raise ValueError(
                    "The two_bin_bias minisuperspace model requires exactly two bins."
                )
            if self.tunneling_strength is None or self.tunneling_strength <= 0:
                raise ValueError(
                    "two_bin_bias requires a strictly positive tunneling_strength."
                )
        elif self.model_variant == "small_scale_factor_barrier":
            if self.nearest_neighbor_tunneling is None or self.nearest_neighbor_tunneling <= 0:
                raise ValueError(
                    "small_scale_factor_barrier requires a strictly positive nearest_neighbor_tunneling."
                )
            if self.quadratic_potential_strength is None:
                raise ValueError(
                    "small_scale_factor_barrier requires quadratic_potential_strength."
                )
            if self.inverse_square_barrier_strength is None or self.inverse_square_barrier_strength < 0:
                raise ValueError(
                    "small_scale_factor_barrier requires a non-negative inverse_square_barrier_strength."
                )
        else:
            raise ValueError(f"Unsupported minisuperspace model_variant: {self.model_variant}")
        if self.focus_bin_observable is not None:
            if not 0 <= self.focus_bin_observable.index < len(self.scale_factor_bins):
                raise ValueError(
                    "Focus-bin observable index must reference a retained basis bin."
                )

    @property
    def basis_size(self) -> int:
        """Return the retained Hilbert-space dimension."""

        return len(self.scale_factor_bins)

    @property
    def qubit_count(self) -> int:
        """Return the number of qubits needed for the retained basis."""

        return int(math.log2(self.basis_size))

    @property
    def scale_factor_small(self) -> float:
        """Return the smallest retained scale-factor bin."""

        return self.scale_factor_bins[0]

    @property
    def scale_factor_large(self) -> float:
        """Return the largest retained scale-factor bin."""

        return self.scale_factor_bins[-1]

    @property
    def scale_factor_mean(self) -> float:
        """Return the mean of the smallest and largest bins."""

        return 0.5 * (self.scale_factor_small + self.scale_factor_large)

    @property
    def scale_factor_z_coefficient(self) -> float:
        """Return the Pauli-Z coefficient for the two-bin scale-factor operator."""

        if self.basis_size != 2:
            raise ValueError(
                "scale_factor_z_coefficient is defined only for the two-bin truncation."
            )
        return 0.5 * (self.scale_factor_small - self.scale_factor_large)

    @property
    def volume_small(self) -> float:
        """Return the smallest retained volume-proxy entry."""

        return self.scale_factor_small**3

    @property
    def volume_large(self) -> float:
        """Return the largest retained volume-proxy entry."""

        return self.scale_factor_large**3

    @property
    def volume_entries(self) -> tuple[float, ...]:
        """Return the retained comoving volume-proxy diagonal entries."""

        return tuple(bin_center**3 for bin_center in self.scale_factor_bins)


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


def _optional_float(mapping: dict[str, Any], key: str) -> float | None:
    """Extract an optional float-valued parameter."""

    if key not in mapping or mapping[key] is None:
        return None
    return float(mapping[key])


def _scale_factor_bins(configuration: ModelConfiguration) -> tuple[float, ...]:
    """Resolve the retained scale-factor bins from configuration data."""

    raw_bins = configuration.truncation.get("bin_centers")
    if raw_bins is not None:
        return tuple(float(value) for value in raw_bins)
    if {
        "scale_factor_small",
        "scale_factor_large",
    }.issubset(configuration.parameters):
        return (
            float(configuration.parameters["scale_factor_small"]),
            float(configuration.parameters["scale_factor_large"]),
        )
    raise KeyError(
        "The minisuperspace configuration must declare truncation.bin_centers "
        "or the legacy scale_factor_small / scale_factor_large parameters."
    )


def _focus_bin_observable_from_metadata(
    metadata: dict[str, Any],
) -> FocusBinObservableSpecification | None:
    """Resolve an optional focus-bin observable declaration."""

    focus_bin_metadata = metadata.get("focus_bin_observable")
    if focus_bin_metadata is None:
        return None
    if not isinstance(focus_bin_metadata, dict):
        raise TypeError("focus_bin_observable metadata must be a mapping when present.")
    return FocusBinObservableSpecification(
        index=int(focus_bin_metadata["index"]),
        name=str(focus_bin_metadata["name"]),
        physical_meaning=str(focus_bin_metadata["physical_meaning"]),
    )


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
    model_variant = str(configuration.metadata.get("model_variant", "two_bin_bias"))
    parameters = MinisuperspaceFRWParameters(
        scale_factor_bins=_scale_factor_bins(configuration),
        model_variant=model_variant,
        diagonal_bias=_optional_float(configuration.parameters, "diagonal_bias"),
        tunneling_strength=_optional_float(configuration.parameters, "tunneling_strength"),
        nearest_neighbor_tunneling=_optional_float(
            configuration.parameters,
            "nearest_neighbor_tunneling",
        ),
        quadratic_potential_strength=_optional_float(
            configuration.parameters,
            "quadratic_potential_strength",
        ),
        inverse_square_barrier_strength=_optional_float(
            configuration.parameters,
            "inverse_square_barrier_strength",
        ),
        focus_bin_observable=_focus_bin_observable_from_metadata(configuration.metadata),
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


def effective_potential_entries(
    parameters: MinisuperspaceFRWParameters,
) -> tuple[float, ...] | None:
    """Return diagonal effective-potential entries when defined explicitly."""

    if parameters.model_variant == "two_bin_bias":
        return None
    return tuple(
        parameters.quadratic_potential_strength * (bin_center**2)
        + parameters.inverse_square_barrier_strength / (bin_center**2)
        for bin_center in parameters.scale_factor_bins
    )


def effective_hamiltonian_matrix(
    parameters: MinisuperspaceFRWParameters,
) -> np.ndarray:
    """Return the reduced effective Hamiltonian matrix."""

    if parameters.model_variant == "two_bin_bias":
        return np.array(
            [
                [parameters.diagonal_bias, -parameters.tunneling_strength],
                [-parameters.tunneling_strength, -parameters.diagonal_bias],
            ],
            dtype=float,
        )

    diagonal_entries = np.array(effective_potential_entries(parameters), dtype=float)
    dimension = parameters.basis_size
    hamiltonian = np.diag(diagonal_entries).astype(float)
    for index in range(dimension - 1):
        hamiltonian[index, index + 1] = -parameters.nearest_neighbor_tunneling
        hamiltonian[index + 1, index] = -parameters.nearest_neighbor_tunneling
    return hamiltonian


def scale_factor_matrix(parameters: MinisuperspaceFRWParameters) -> np.ndarray:
    """Return the truncated scale-factor operator."""

    return np.diag(parameters.scale_factor_bins).astype(float)


def volume_matrix(parameters: MinisuperspaceFRWParameters) -> np.ndarray:
    """Return the truncated volume proxy operator."""

    return np.diag(parameters.volume_entries).astype(float)


def selected_bin_projector(
    parameters: MinisuperspaceFRWParameters,
    bin_index: int,
) -> np.ndarray:
    """Return the projector onto one retained scale-factor bin."""

    if not 0 <= bin_index < parameters.basis_size:
        raise ValueError("The requested scale-factor bin index is out of range.")
    projector = np.zeros((parameters.basis_size, parameters.basis_size), dtype=float)
    projector[bin_index, bin_index] = 1.0
    return projector


def large_scale_factor_projector(
    parameters: MinisuperspaceFRWParameters,
) -> np.ndarray:
    """Return the projector onto the largest retained scale-factor bin."""

    return selected_bin_projector(parameters, parameters.basis_size - 1)


def focus_bin_projector(parameters: MinisuperspaceFRWParameters) -> np.ndarray | None:
    """Return the configured focus-bin projector when present."""

    if parameters.focus_bin_observable is None:
        return None
    return selected_bin_projector(parameters, parameters.focus_bin_observable.index)


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
    parameters: MinisuperspaceFRWParameters,
) -> tuple[float, np.ndarray]:
    """Return the benchmark ground-state energy and statevector."""

    eigenvalues, eigenvectors = np.linalg.eigh(effective_hamiltonian_matrix(parameters))
    ground_state = canonicalize_real_statevector(eigenvectors[:, 0])
    return float(eigenvalues[0]), ground_state


def ground_state_rotation_angle(parameters: MinisuperspaceFRWParameters) -> float | None:
    """Return the one-qubit RY angle when the retained basis has two states."""

    if parameters.basis_size != 2:
        return None
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
