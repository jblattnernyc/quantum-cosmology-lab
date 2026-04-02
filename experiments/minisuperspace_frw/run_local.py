"""Exact local execution for the reduced FRW minisuperspace toy model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from qclab.analysis import write_comparison_records_json
from qclab.backends import (
    BackendRequest,
    ExactLocalEstimatorExecutor,
    write_execution_result_json,
)
from qclab.backends.base import ExecutionTier, validate_execution_progression

from experiments.minisuperspace_frw.benchmark import (
    comparison_records_for_result,
    compute_benchmark,
    write_benchmark_json,
)
from experiments.minisuperspace_frw.circuit import build_ground_state_circuit
from experiments.minisuperspace_frw.common import (
    DEFAULT_CONFIG_PATH,
    default_backend_request_kwargs,
    load_experiment_definition,
)
from experiments.minisuperspace_frw.observables import build_observables


def run_exact_local(config_path: str = str(DEFAULT_CONFIG_PATH)) -> dict[str, str]:
    """Execute the exact local reference path and persist its outputs."""

    experiment = load_experiment_definition(config_path)
    validate_execution_progression(
        ExecutionTier.EXACT_LOCAL,
        benchmark_complete=True,
    )
    benchmark = compute_benchmark(experiment.parameters)
    write_benchmark_json(experiment, benchmark)

    request = BackendRequest(**default_backend_request_kwargs(experiment, ExecutionTier.EXACT_LOCAL))
    result = ExactLocalEstimatorExecutor().run(
        build_ground_state_circuit(experiment.parameters),
        build_observables(experiment.parameters),
        request=request,
    )
    comparison_records = comparison_records_for_result(
        result,
        benchmark,
        tier_label="Exact local",
    )
    execution_path = write_execution_result_json(
        result,
        experiment.artifacts.exact_local_json,
    )
    comparison_path = write_comparison_records_json(
        comparison_records,
        experiment.artifacts.exact_local_comparisons_json,
    )
    return {
        "benchmark_json": str(experiment.artifacts.benchmark_json),
        "exact_local_json": str(execution_path),
        "exact_local_comparisons_json": str(comparison_path),
    }


def main(argv: list[str] | None = None) -> int:
    """Run the exact local experiment path."""

    parser = argparse.ArgumentParser(
        description="Run the exact local reduced FRW minisuperspace workflow."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    outputs = run_exact_local(args.config)
    for label, path in outputs.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
