"""Observables for the reduced FRW minisuperspace toy model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from qclab.observables import ObservableDefinition, make_pauli_observable

from experiments.minisuperspace_frw.common import (
    DEFAULT_CONFIG_PATH,
    MinisuperspaceFRWParameters,
    diagonal_operator_pauli_coefficients,
    load_experiment_definition,
)


def build_scale_factor_observable(
    parameters: MinisuperspaceFRWParameters,
) -> ObservableDefinition:
    """Return the truncated scale-factor observable."""

    return make_pauli_observable(
        name="scale_factor_expectation_value",
        terms=diagonal_operator_pauli_coefficients(
            parameters.scale_factor_small,
            parameters.scale_factor_large,
        ),
        physical_meaning=(
            "Expectation value of the scale-factor operator in the two-bin "
            "positive-scale-factor truncation."
        ),
        units="dimensionless",
    )


def build_volume_observable(
    parameters: MinisuperspaceFRWParameters,
) -> ObservableDefinition:
    """Return the truncated FRW volume proxy observable."""

    return make_pauli_observable(
        name="volume_expectation_value",
        terms=diagonal_operator_pauli_coefficients(
            parameters.volume_small,
            parameters.volume_large,
        ),
        physical_meaning=(
            "Expectation value of the comoving volume proxy a^3 within the "
            "two-bin truncation."
        ),
        units="dimensionless",
    )


def build_effective_hamiltonian_observable(
    parameters: MinisuperspaceFRWParameters,
) -> ObservableDefinition:
    """Return the projected effective Hamiltonian observable."""

    return make_pauli_observable(
        name="effective_hamiltonian_expectation",
        terms={
            "Z": parameters.diagonal_bias,
            "X": -parameters.tunneling_strength,
        },
        physical_meaning=(
            "Expectation value of the projected effective minisuperspace "
            "Hamiltonian used in this toy truncation."
        ),
        units="dimensionless",
    )


def build_observables(
    parameters: MinisuperspaceFRWParameters,
) -> tuple[ObservableDefinition, ...]:
    """Return the observables used in the official experiment workflow."""

    return (
        build_scale_factor_observable(parameters),
        build_volume_observable(parameters),
        build_effective_hamiltonian_observable(parameters),
    )


def main(argv: list[str] | None = None) -> int:
    """Print observable labels for the default configuration."""

    parser = argparse.ArgumentParser(
        description="Display the Pauli observables used by the reduced FRW minisuperspace experiment."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    experiment = load_experiment_definition(args.config)
    for observable in build_observables(experiment.parameters):
        print(f"{observable.name}: {observable.operator_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
