"""Classical benchmark for the reduced two-link Z2 gauge toy model."""

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

from experiments.gut_toy_gauge.common import (
    DEFAULT_CONFIG_PATH,
    GutToyGaugeExperiment,
    GutToyGaugeParameters,
    full_hamiltonian_matrix,
    gauge_violation_operator,
    ground_state_data,
    ground_state_rotation_angle,
    link_alignment_operator,
    load_experiment_definition,
    physical_sector_projector,
    wilson_line_operator,
)


@dataclass(frozen=True)
class GutToyGaugeBenchmark:
    """Benchmark values for the default reduced toy-gauge parameter set."""

    spectrum: tuple[float, float, float, float]
    ground_energy: float
    ground_state: tuple[float, float, float, float]
    rotation_angle: float
    gauge_invariance_violation_expectation: float
    link_alignment_order_parameter: float
    wilson_line_correlator_proxy: float
    physical_sector_probability: float

    def expected_observable_values(self) -> dict[str, float]:
        """Return benchmark values keyed by observable name."""

        return {
            "gauge_invariance_violation_expectation": (
                self.gauge_invariance_violation_expectation
            ),
            "link_alignment_order_parameter": self.link_alignment_order_parameter,
            "wilson_line_correlator_proxy": self.wilson_line_correlator_proxy,
        }


def _expectation_value(operator: np.ndarray, statevector: np.ndarray) -> float:
    """Return the expectation value of a Hermitian operator."""

    return float(np.real_if_close(statevector.conj().T @ operator @ statevector))


def compute_benchmark(parameters: GutToyGaugeParameters) -> GutToyGaugeBenchmark:
    """Compute the exact benchmark by direct diagonalization."""

    spectrum, ground_state = ground_state_data(parameters)
    gauge_violation = _expectation_value(
        gauge_violation_operator(parameters),
        ground_state,
    )
    link_alignment = _expectation_value(
        link_alignment_operator(parameters),
        ground_state,
    )
    wilson_line = _expectation_value(
        wilson_line_operator(parameters),
        ground_state,
    )
    physical_sector_probability = _expectation_value(
        physical_sector_projector(parameters),
        ground_state,
    )
    return GutToyGaugeBenchmark(
        spectrum=tuple(float(value) for value in spectrum),
        ground_energy=float(spectrum[0]),
        ground_state=tuple(float(value) for value in ground_state),
        rotation_angle=ground_state_rotation_angle(parameters),
        gauge_invariance_violation_expectation=gauge_violation,
        link_alignment_order_parameter=link_alignment,
        wilson_line_correlator_proxy=wilson_line,
        physical_sector_probability=physical_sector_probability,
    )


def benchmark_to_serializable(
    experiment: GutToyGaugeExperiment,
    benchmark: GutToyGaugeBenchmark,
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
            "rotation_angle": benchmark.rotation_angle,
            "gauge_invariance_violation_expectation": (
                benchmark.gauge_invariance_violation_expectation
            ),
            "link_alignment_order_parameter": benchmark.link_alignment_order_parameter,
            "wilson_line_correlator_proxy": benchmark.wilson_line_correlator_proxy,
            "physical_sector_probability": benchmark.physical_sector_probability,
            "full_hamiltonian_matrix": full_hamiltonian_matrix(
                experiment.parameters
            ).tolist(),
        },
    }


def write_benchmark_json(
    experiment: GutToyGaugeExperiment,
    benchmark: GutToyGaugeBenchmark,
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
    benchmark: GutToyGaugeBenchmark,
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
                    f"{tier_label} comparison against the direct two-link Z2 "
                    "toy-gauge benchmark."
                ),
            )
        )
    return comparison_records


def comparison_records_for_result(
    result,
    benchmark: GutToyGaugeBenchmark,
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
        description="Compute the direct benchmark for the reduced two-link Z2 gauge toy model."
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
