"""Observables for the reduced two-link Z2 gauge toy model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from qclab.observables import ObservableDefinition, make_pauli_observable

from experiments.gut_toy_gauge.common import (
    DEFAULT_CONFIG_PATH,
    GutToyGaugeParameters,
    load_experiment_definition,
)


def build_gauge_invariance_violation_observable(
    parameters: GutToyGaugeParameters,
) -> ObservableDefinition:
    """Return the odd-sector projector that diagnoses gauge-violation leakage."""

    del parameters
    return make_pauli_observable(
        name="gauge_invariance_violation_expectation",
        terms={"II": 0.5, "ZZ": -0.5},
        physical_meaning=(
            "Expectation value of the odd-parity projector that measures "
            "leakage out of the retained gauge-invariant sector."
        ),
        units="dimensionless",
    )


def build_link_alignment_order_parameter(
    parameters: GutToyGaugeParameters,
) -> ObservableDefinition:
    """Return the reduced link-alignment order parameter."""

    del parameters
    return make_pauli_observable(
        name="link_alignment_order_parameter",
        terms={"IZ": 0.5, "ZI": 0.5},
        physical_meaning=(
            "Expectation value of the average retained Z2 electric-flux "
            "orientation across the two links."
        ),
        units="dimensionless",
    )


def build_wilson_line_correlator_proxy(
    parameters: GutToyGaugeParameters,
) -> ObservableDefinition:
    """Return the reduced two-link Wilson-line correlator proxy."""

    del parameters
    return make_pauli_observable(
        name="wilson_line_correlator_proxy",
        terms={"XX": 1.0},
        physical_meaning=(
            "Expectation value of a gauge-invariant two-link flip operator "
            "used here as a Wilson-line correlator proxy."
        ),
        units="dimensionless",
    )


def build_observables(
    parameters: GutToyGaugeParameters,
) -> tuple[ObservableDefinition, ...]:
    """Return the observables used in the official experiment workflow."""

    return (
        build_gauge_invariance_violation_observable(parameters),
        build_link_alignment_order_parameter(parameters),
        build_wilson_line_correlator_proxy(parameters),
    )


def main(argv: list[str] | None = None) -> int:
    """Print observable labels for the default configuration."""

    parser = argparse.ArgumentParser(
        description="Display the Pauli observables used by the reduced two-link Z2 gauge experiment."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    experiment = load_experiment_definition(args.config)
    for observable in build_observables(experiment.parameters):
        print(f"{observable.name}: {observable.operator_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
