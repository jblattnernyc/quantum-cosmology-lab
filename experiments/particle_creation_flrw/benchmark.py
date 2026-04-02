"""Classical benchmark for the reduced FLRW particle-creation toy model."""

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

from experiments.particle_creation_flrw.common import (
    DEFAULT_CONFIG_PATH,
    EvolutionSlice,
    ParticleCreationFLRWExperiment,
    ParticleCreationFLRWParameters,
    canonicalize_statevector,
    evolution_slices,
    evolve_even_subspace_state,
    full_statevector_from_even_subspace,
    load_experiment_definition,
    mode_frequency_edges,
    scale_factor_edges,
)


@dataclass(frozen=True)
class ParticleCreationFLRWBenchmark:
    """Benchmark values for the default reduced FLRW particle-creation model."""

    final_statevector: tuple[complex, complex, complex, complex]
    scale_factor_edges: tuple[float, ...]
    mode_frequency_edges: tuple[float, ...]
    slices: tuple[EvolutionSlice, ...]
    single_mode_particle_number_expectation: float
    total_particle_number_expectation: float
    pairing_correlator_expectation: float
    pair_occupation_probability: float
    even_parity_probability: float

    def expected_observable_values(self) -> dict[str, float]:
        """Return benchmark values keyed by observable name."""

        return {
            "single_mode_particle_number_expectation": (
                self.single_mode_particle_number_expectation
            ),
            "total_particle_number_expectation": (
                self.total_particle_number_expectation
            ),
            "pairing_correlator_expectation": self.pairing_correlator_expectation,
        }


def _complex_record(value: complex) -> dict[str, float]:
    """Return a JSON-safe complex scalar record."""

    return {"real": float(value.real), "imag": float(value.imag)}


def compute_benchmark(
    parameters: ParticleCreationFLRWParameters,
) -> ParticleCreationFLRWBenchmark:
    """Compute the exact benchmark of the declared discrete model."""

    even_state = evolve_even_subspace_state(parameters)
    full_statevector = canonicalize_statevector(
        full_statevector_from_even_subspace(even_state)
    )
    c00 = complex(full_statevector[0])
    c11 = complex(full_statevector[3])
    pair_probability = float(abs(c11) ** 2)
    single_mode_particle_number = pair_probability
    total_particle_number = 2.0 * pair_probability
    pairing_correlator = float(2.0 * np.real(np.conj(c00) * c11))
    even_parity_probability = float(abs(c00) ** 2 + abs(c11) ** 2)
    return ParticleCreationFLRWBenchmark(
        final_statevector=tuple(complex(component) for component in full_statevector),
        scale_factor_edges=tuple(
            float(value) for value in scale_factor_edges(parameters).tolist()
        ),
        mode_frequency_edges=tuple(
            float(value) for value in mode_frequency_edges(parameters).tolist()
        ),
        slices=evolution_slices(parameters),
        single_mode_particle_number_expectation=single_mode_particle_number,
        total_particle_number_expectation=total_particle_number,
        pairing_correlator_expectation=pairing_correlator,
        pair_occupation_probability=pair_probability,
        even_parity_probability=even_parity_probability,
    )


def benchmark_to_serializable(
    experiment: ParticleCreationFLRWExperiment,
    benchmark: ParticleCreationFLRWBenchmark,
) -> dict[str, object]:
    """Convert benchmark data into a serializable record."""

    return {
        "experiment_name": experiment.configuration.experiment_name,
        "scientific_question": experiment.configuration.scientific_question,
        "parameters": dict(experiment.configuration.parameters),
        "truncation": dict(experiment.configuration.truncation),
        "benchmark": {
            "final_statevector": [
                _complex_record(value) for value in benchmark.final_statevector
            ],
            "scale_factor_edges": list(benchmark.scale_factor_edges),
            "mode_frequency_edges": list(benchmark.mode_frequency_edges),
            "single_mode_particle_number_expectation": (
                benchmark.single_mode_particle_number_expectation
            ),
            "total_particle_number_expectation": (
                benchmark.total_particle_number_expectation
            ),
            "pairing_correlator_expectation": benchmark.pairing_correlator_expectation,
            "pair_occupation_probability": benchmark.pair_occupation_probability,
            "even_parity_probability": benchmark.even_parity_probability,
            "slices": [
                {
                    "index": evolution_slice.index,
                    "scale_factor_start": evolution_slice.scale_factor_start,
                    "scale_factor_end": evolution_slice.scale_factor_end,
                    "mode_frequency_start": evolution_slice.mode_frequency_start,
                    "mode_frequency_end": evolution_slice.mode_frequency_end,
                    "midpoint_frequency": evolution_slice.midpoint_frequency,
                    "phase_angle": evolution_slice.phase_angle,
                    "squeezing_angle": evolution_slice.squeezing_angle,
                }
                for evolution_slice in benchmark.slices
            ],
        },
    }


def write_benchmark_json(
    experiment: ParticleCreationFLRWExperiment,
    benchmark: ParticleCreationFLRWBenchmark,
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
    benchmark: ParticleCreationFLRWBenchmark,
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
                    f"{tier_label} comparison against the exact discrete "
                    "particle-creation benchmark."
                ),
            )
        )
    return comparison_records


def comparison_records_for_result(
    result,
    benchmark: ParticleCreationFLRWBenchmark,
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
        description="Compute the direct benchmark for the reduced FLRW particle-creation toy model."
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
