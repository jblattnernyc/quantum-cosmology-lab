"""Classical benchmark for the reduced FRW minisuperspace toy model."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

import numpy as np

from qclab.analysis import compare_scalar_observable
from qclab.observables import ObservableEvaluation

from experiments.minisuperspace_frw.common import (
    DEFAULT_CONFIG_PATH,
    MinisuperspaceFRWExperiment,
    MinisuperspaceFRWParameters,
    effective_hamiltonian_matrix,
    ground_state_data,
    ground_state_rotation_angle,
    large_scale_factor_projector,
    load_experiment_definition,
    scale_factor_matrix,
    volume_matrix,
)


@dataclass(frozen=True)
class MinisuperspaceFRWBenchmark:
    """Benchmark values for the default reduced FRW parameter set."""

    ground_energy: float
    ground_state: tuple[float, float]
    rotation_angle: float
    scale_factor_expectation_value: float
    volume_expectation_value: float
    effective_hamiltonian_expectation: float
    large_scale_factor_probability: float

    def expected_observable_values(self) -> dict[str, float]:
        """Return benchmark values keyed by observable name."""

        return {
            "scale_factor_expectation_value": self.scale_factor_expectation_value,
            "volume_expectation_value": self.volume_expectation_value,
            "effective_hamiltonian_expectation": self.effective_hamiltonian_expectation,
        }


def _expectation_value(operator: np.ndarray, statevector: np.ndarray) -> float:
    """Return the expectation value of a Hermitian operator."""

    return float(np.real_if_close(statevector.T @ operator @ statevector))


def compute_benchmark(
    parameters: MinisuperspaceFRWParameters,
) -> MinisuperspaceFRWBenchmark:
    """Compute the exact reduced-model benchmark by direct diagonalization."""

    ground_energy, statevector = ground_state_data(parameters)
    scale_factor_expectation = _expectation_value(
        scale_factor_matrix(parameters), statevector
    )
    volume_expectation = _expectation_value(volume_matrix(parameters), statevector)
    effective_hamiltonian_expectation = _expectation_value(
        effective_hamiltonian_matrix(parameters), statevector
    )
    large_scale_factor_probability = _expectation_value(
        large_scale_factor_projector(parameters),
        statevector,
    )
    return MinisuperspaceFRWBenchmark(
        ground_energy=ground_energy,
        ground_state=(float(statevector[0]), float(statevector[1])),
        rotation_angle=ground_state_rotation_angle(parameters),
        scale_factor_expectation_value=scale_factor_expectation,
        volume_expectation_value=volume_expectation,
        effective_hamiltonian_expectation=effective_hamiltonian_expectation,
        large_scale_factor_probability=large_scale_factor_probability,
    )


def benchmark_to_serializable(
    experiment: MinisuperspaceFRWExperiment,
    benchmark: MinisuperspaceFRWBenchmark,
) -> dict[str, object]:
    """Convert benchmark data into a serializable record."""

    return {
        "experiment_name": experiment.configuration.experiment_name,
        "scientific_question": experiment.configuration.scientific_question,
        "parameters": dict(experiment.configuration.parameters),
        "truncation": dict(experiment.configuration.truncation),
        "benchmark": {
            "ground_energy": benchmark.ground_energy,
            "ground_state": list(benchmark.ground_state),
            "rotation_angle": benchmark.rotation_angle,
            "scale_factor_expectation_value": benchmark.scale_factor_expectation_value,
            "volume_expectation_value": benchmark.volume_expectation_value,
            "effective_hamiltonian_expectation": benchmark.effective_hamiltonian_expectation,
            "large_scale_factor_probability": benchmark.large_scale_factor_probability,
        },
    }


def write_benchmark_json(
    experiment: MinisuperspaceFRWExperiment,
    benchmark: MinisuperspaceFRWBenchmark,
    path: str | Path | None = None,
) -> Path:
    """Write the classical benchmark to disk as JSON."""

    resolved_path = (
        experiment.artifacts.benchmark_json
        if path is None
        else Path(path).expanduser().resolve()
    )
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(
        json.dumps(benchmark_to_serializable(experiment, benchmark), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return resolved_path


def comparison_records_for_evaluations(
    evaluations: tuple[ObservableEvaluation, ...],
    benchmark: MinisuperspaceFRWBenchmark,
    *,
    tier_label: str,
) -> list:
    """Build comparison records from observable evaluations alone."""

    target_values = benchmark.expected_observable_values()
    comparison_records = []
    for evaluation in evaluations:
        target_value = target_values[evaluation.observable.name]
        comparison_records.append(
            compare_scalar_observable(
                observable_name=evaluation.observable.name,
                benchmark_value=target_value,
                candidate_value=evaluation.value,
                interpretation=(
                    f"{tier_label} comparison against the direct two-state "
                    "diagonalization benchmark."
                ),
            )
        )
    return comparison_records


def comparison_records_for_result(
    result,
    benchmark: MinisuperspaceFRWBenchmark,
    *,
    tier_label: str,
) -> list:
    """Build comparison records between an execution result and the benchmark."""

    return comparison_records_for_evaluations(
        result.evaluations,
        benchmark,
        tier_label=tier_label,
    )


def main(argv: list[str] | None = None) -> int:
    """Compute and write the direct classical benchmark."""

    parser = argparse.ArgumentParser(
        description="Compute the direct benchmark for the reduced FRW minisuperspace toy model."
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
