"""Classical benchmark for the Planck-epoch-motivated minisuperspace model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from experiments.minisuperspace_frw.benchmark import (
    MinisuperspaceFRWBenchmark as PlanckEpochMinisuperspaceBenchmark,
    comparison_records_for_evaluations,
    comparison_records_for_result,
    compute_benchmark,
    write_benchmark_json,
)

from experiments.planck_epoch_minisuperspace.common import (
    DEFAULT_CONFIG_PATH,
    load_experiment_definition,
)


def main(argv: list[str] | None = None) -> int:
    """Compute and write the direct classical benchmark."""

    parser = argparse.ArgumentParser(
        description=(
            "Compute the direct benchmark for the Planck-epoch-motivated "
            "reduced minisuperspace experiment."
        )
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    experiment = load_experiment_definition(args.config)
    benchmark = compute_benchmark(experiment.parameters)
    output_path = write_benchmark_json(experiment, benchmark, args.output)
    print(f"Wrote benchmark to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
