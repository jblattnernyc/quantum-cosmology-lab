"""Classical benchmark for the reduced Grand-Unification-Epoch-context toy model."""

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

from experiments.grand_unification_epoch_toy.common import (
    DEFAULT_CONFIG_PATH,
    GrandUnificationToyExperiment,
    GrandUnificationToyParameters,
    domain_wall_operator,
    effective_hamiltonian_matrix,
    ground_state_data,
    load_experiment_definition,
    order_parameter_operator,
    transverse_coherence_operator,
)


@dataclass(frozen=True)
class GrandUnificationToyBenchmark:
    """Benchmark values for the reduced two-site Z2 toy model."""

    spectrum: tuple[float, float, float, float]
    ground_energy: float
    ground_state: tuple[float, float, float, float]
    order_parameter_expectation: float
    domain_wall_density: float
    transverse_coherence_expectation: float
    effective_hamiltonian_expectation: float

    def expected_observable_values(self) -> dict[str, float]:
        """Return benchmark values keyed by observable name."""

        return {
            "order_parameter_expectation": self.order_parameter_expectation,
            "domain_wall_density": self.domain_wall_density,
            "transverse_coherence_expectation": (
                self.transverse_coherence_expectation
            ),
            "effective_hamiltonian_expectation": (
                self.effective_hamiltonian_expectation
            ),
        }


def _expectation_value(operator: np.ndarray, statevector: np.ndarray) -> float:
    """Return the expectation value of a Hermitian operator."""

    return float(np.real_if_close(statevector.conj().T @ operator @ statevector))


def compute_benchmark(
    parameters: GrandUnificationToyParameters,
) -> GrandUnificationToyBenchmark:
    """Compute the exact benchmark by direct diagonalization."""

    spectrum, ground_state = ground_state_data(parameters)
    hamiltonian = effective_hamiltonian_matrix(parameters)
    return GrandUnificationToyBenchmark(
        spectrum=tuple(float(value) for value in spectrum),
        ground_energy=float(spectrum[0]),
        ground_state=tuple(float(value) for value in ground_state),
        order_parameter_expectation=_expectation_value(
            order_parameter_operator(parameters),
            ground_state,
        ),
        domain_wall_density=_expectation_value(
            domain_wall_operator(parameters),
            ground_state,
        ),
        transverse_coherence_expectation=_expectation_value(
            transverse_coherence_operator(parameters),
            ground_state,
        ),
        effective_hamiltonian_expectation=_expectation_value(
            hamiltonian,
            ground_state,
        ),
    )


def benchmark_to_serializable(
    experiment: GrandUnificationToyExperiment,
    benchmark: GrandUnificationToyBenchmark,
) -> dict[str, object]:
    """Convert benchmark data into a serializable record."""

    return {
        "experiment_name": experiment.configuration.experiment_name,
        "scientific_question": experiment.configuration.scientific_question,
        "parameters": dict(experiment.configuration.parameters),
        "truncation": dict(experiment.configuration.truncation),
        "benchmark": {
            "spectrum": list(benchmark.spectrum),
            "ground_energy": benchmark.ground_energy,
            "ground_state": list(benchmark.ground_state),
            "order_parameter_expectation": benchmark.order_parameter_expectation,
            "domain_wall_density": benchmark.domain_wall_density,
            "transverse_coherence_expectation": (
                benchmark.transverse_coherence_expectation
            ),
            "effective_hamiltonian_expectation": (
                benchmark.effective_hamiltonian_expectation
            ),
            "effective_hamiltonian_matrix": effective_hamiltonian_matrix(
                experiment.parameters
            ).tolist(),
        },
    }


def write_benchmark_json(
    experiment: GrandUnificationToyExperiment,
    benchmark: GrandUnificationToyBenchmark,
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
    benchmark: GrandUnificationToyBenchmark,
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
                    f"{tier_label} comparison against the exact two-site Z2 "
                    "symmetry-breaking toy benchmark."
                ),
            )
        )
    return comparison_records


def comparison_records_for_result(
    result,
    benchmark: GrandUnificationToyBenchmark,
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
        description=(
            "Compute the direct benchmark for the reduced "
            "Grand-Unification-Epoch-context toy model."
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

