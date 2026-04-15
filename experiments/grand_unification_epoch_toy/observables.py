"""Observables for the reduced Grand-Unification-Epoch-context toy model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from qclab.observables import ObservableDefinition, make_pauli_observable

from experiments.grand_unification_epoch_toy.common import (
    DEFAULT_CONFIG_PATH,
    GrandUnificationToyParameters,
    effective_hamiltonian_terms,
    load_experiment_definition,
)


def build_order_parameter_observable(
    parameters: GrandUnificationToyParameters,
) -> ObservableDefinition:
    """Return the reduced two-site order-parameter observable."""

    del parameters
    return make_pauli_observable(
        name="order_parameter_expectation",
        terms={"IZ": 0.5, "ZI": 0.5},
        physical_meaning=(
            "Expectation value of the average retained Z2 order-parameter "
            "orientation across the two-site toy truncation."
        ),
        units="dimensionless",
    )


def build_domain_wall_density_observable(
    parameters: GrandUnificationToyParameters,
) -> ObservableDefinition:
    """Return the anti-alignment diagnostic for the retained two-site system."""

    del parameters
    return make_pauli_observable(
        name="domain_wall_density",
        terms={"II": 0.5, "ZZ": -0.5},
        physical_meaning=(
            "Expectation value of the anti-aligned-sector projector used as a "
            "finite two-site domain-wall proxy."
        ),
        units="dimensionless",
    )


def build_transverse_coherence_observable(
    parameters: GrandUnificationToyParameters,
) -> ObservableDefinition:
    """Return the transverse-coherence observable for the toy model."""

    del parameters
    return make_pauli_observable(
        name="transverse_coherence_expectation",
        terms={"IX": 0.5, "XI": 0.5},
        physical_meaning=(
            "Expectation value of the reduced transverse-mixing operator that "
            "couples the retained Z2 order-parameter configurations."
        ),
        units="dimensionless",
    )


def build_effective_hamiltonian_observable(
    parameters: GrandUnificationToyParameters,
) -> ObservableDefinition:
    """Return the declared effective-Hamiltonian observable."""

    return make_pauli_observable(
        name="effective_hamiltonian_expectation",
        terms=effective_hamiltonian_terms(parameters),
        physical_meaning=(
            "Expectation value of the projected two-site Z2 toy Hamiltonian."
        ),
        units="dimensionless",
    )


def build_observables(
    parameters: GrandUnificationToyParameters,
) -> tuple[ObservableDefinition, ...]:
    """Return the observables used in the official experiment workflow."""

    return (
        build_order_parameter_observable(parameters),
        build_domain_wall_density_observable(parameters),
        build_transverse_coherence_observable(parameters),
        build_effective_hamiltonian_observable(parameters),
    )


def main(argv: list[str] | None = None) -> int:
    """Print observable labels for the default configuration."""

    parser = argparse.ArgumentParser(
        description=(
            "Display the Pauli observables used by the "
            "Grand-Unification-Epoch-context toy experiment."
        )
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    experiment = load_experiment_definition(args.config)
    for observable in build_observables(experiment.parameters):
        print(f"{observable.name}: {observable.operator_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

