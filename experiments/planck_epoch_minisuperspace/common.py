"""Shared utilities for the Planck-epoch-motivated minisuperspace experiment."""

from __future__ import annotations

from pathlib import Path

from experiments.minisuperspace_frw.common import (
    FocusBinObservableSpecification,
    MinisuperspaceArtifactPaths,
    MinisuperspaceFRWExperiment,
    MinisuperspaceFRWParameters,
    NoiseModelSpecification,
    canonicalize_real_statevector,
    default_backend_request_kwargs,
    diagonal_operator_pauli_coefficients,
    effective_hamiltonian_matrix,
    effective_potential_entries,
    focus_bin_projector,
    ground_state_data,
    ground_state_rotation_angle,
    large_scale_factor_projector,
    load_experiment_definition as _load_experiment_definition,
    scale_factor_matrix,
    selected_bin_projector,
    volume_matrix,
)


DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")

PlanckEpochMinisuperspaceExperiment = MinisuperspaceFRWExperiment
PlanckEpochMinisuperspaceParameters = MinisuperspaceFRWParameters
PlanckEpochArtifactPaths = MinisuperspaceArtifactPaths


def load_experiment_definition(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> PlanckEpochMinisuperspaceExperiment:
    """Load the local experiment configuration and resolve typed parameters."""

    return _load_experiment_definition(config_path)


__all__ = [
    "DEFAULT_CONFIG_PATH",
    "FocusBinObservableSpecification",
    "NoiseModelSpecification",
    "PlanckEpochArtifactPaths",
    "PlanckEpochMinisuperspaceExperiment",
    "PlanckEpochMinisuperspaceParameters",
    "canonicalize_real_statevector",
    "default_backend_request_kwargs",
    "diagonal_operator_pauli_coefficients",
    "effective_hamiltonian_matrix",
    "effective_potential_entries",
    "focus_bin_projector",
    "ground_state_data",
    "ground_state_rotation_angle",
    "large_scale_factor_projector",
    "load_experiment_definition",
    "scale_factor_matrix",
    "selected_bin_projector",
    "volume_matrix",
]
