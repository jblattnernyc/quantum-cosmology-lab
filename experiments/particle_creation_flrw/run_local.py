"""Exact local execution for the reduced FLRW particle-creation toy model."""

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
from qclab.validation import assess_observable_values

from experiments.particle_creation_flrw.benchmark import (
    comparison_records_for_result,
    compute_benchmark,
    validation_context_for_benchmark,
    write_benchmark_json,
)
from experiments.particle_creation_flrw.circuit import build_particle_creation_circuit
from experiments.particle_creation_flrw.common import (
    DEFAULT_CONFIG_PATH,
    default_backend_request_kwargs,
    load_experiment_definition,
    validation_configuration_for_experiment,
)
from experiments.particle_creation_flrw.observables import build_observables


def run_exact_local(config_path: str = str(DEFAULT_CONFIG_PATH)) -> dict[str, str]:
    """Execute the exact local reference path and persist its outputs."""

    experiment = load_experiment_definition(config_path)
    validate_execution_progression(
        ExecutionTier.EXACT_LOCAL,
        benchmark_complete=True,
    )
    benchmark = compute_benchmark(experiment.parameters)
    validation_context = validation_context_for_benchmark(experiment, benchmark)
    write_benchmark_json(
        experiment,
        benchmark,
        validation_context=validation_context,
    )

    observables = build_observables(experiment.parameters)
    request = BackendRequest(
        **default_backend_request_kwargs(experiment, ExecutionTier.EXACT_LOCAL)
    )
    result = ExactLocalEstimatorExecutor().run(
        build_particle_creation_circuit(experiment.parameters),
        observables,
        request=request,
    )
    validation_assessment = assess_observable_values(
        tier=ExecutionTier.EXACT_LOCAL.value,
        lineage_id=validation_context.lineage_id,
        evaluations=result.evaluations,
        benchmark_values=benchmark.expected_observable_values(),
        validation_configuration=validation_configuration_for_experiment(experiment),
    )
    comparison_records = comparison_records_for_result(
        result,
        benchmark,
        tier_label="Exact local",
    )
    execution_path = write_execution_result_json(
        result,
        experiment.artifacts.exact_local_json,
        validation_context=validation_context,
        validation_assessment=validation_assessment,
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
        description="Run the exact local reduced FLRW particle-creation workflow."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    outputs = run_exact_local(args.config)
    for label, path in outputs.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
