"""Circuit construction for the Planck-epoch-motivated minisuperspace model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from experiments.minisuperspace_frw.circuit import (
    build_ground_state_artifact,
    build_ground_state_circuit,
)

from experiments.planck_epoch_minisuperspace.common import (
    DEFAULT_CONFIG_PATH,
    load_experiment_definition,
)


def main(argv: list[str] | None = None) -> int:
    """Print the default ground-state circuit."""

    parser = argparse.ArgumentParser(
        description=(
            "Construct the Planck-epoch-motivated reduced minisuperspace "
            "state-preparation circuit."
        )
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    experiment = load_experiment_definition(args.config)
    circuit = build_ground_state_circuit(experiment.parameters)
    print(circuit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
