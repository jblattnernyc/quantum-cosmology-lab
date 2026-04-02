"""Noisy local Aer execution for the reduced FRW minisuperspace toy model."""

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
    AerEstimatorExecutor,
    BackendRequest,
    write_execution_result_json,
)
from qclab.backends.base import ExecutionTier, validate_execution_progression
from qclab.utils.optional import require_dependency

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


def _build_noise_model(experiment):
    """Construct the explicit Aer noise model for the official noisy tier."""

    aer_noise = require_dependency(
        "qiskit_aer.noise",
        "construct the Aer noise model for the minisuperspace FRW experiment",
    )
    noise_model = aer_noise.NoiseModel()
    one_qubit_error = aer_noise.depolarizing_error(
        experiment.noise_model.one_qubit_depolarizing_probability,
        1,
    )
    readout_probability = experiment.noise_model.readout_error_probability
    readout_error = aer_noise.ReadoutError(
        [
            [1.0 - readout_probability, readout_probability],
            [readout_probability, 1.0 - readout_probability],
        ]
    )
    noise_model.add_all_qubit_quantum_error(one_qubit_error, ["ry"])
    noise_model.add_all_qubit_readout_error(readout_error)
    return noise_model


def run_noisy_local(config_path: str = str(DEFAULT_CONFIG_PATH)) -> dict[str, str]:
    """Execute the explicit noisy local Aer path and persist its outputs."""

    experiment = load_experiment_definition(config_path)
    validate_execution_progression(
        ExecutionTier.NOISY_LOCAL,
        benchmark_complete=True,
    )
    benchmark = compute_benchmark(experiment.parameters)
    write_benchmark_json(experiment, benchmark)

    aer_module = require_dependency(
        "qiskit_aer",
        "run noisy local Aer simulations for the minisuperspace FRW experiment",
    )
    noise_model = _build_noise_model(experiment)

    request_kwargs = default_backend_request_kwargs(experiment, ExecutionTier.NOISY_LOCAL)
    request_kwargs["options"] = {
        "backend_options": {"method": experiment.noise_model.method},
        "noise_model_metadata": {
            "one_qubit_depolarizing_probability": (
                experiment.noise_model.one_qubit_depolarizing_probability
            ),
            "readout_error_probability": (
                experiment.noise_model.readout_error_probability
            ),
            "method": experiment.noise_model.method,
        },
    }
    request = BackendRequest(**request_kwargs)
    executor = AerEstimatorExecutor(
        backend_factory=lambda **kwargs: aer_module.AerSimulator(
            noise_model=noise_model,
            **kwargs,
        )
    )
    result = executor.run(
        build_ground_state_circuit(experiment.parameters),
        build_observables(experiment.parameters),
        request=request,
    )
    comparison_records = comparison_records_for_result(
        result,
        benchmark,
        tier_label="Noisy local Aer",
    )
    execution_path = write_execution_result_json(
        result,
        experiment.artifacts.noisy_local_json,
    )
    comparison_path = write_comparison_records_json(
        comparison_records,
        experiment.artifacts.noisy_local_comparisons_json,
    )
    return {
        "benchmark_json": str(experiment.artifacts.benchmark_json),
        "noisy_local_json": str(execution_path),
        "noisy_local_comparisons_json": str(comparison_path),
    }


def main(argv: list[str] | None = None) -> int:
    """Run the noisy local Aer workflow."""

    parser = argparse.ArgumentParser(
        description="Run the noisy local Aer reduced FRW minisuperspace workflow."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    outputs = run_noisy_local(args.config)
    for label, path in outputs.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
