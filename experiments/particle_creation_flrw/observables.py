"""Observables for the reduced FLRW particle-creation toy model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from qclab.observables import ObservableDefinition, make_pauli_observable

from experiments.particle_creation_flrw.common import (
    DEFAULT_CONFIG_PATH,
    ParticleCreationFLRWParameters,
    load_experiment_definition,
)


def build_single_mode_particle_number_observable(
    parameters: ParticleCreationFLRWParameters,
) -> ObservableDefinition:
    """Return the particle-number observable for qiskit qubit 0."""

    del parameters
    return make_pauli_observable(
        name="single_mode_particle_number_expectation",
        terms={"II": 0.5, "IZ": -0.5},
        physical_meaning=(
            "Expectation value of the retained occupation number for mode k, "
            "encoded in qiskit qubit 0."
        ),
        units="dimensionless",
        metadata={"mode": "k", "qubit_index": 0},
    )


def build_total_particle_number_observable(
    parameters: ParticleCreationFLRWParameters,
) -> ObservableDefinition:
    """Return the total particle-number observable for the retained mode pair."""

    del parameters
    return make_pauli_observable(
        name="total_particle_number_expectation",
        terms={"II": 1.0, "IZ": -0.5, "ZI": -0.5},
        physical_meaning=(
            "Expectation value of the total retained particle number n_k + "
            "n_-k in the two-mode truncation."
        ),
        units="dimensionless",
    )


def build_pairing_correlator_observable(
    parameters: ParticleCreationFLRWParameters,
) -> ObservableDefinition:
    """Return the anomalous pair-correlation observable."""

    del parameters
    return make_pauli_observable(
        name="pairing_correlator_expectation",
        terms={"XX": 0.5, "YY": -0.5},
        physical_meaning=(
            "Expectation value of a_k^dagger a_-k^dagger + a_k a_-k within the "
            "retained two-mode truncation."
        ),
        units="dimensionless",
    )


def build_observables(
    parameters: ParticleCreationFLRWParameters,
) -> tuple[ObservableDefinition, ...]:
    """Return the observables used in the official experiment workflow."""

    return (
        build_single_mode_particle_number_observable(parameters),
        build_total_particle_number_observable(parameters),
        build_pairing_correlator_observable(parameters),
    )


def main(argv: list[str] | None = None) -> int:
    """Print observable labels for the default configuration."""

    parser = argparse.ArgumentParser(
        description="Display the Pauli observables used by the reduced FLRW particle-creation experiment."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    experiment = load_experiment_definition(args.config)
    for observable in build_observables(experiment.parameters):
        print(f"{observable.name}: {observable.operator_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
