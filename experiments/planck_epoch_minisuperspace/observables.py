"""Observables for the Planck-epoch-motivated minisuperspace model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from experiments.minisuperspace_frw.observables import (
    build_effective_hamiltonian_observable,
    build_focus_bin_probability_observable,
    build_observables,
    build_scale_factor_observable,
    build_volume_observable,
)

from experiments.planck_epoch_minisuperspace.common import (
    DEFAULT_CONFIG_PATH,
    load_experiment_definition,
)


def main(argv: list[str] | None = None) -> int:
    """Print observable labels for the default configuration."""

    parser = argparse.ArgumentParser(
        description=(
            "Display the Pauli observables used by the Planck-epoch-motivated "
            "reduced minisuperspace experiment."
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
