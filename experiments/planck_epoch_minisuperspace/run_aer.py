"""Noisy local execution for the Planck-epoch-motivated minisuperspace model."""

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
    EstimatorExecutionResult,
    ExecutionProvenance,
    write_execution_result_json,
)
from qclab.backends.base import ExecutionTier, validate_execution_progression
from qclab.observables import ObservableEvaluation
from qclab.utils.optional import require_dependency
from qclab.utils.runtime import aer_execution_guard_message, is_aer_execution_guard_required

from experiments.minisuperspace_frw.run_aer import run_noisy_local as _run_noisy_local
from experiments.planck_epoch_minisuperspace.benchmark import (
    comparison_records_for_evaluations,
    compute_benchmark,
    write_benchmark_json,
)
from experiments.planck_epoch_minisuperspace.circuit import build_ground_state_circuit
from experiments.planck_epoch_minisuperspace.common import (
    DEFAULT_CONFIG_PATH,
    default_backend_request_kwargs,
    load_experiment_definition,
)
from experiments.planck_epoch_minisuperspace.observables import build_observables


def _readout_attenuation(pauli_label: str, readout_error_probability: float) -> float:
    """Return the symmetric readout-error attenuation for one Pauli term."""

    pauli_weight = sum(symbol != "I" for symbol in pauli_label)
    return (1.0 - 2.0 * readout_error_probability) ** pauli_weight


def _analytic_readout_fallback_result(
    experiment,
) -> EstimatorExecutionResult:
    """Construct a host-safe noisy-local result when Aer execution is guarded.

    This fallback is used only when the declared Aer gate-noise model is inactive
    for the generated state-preparation circuit. In the current experiment, the
    decomposed circuit contains no ``ry`` instructions, so the configured
    one-qubit depolarizing noise attached to ``ry`` gates is not applied. The
    remaining declared noisy-local effect is symmetric readout error, which can
    be modeled exactly by attenuating each measured Pauli term by
    ``(1 - 2 p)^w`` where ``w`` is the Pauli weight.
    """

    quantum_info = require_dependency(
        "qiskit.quantum_info",
        "evaluate the host-safe readout-error fallback for the noisy local tier",
    )
    circuit = build_ground_state_circuit(experiment.parameters)
    ry_gate_count = int(circuit.count_ops().get("ry", 0))
    if ry_gate_count != 0:
        raise RuntimeError(
            "The analytic noisy-local fallback is only valid when the declared "
            "Aer gate-noise component is inactive because the prepared circuit "
            "contains no ry instructions."
        )

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
            "inactive_gate_noise_model": {
                "gate": "ry",
                "one_qubit_depolarizing_probability": (
                    experiment.noise_model.one_qubit_depolarizing_probability
                ),
                "observed_ry_gate_count": ry_gate_count,
            },
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
                "inactive_gate_noise_model": {
                    "gate": "ry",
                    "one_qubit_depolarizing_probability": (
                        experiment.noise_model.one_qubit_depolarizing_probability
                    ),
                    "observed_ry_gate_count": ry_gate_count,
                },
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

    if not is_aer_execution_guard_required():
        return _run_noisy_local(config_path)

    result = _analytic_readout_fallback_result(experiment)
    comparison_records = comparison_records_for_evaluations(
        result.evaluations,
        benchmark,
        tier_label="Noisy local analytic fallback",
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
            "Run the noisy local Planck-epoch-motivated reduced minisuperspace workflow."
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
