"""Noisy local execution for the Grand-Unification-Epoch-context toy model."""

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
    EstimatorExecutionResult,
    ExecutionProvenance,
    write_execution_result_json,
)
from qclab.backends.base import ExecutionTier, validate_execution_progression
from qclab.observables import ObservableEvaluation
from qclab.utils.optional import require_dependency
from qclab.utils.runtime import aer_execution_guard_message, is_aer_execution_guard_required

from experiments.grand_unification_epoch_toy.benchmark import (
    comparison_records_for_evaluations,
    comparison_records_for_result,
    compute_benchmark,
    write_benchmark_json,
)
from experiments.grand_unification_epoch_toy.circuit import build_ground_state_circuit
from experiments.grand_unification_epoch_toy.common import (
    DEFAULT_CONFIG_PATH,
    default_backend_request_kwargs,
    load_experiment_definition,
)
from experiments.grand_unification_epoch_toy.observables import build_observables


def _build_noise_model(experiment):
    """Construct the explicit Aer readout-noise model for the noisy tier."""

    aer_noise = require_dependency(
        "qiskit_aer.noise",
        "construct the Aer noise model for the Grand-Unification-Epoch toy experiment",
    )
    readout_probability = experiment.noise_model.readout_error_probability
    readout_error = aer_noise.ReadoutError(
        [
            [1.0 - readout_probability, readout_probability],
            [readout_probability, 1.0 - readout_probability],
        ]
    )
    noise_model = aer_noise.NoiseModel()
    noise_model.add_all_qubit_readout_error(readout_error)
    return noise_model


def _readout_attenuation(pauli_label: str, readout_error_probability: float) -> float:
    """Return the symmetric readout-error attenuation for one Pauli term."""

    pauli_weight = sum(symbol != "I" for symbol in pauli_label)
    return (1.0 - 2.0 * readout_error_probability) ** pauli_weight


def _analytic_readout_fallback_result(experiment) -> EstimatorExecutionResult:
    """Construct a host-safe noisy-local result for symmetric readout error."""

    quantum_info = require_dependency(
        "qiskit.quantum_info",
        "evaluate the analytic readout-error fallback for the noisy local tier",
    )
    circuit = build_ground_state_circuit(experiment.parameters)
    statevector = quantum_info.Statevector.from_instruction(circuit)
    sparse_pauli_op = quantum_info.SparsePauliOp
    readout_error_probability = experiment.noise_model.readout_error_probability

    configured_request_kwargs = default_backend_request_kwargs(
        experiment,
        ExecutionTier.NOISY_LOCAL,
    )
    request = BackendRequest(
        tier=ExecutionTier.NOISY_LOCAL,
        backend_name="analytic_readout_fallback",
        shots=configured_request_kwargs["shots"],
        seed=configured_request_kwargs["seed"],
        precision=configured_request_kwargs["precision"],
        optimization_level=configured_request_kwargs["optimization_level"],
        options={
            "configured_backend_name": configured_request_kwargs["backend_name"],
            "fallback_mode": "analytic_readout_error_model",
            "readout_error_probability": readout_error_probability,
            "fallback_reason": aer_execution_guard_message(
                "Noisy local Aer execution"
            ),
        },
    )

    evaluations = []
    for observable in build_observables(experiment.parameters):
        value = 0.0 + 0.0j
        for term in observable.pauli_terms:
            term_operator = sparse_pauli_op.from_list([(term.label, 1.0)])
            exact_term_value = complex(statevector.expectation_value(term_operator))
            value += (
                term.coefficient
                * _readout_attenuation(term.label, readout_error_probability)
                * exact_term_value
            )
        if abs(value.imag) > 1e-12:
            raise ValueError(
                "The analytic noisy-local fallback produced a non-negligible "
                "imaginary expectation value."
            )
        evaluations.append(
            ObservableEvaluation(
                observable=observable,
                value=float(value.real),
                uncertainty=0.0,
                shots=request.shots,
                metadata={
                    "backend_name": request.backend_name,
                    "tier": request.tier.value,
                    "fallback_mode": "analytic_readout_error_model",
                },
            )
        )

    return EstimatorExecutionResult(
        request=request,
        evaluations=tuple(evaluations),
        provenance=ExecutionProvenance(
            tier=request.tier,
            backend_name=request.backend_name,
            primitive_name="analytic_readout_error_model",
            shots=request.shots,
            seed=request.seed,
            precision=request.precision,
            optimization_level=request.optimization_level,
            metadata={
                "configured_backend_name": configured_request_kwargs["backend_name"],
                "fallback_mode": "analytic_readout_error_model",
                "readout_error_probability": readout_error_probability,
                "reason": aer_execution_guard_message("Noisy local Aer execution"),
            },
        ),
        raw_result=None,
        raw_job=None,
        raw_backend=None,
        job_metadata={},
    )


def run_noisy_local(config_path: str = str(DEFAULT_CONFIG_PATH)) -> dict[str, str]:
    """Execute the noisy local path and persist its outputs."""

    experiment = load_experiment_definition(config_path)
    validate_execution_progression(
        ExecutionTier.NOISY_LOCAL,
        benchmark_complete=True,
    )
    benchmark = compute_benchmark(experiment.parameters)
    write_benchmark_json(experiment, benchmark)

    if is_aer_execution_guard_required():
        result = _analytic_readout_fallback_result(experiment)
        comparison_records = comparison_records_for_evaluations(
            result.evaluations,
            benchmark,
            tier_label="Noisy local analytic fallback",
        )
    else:
        aer_module = require_dependency(
            "qiskit_aer",
            "run noisy local Aer simulations for the Grand-Unification-Epoch toy experiment",
        )
        noise_model = _build_noise_model(experiment)
        request_kwargs = default_backend_request_kwargs(
            experiment,
            ExecutionTier.NOISY_LOCAL,
        )
        request_kwargs["options"] = {
            "backend_options": {"method": experiment.noise_model.method},
            "noise_model_metadata": {
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
    """Run the noisy local workflow."""

    parser = argparse.ArgumentParser(
        description=(
            "Run the noisy local Grand-Unification-Epoch-context toy workflow."
        )
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    outputs = run_noisy_local(args.config)
    for label, path in outputs.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

