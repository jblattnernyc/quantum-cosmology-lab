"""Independent matrix validation for the reduced FLRW particle-creation model.

This module intentionally does not use the experiment's evolution, circuit, or
observable-construction helpers. It reconstructs the declared model directly
as four-dimensional matrices and evaluates every exponential with SciPy.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import json
import math
from pathlib import Path
import platform
import sys
from typing import Any, Mapping

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from qclab.utils.paths import repository_relative_path
from qclab.validation import (
    ArtifactLineageStatus,
    HardwareValidationGateError,
    TierAssessment,
    ValidationContext,
    classify_artifact_lineage,
    computed_payloads_equivalent,
)

from experiments.particle_creation_flrw.common import (
    DEFAULT_CONFIG_PATH,
    ParticleCreationFLRWExperiment,
    ParticleCreationFLRWParameters,
    load_experiment_definition,
    validation_configuration_for_experiment,
)


INDEPENDENT_TIER = "independent_benchmark"
OBSERVABLE_NAMES = (
    "single_mode_particle_number_expectation",
    "total_particle_number_expectation",
    "pairing_correlator_expectation",
)

_IDENTITY_2 = np.eye(2, dtype=complex)
_PAULI_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
_PAULI_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
_PAULI_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
_IDENTITY_4 = np.eye(4, dtype=complex)
_IZ = np.kron(_IDENTITY_2, _PAULI_Z)
_ZI = np.kron(_PAULI_Z, _IDENTITY_2)
_XX = np.kron(_PAULI_X, _PAULI_X)
_YY = np.kron(_PAULI_Y, _PAULI_Y)
_PHASE_GENERATOR = -0.5 * (_IZ + _ZI)
_PAIRING_GENERATOR = 0.5 * (_XX - _YY)
_VACUUM_STATE = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)


@dataclass(frozen=True)
class IndependentValidationPolicy:
    """Declared numerical acceptance policy for independent validation."""

    statevector_tolerance: float
    observable_tolerance: float
    normalization_tolerance: float
    parity_tolerance: float
    convergence_time_steps: tuple[int, ...]
    maximum_final_observable_error: float
    maximum_final_state_infidelity: float
    minimum_final_observable_convergence_order: float
    require_monotone_observable_error: bool
    continuum_method: str
    continuum_relative_tolerance: float
    continuum_absolute_tolerance: float

    def __post_init__(self) -> None:
        nonnegative = {
            "statevector_tolerance": self.statevector_tolerance,
            "observable_tolerance": self.observable_tolerance,
            "normalization_tolerance": self.normalization_tolerance,
            "parity_tolerance": self.parity_tolerance,
            "maximum_final_observable_error": self.maximum_final_observable_error,
            "maximum_final_state_infidelity": self.maximum_final_state_infidelity,
            "minimum_final_observable_convergence_order": (
                self.minimum_final_observable_convergence_order
            ),
        }
        for name, value in nonnegative.items():
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and non-negative.")
        if len(self.convergence_time_steps) < 2:
            raise ValueError("At least two convergence time-step counts are required.")
        if any(value <= 0 for value in self.convergence_time_steps):
            raise ValueError("Convergence time-step counts must be positive.")
        if any(
            current <= previous
            for previous, current in zip(
                self.convergence_time_steps,
                self.convergence_time_steps[1:],
            )
        ):
            raise ValueError(
                "Convergence time-step counts must be strictly increasing."
            )
        if not self.continuum_method:
            raise ValueError("A continuum-reference solver method is required.")
        if self.continuum_relative_tolerance <= 0.0:
            raise ValueError("Continuum relative tolerance must be positive.")
        if self.continuum_absolute_tolerance <= 0.0:
            raise ValueError("Continuum absolute tolerance must be positive.")

    def to_serializable(self) -> dict[str, Any]:
        """Return the policy as a JSON-safe mapping."""

        return {
            "statevector_tolerance": self.statevector_tolerance,
            "observable_tolerance": self.observable_tolerance,
            "normalization_tolerance": self.normalization_tolerance,
            "parity_tolerance": self.parity_tolerance,
            "convergence_time_steps": list(self.convergence_time_steps),
            "maximum_final_observable_error": (self.maximum_final_observable_error),
            "maximum_final_state_infidelity": self.maximum_final_state_infidelity,
            "minimum_final_observable_convergence_order": (
                self.minimum_final_observable_convergence_order
            ),
            "require_monotone_observable_error": (
                self.require_monotone_observable_error
            ),
            "continuum_reference": {
                "method": self.continuum_method,
                "relative_tolerance": self.continuum_relative_tolerance,
                "absolute_tolerance": self.continuum_absolute_tolerance,
            },
        }


@dataclass(frozen=True)
class ConvergenceRecord:
    """One discrete refinement result relative to the continuum interpolant."""

    time_steps: int
    observables: dict[str, float]
    maximum_observable_absolute_error: float
    state_infidelity: float
    phase_aligned_maximum_amplitude_error: float
    observable_convergence_order: float | None

    def to_serializable(self) -> dict[str, Any]:
        """Return the refinement record as a JSON-safe mapping."""

        return {
            "time_steps": self.time_steps,
            "observables": dict(self.observables),
            "maximum_observable_absolute_error": (
                self.maximum_observable_absolute_error
            ),
            "state_infidelity": self.state_infidelity,
            "phase_aligned_maximum_amplitude_error": (
                self.phase_aligned_maximum_amplitude_error
            ),
            "observable_convergence_order": self.observable_convergence_order,
        }


@dataclass(frozen=True)
class IndependentValidationAssessment:
    """Numerical checks governing the independent validation result."""

    passed: bool
    checks: dict[str, bool]
    metrics: dict[str, float | bool]
    errors: tuple[str, ...] = ()
    schema_version: int = 1

    def to_serializable(self) -> dict[str, Any]:
        """Return the assessment as a JSON-safe mapping."""

        return {
            "schema_version": self.schema_version,
            "tier": INDEPENDENT_TIER,
            "passed": self.passed,
            "checks": dict(self.checks),
            "metrics": dict(self.metrics),
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class IndependentValidationResult:
    """Complete independently computed benchmark and refinement evidence."""

    official_reference_statevector: tuple[complex, ...]
    official_reference_observables: dict[str, float]
    independent_statevector: tuple[complex, ...]
    independent_observables: dict[str, float]
    continuum_reference_statevector: tuple[complex, ...]
    continuum_reference_observables: dict[str, float]
    convergence_records: tuple[ConvergenceRecord, ...]
    assessment: IndependentValidationAssessment


def independent_validation_policy(
    experiment: ParticleCreationFLRWExperiment,
) -> IndependentValidationPolicy:
    """Load and validate the independent-benchmark policy."""

    validation = validation_configuration_for_experiment(experiment)
    raw_policy = validation.get(INDEPENDENT_TIER)
    if not isinstance(raw_policy, Mapping):
        raise ValueError(
            "The particle-creation experiment requires an independent_benchmark "
            "validation policy."
        )
    continuum = raw_policy.get("continuum_reference")
    if not isinstance(continuum, Mapping):
        raise ValueError(
            "The independent benchmark policy requires continuum_reference settings."
        )
    raw_steps = raw_policy.get("convergence_time_steps")
    if not isinstance(raw_steps, (list, tuple)):
        raise ValueError("convergence_time_steps must be a sequence.")
    return IndependentValidationPolicy(
        statevector_tolerance=float(raw_policy["statevector_tolerance"]),
        observable_tolerance=float(raw_policy["observable_tolerance"]),
        normalization_tolerance=float(raw_policy["normalization_tolerance"]),
        parity_tolerance=float(raw_policy["parity_tolerance"]),
        convergence_time_steps=tuple(int(value) for value in raw_steps),
        maximum_final_observable_error=float(
            raw_policy["maximum_final_observable_error"]
        ),
        maximum_final_state_infidelity=float(
            raw_policy["maximum_final_state_infidelity"]
        ),
        minimum_final_observable_convergence_order=float(
            raw_policy["minimum_final_observable_convergence_order"]
        ),
        require_monotone_observable_error=bool(
            raw_policy["require_monotone_observable_error"]
        ),
        continuum_method=str(continuum["method"]),
        continuum_relative_tolerance=float(continuum["relative_tolerance"]),
        continuum_absolute_tolerance=float(continuum["absolute_tolerance"]),
    )


def independent_operator_matrices() -> dict[str, np.ndarray]:
    """Return independent copies of all generators and observables."""

    return {
        "phase_generator": _PHASE_GENERATOR.copy(),
        "pairing_generator": _PAIRING_GENERATOR.copy(),
        "single_mode_particle_number_expectation": (0.5 * (_IDENTITY_4 - _IZ)).copy(),
        "total_particle_number_expectation": (_IDENTITY_4 - 0.5 * (_IZ + _ZI)).copy(),
        "pairing_correlator_expectation": _PAIRING_GENERATOR.copy(),
    }


def independent_slice_unitary(phase_angle: float, squeezing_angle: float) -> np.ndarray:
    """Return one phase-then-pairing slice as an explicit matrix exponential."""

    phase_unitary = expm(-1.0j * phase_angle * _PHASE_GENERATOR)
    pairing_unitary = expm(-1.0j * squeezing_angle * _PAIRING_GENERATOR)
    return pairing_unitary @ phase_unitary


def independent_discrete_state(
    parameters: ParticleCreationFLRWParameters,
) -> np.ndarray:
    """Evolve the vacuum without using experiment evolution or circuit helpers."""

    scale_factors = np.linspace(
        parameters.scale_factor_initial,
        parameters.scale_factor_final,
        parameters.time_steps + 1,
        dtype=float,
    )
    frequencies = np.sqrt(
        parameters.comoving_momentum**2 + (parameters.mass * scale_factors) ** 2
    )
    state = _VACUUM_STATE.copy()
    for index in range(parameters.time_steps):
        frequency_start = float(frequencies[index])
        frequency_end = float(frequencies[index + 1])
        phase_angle = (
            0.5
            * (frequency_start + frequency_end)
            * (parameters.time_extent / parameters.time_steps)
        )
        squeezing_angle = 0.5 * math.log(frequency_end / frequency_start)
        state = independent_slice_unitary(phase_angle, squeezing_angle) @ state
    return state


def independent_observable_values(statevector: np.ndarray) -> dict[str, float]:
    """Evaluate independently constructed observable matrices."""

    state = np.asarray(statevector, dtype=complex).reshape(4)
    matrices = independent_operator_matrices()
    return {
        name: float(np.vdot(state, matrices[name] @ state).real)
        for name in OBSERVABLE_NAMES
    }


def continuum_reference_state(
    parameters: ParticleCreationFLRWParameters,
    policy: IndependentValidationPolicy,
) -> np.ndarray:
    """Solve the explicitly added continuous interpolation of the toy model."""

    scale_factor_slope = (
        parameters.scale_factor_final - parameters.scale_factor_initial
    ) / parameters.time_extent

    def derivative(conformal_time: float, state: np.ndarray) -> np.ndarray:
        scale_factor = (
            parameters.scale_factor_initial + scale_factor_slope * conformal_time
        )
        frequency_squared = (
            parameters.comoving_momentum**2 + (parameters.mass * scale_factor) ** 2
        )
        frequency = math.sqrt(frequency_squared)
        squeezing_rate = (
            parameters.mass**2
            * scale_factor
            * scale_factor_slope
            / (2.0 * frequency_squared)
        )
        hamiltonian = frequency * _PHASE_GENERATOR + squeezing_rate * _PAIRING_GENERATOR
        return -1.0j * hamiltonian @ state

    solution = solve_ivp(
        derivative,
        (0.0, parameters.time_extent),
        _VACUUM_STATE,
        method=policy.continuum_method,
        rtol=policy.continuum_relative_tolerance,
        atol=policy.continuum_absolute_tolerance,
        t_eval=(parameters.time_extent,),
    )
    if not solution.success:
        raise RuntimeError(
            "The independent continuum-reference integration failed: "
            f"{solution.message}"
        )
    return np.asarray(solution.y[:, -1], dtype=complex)


def _state_comparison(
    candidate_statevector: np.ndarray,
    reference_statevector: np.ndarray,
) -> tuple[float, float]:
    """Return phase-insensitive infidelity and phase-aligned maximum error."""

    candidate = np.asarray(candidate_statevector, dtype=complex).reshape(4)
    reference = np.asarray(reference_statevector, dtype=complex).reshape(4)
    candidate_norm = float(np.linalg.norm(candidate))
    reference_norm = float(np.linalg.norm(reference))
    if candidate_norm == 0.0 or reference_norm == 0.0:
        raise ValueError("Statevector comparisons require nonzero states.")
    candidate_normalized = candidate / candidate_norm
    reference_normalized = reference / reference_norm
    overlap = np.vdot(reference_normalized, candidate_normalized)
    fidelity = min(1.0, float(abs(overlap) ** 2))
    aligned_candidate = candidate_normalized * np.exp(-1.0j * np.angle(overlap))
    maximum_error = float(np.max(np.abs(aligned_candidate - reference_normalized)))
    return max(0.0, 1.0 - fidelity), maximum_error


def _maximum_observable_error(
    candidate: Mapping[str, float],
    reference: Mapping[str, float],
) -> float:
    """Return the largest absolute observable deviation."""

    return max(
        abs(float(candidate[name]) - float(reference[name]))
        for name in OBSERVABLE_NAMES
    )


def _convergence_records(
    parameters: ParticleCreationFLRWParameters,
    policy: IndependentValidationPolicy,
    continuum_statevector: np.ndarray,
) -> tuple[ConvergenceRecord, ...]:
    """Build the declared refinement sequence against the continuum interpolant."""

    continuum_observables = independent_observable_values(continuum_statevector)
    records: list[ConvergenceRecord] = []
    previous_error: float | None = None
    previous_steps: int | None = None
    for time_steps in policy.convergence_time_steps:
        refined_parameters = replace(parameters, time_steps=time_steps)
        statevector = independent_discrete_state(refined_parameters)
        observables = independent_observable_values(statevector)
        maximum_error = _maximum_observable_error(
            observables,
            continuum_observables,
        )
        state_infidelity, maximum_amplitude_error = _state_comparison(
            statevector,
            continuum_statevector,
        )
        convergence_order = None
        if (
            previous_error is not None
            and previous_steps is not None
            and maximum_error > 0.0
            and previous_error > 0.0
        ):
            convergence_order = math.log(previous_error / maximum_error) / math.log(
                time_steps / previous_steps
            )
        records.append(
            ConvergenceRecord(
                time_steps=time_steps,
                observables=observables,
                maximum_observable_absolute_error=maximum_error,
                state_infidelity=state_infidelity,
                phase_aligned_maximum_amplitude_error=maximum_amplitude_error,
                observable_convergence_order=convergence_order,
            )
        )
        previous_error = maximum_error
        previous_steps = time_steps
    return tuple(records)


def compute_independent_validation(
    parameters: ParticleCreationFLRWParameters,
    official_reference_statevector: tuple[complex, ...] | np.ndarray,
    official_reference_observables: Mapping[str, float],
    policy: IndependentValidationPolicy,
) -> IndependentValidationResult:
    """Compute independent discrete reproduction and continuum refinement tests."""

    official_state = np.asarray(official_reference_statevector, dtype=complex).reshape(
        4
    )
    official_observables = {
        name: float(official_reference_observables[name]) for name in OBSERVABLE_NAMES
    }
    independent_state = independent_discrete_state(parameters)
    independent_observables = independent_observable_values(independent_state)
    continuum_state = continuum_reference_state(parameters, policy)
    continuum_observables = independent_observable_values(continuum_state)
    convergence_records = _convergence_records(
        parameters,
        policy,
        continuum_state,
    )

    official_infidelity, official_amplitude_error = _state_comparison(
        independent_state,
        official_state,
    )
    official_observable_error = _maximum_observable_error(
        independent_observables,
        official_observables,
    )
    normalization_error = abs(
        float(np.vdot(independent_state, independent_state).real) - 1.0
    )
    continuum_normalization_error = abs(
        float(np.vdot(continuum_state, continuum_state).real) - 1.0
    )
    odd_parity_probability = float(
        abs(independent_state[1]) ** 2 + abs(independent_state[2]) ** 2
    )
    even_parity_probability = float(
        abs(independent_state[0]) ** 2 + abs(independent_state[3]) ** 2
    )
    monotone_observable_error = all(
        current.maximum_observable_absolute_error
        < previous.maximum_observable_absolute_error
        for previous, current in zip(
            convergence_records,
            convergence_records[1:],
        )
    )
    final_record = convergence_records[-1]
    final_order = final_record.observable_convergence_order

    checks = {
        "official_state_infidelity": official_infidelity
        <= policy.statevector_tolerance,
        "official_phase_aligned_amplitude_error": official_amplitude_error
        <= policy.statevector_tolerance,
        "official_observable_error": official_observable_error
        <= policy.observable_tolerance,
        "independent_normalization": normalization_error
        <= policy.normalization_tolerance,
        "continuum_reference_normalization": continuum_normalization_error
        <= policy.normalization_tolerance,
        "odd_parity_suppression": odd_parity_probability <= policy.parity_tolerance,
        "even_parity_preservation": abs(even_parity_probability - 1.0)
        <= policy.parity_tolerance,
        "monotone_observable_refinement": (
            monotone_observable_error
            if policy.require_monotone_observable_error
            else True
        ),
        "final_observable_refinement_error": (
            final_record.maximum_observable_absolute_error
            <= policy.maximum_final_observable_error
        ),
        "final_state_refinement_infidelity": (
            final_record.state_infidelity <= policy.maximum_final_state_infidelity
        ),
        "final_observable_convergence_order": (
            final_order is not None
            and final_order >= policy.minimum_final_observable_convergence_order
        ),
    }
    errors = tuple(name for name, passed in checks.items() if not passed)
    assessment = IndependentValidationAssessment(
        passed=not errors,
        checks=checks,
        metrics={
            "official_state_infidelity": official_infidelity,
            "official_phase_aligned_maximum_amplitude_error": (
                official_amplitude_error
            ),
            "official_maximum_observable_absolute_error": (official_observable_error),
            "independent_normalization_error": normalization_error,
            "continuum_reference_normalization_error": (continuum_normalization_error),
            "odd_parity_probability": odd_parity_probability,
            "even_parity_probability": even_parity_probability,
            "monotone_observable_error": monotone_observable_error,
            "final_maximum_observable_absolute_error": (
                final_record.maximum_observable_absolute_error
            ),
            "final_state_infidelity": final_record.state_infidelity,
            "final_observable_convergence_order": (
                0.0 if final_order is None else final_order
            ),
        },
        errors=errors,
    )
    return IndependentValidationResult(
        official_reference_statevector=tuple(
            complex(value) for value in official_state
        ),
        official_reference_observables=official_observables,
        independent_statevector=tuple(complex(value) for value in independent_state),
        independent_observables=independent_observables,
        continuum_reference_statevector=tuple(
            complex(value) for value in continuum_state
        ),
        continuum_reference_observables=continuum_observables,
        convergence_records=convergence_records,
        assessment=assessment,
    )


def _complex_record(value: complex) -> dict[str, float]:
    """Return a JSON-safe complex scalar."""

    return {"real": float(value.real), "imag": float(value.imag)}


def independent_validation_to_serializable(
    experiment: ParticleCreationFLRWExperiment,
    result: IndependentValidationResult,
    policy: IndependentValidationPolicy,
    validation_context: ValidationContext,
) -> dict[str, Any]:
    """Serialize independent validation evidence and scientific provenance."""

    return {
        "schema_version": 1,
        "experiment_name": experiment.configuration.experiment_name,
        "scientific_question": experiment.configuration.scientific_question,
        "parameters": dict(experiment.configuration.parameters),
        "truncation": dict(experiment.configuration.truncation),
        "method": {
            "basis_order": ["|00>", "|01>", "|10>", "|11>"],
            "phase_generator": "-(IZ + ZI) / 2",
            "pairing_generator": "(XX - YY) / 2",
            "slice_action_order": "phase_then_pairing",
            "slice_unitary": "U_pairing @ U_phase",
            "matrix_exponential": "scipy.linalg.expm",
            "shared_evolution_helpers_used": False,
            "continuum_interpolation_assumption": (
                "a(eta) is linear between the declared endpoints and the "
                "continuous Hamiltonian is omega(eta) G_phase + "
                "0.5 d(log omega)/deta G_pairing."
            ),
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "policy": policy.to_serializable(),
        "official_reference": {
            "statevector": [
                _complex_record(value)
                for value in result.official_reference_statevector
            ],
            "observables": dict(result.official_reference_observables),
        },
        "independent_discrete_result": {
            "statevector": [
                _complex_record(value) for value in result.independent_statevector
            ],
            "observables": dict(result.independent_observables),
        },
        "continuum_reference": {
            "status": "additional_interpolation_assumption",
            "statevector": [
                _complex_record(value)
                for value in result.continuum_reference_statevector
            ],
            "observables": dict(result.continuum_reference_observables),
        },
        "convergence": [
            record.to_serializable() for record in result.convergence_records
        ],
        "assessment": result.assessment.to_serializable(),
        "validation_context": validation_context.to_serializable(),
    }


def _write_convergence_table(
    result: IndependentValidationResult,
    output_path: Path,
) -> Path:
    """Write the refinement sequence as a Markdown table."""

    lines = [
        "# Particle-Creation FLRW Independent Convergence Summary",
        "",
        (
            "The continuum column is an added linear-interpolation reference for "
            "discretization analysis, not a continuum-exact FLRW field solution."
        ),
        "",
        "|Time steps|Single-mode number|Total number|Pairing correlator|Max. observable error|State infidelity|Observed order|",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for record in result.convergence_records:
        order = (
            "n/a"
            if record.observable_convergence_order is None
            else f"{record.observable_convergence_order:.6f}"
        )
        lines.append(
            "|"
            f"{record.time_steps}|"
            f"{record.observables[OBSERVABLE_NAMES[0]]:.12f}|"
            f"{record.observables[OBSERVABLE_NAMES[1]]:.12f}|"
            f"{record.observables[OBSERVABLE_NAMES[2]]:.12f}|"
            f"{record.maximum_observable_absolute_error:.6e}|"
            f"{record.state_infidelity:.6e}|"
            f"{order}|"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def _write_independent_report(
    experiment: ParticleCreationFLRWExperiment,
    result: IndependentValidationResult,
    json_path: Path,
    table_path: Path,
    output_path: Path,
) -> Path:
    """Write the independent validation report."""

    assessment = result.assessment
    lines = [
        "# Particle-Creation FLRW Independent Validation Report",
        "",
        f"Overall result: **{'PASS' if assessment.passed else 'FAIL'}**",
        "",
        "## Independent discrete reproduction",
        "",
        (
            "The declared two-qubit model was reconstructed with explicit 4 x 4 "
            "matrices and SciPy matrix exponentials. No experiment evolution, "
            "circuit-construction, or observable-construction helper was used."
        ),
        "",
        (
            "- Official-state infidelity: "
            f"{assessment.metrics['official_state_infidelity']:.6e}"
        ),
        (
            "- Phase-aligned maximum amplitude error: "
            f"{assessment.metrics['official_phase_aligned_maximum_amplitude_error']:.6e}"
        ),
        (
            "- Maximum observable absolute error: "
            f"{assessment.metrics['official_maximum_observable_absolute_error']:.6e}"
        ),
        (
            "- Odd-parity probability: "
            f"{assessment.metrics['odd_parity_probability']:.6e}"
        ),
        "",
        "## Refinement study",
        "",
        (
            "The refinement study compares the discrete ordered product with an "
            "ODE obtained by linearly interpolating the prescribed scale factor. "
            "This is an added discretization diagnostic; it is not a claim of a "
            "continuum-exact quantum field calculation."
        ),
        "",
        (
            "- Final maximum observable error: "
            f"{assessment.metrics['final_maximum_observable_absolute_error']:.6e}"
        ),
        (
            "- Final state infidelity: "
            f"{assessment.metrics['final_state_infidelity']:.6e}"
        ),
        (
            "- Final observed convergence order: "
            f"{assessment.metrics['final_observable_convergence_order']:.6f}"
        ),
        "",
        "## Interpretation",
        "",
        (
            "Passing independent reproduction corroborates the implementation of "
            "the declared finite-dimensional discrete model. It does not validate "
            "the single-pair truncation as a complete curved-spacetime field theory."
        ),
        (
            "The refinement sequence quantifies sensitivity to the number of time "
            "slices and should be considered separately from backend noise."
        ),
        "",
        f"Experiment: `{experiment.configuration.experiment_name}`",
        f"JSON evidence: `{repository_relative_path(json_path)}`",
        f"Convergence table: `{repository_relative_path(table_path)}`",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def write_independent_validation_artifacts(
    experiment: ParticleCreationFLRWExperiment,
    result: IndependentValidationResult,
    policy: IndependentValidationPolicy,
    validation_context: ValidationContext,
    *,
    json_path: str | Path | None = None,
    report_path: str | Path | None = None,
    table_path: str | Path | None = None,
) -> dict[str, Path]:
    """Write independent JSON evidence, report, and convergence table."""

    resolved_json = (
        experiment.artifacts.independent_validation_json
        if json_path is None
        else Path(json_path).expanduser().resolve()
    )
    resolved_report = (
        experiment.artifacts.independent_validation_report_markdown
        if report_path is None
        else Path(report_path).expanduser().resolve()
    )
    resolved_table = (
        experiment.artifacts.convergence_summary_table_markdown
        if table_path is None
        else Path(table_path).expanduser().resolve()
    )
    resolved_json.parent.mkdir(parents=True, exist_ok=True)
    resolved_json.write_text(
        json.dumps(
            independent_validation_to_serializable(
                experiment,
                result,
                policy,
                validation_context,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    _write_convergence_table(result, resolved_table)
    _write_independent_report(
        experiment,
        result,
        resolved_json,
        resolved_table,
        resolved_report,
    )
    return {
        "independent_validation_json": resolved_json,
        "independent_validation_report_markdown": resolved_report,
        "convergence_summary_table_markdown": resolved_table,
    }


def independent_validation_record(
    experiment: ParticleCreationFLRWExperiment,
    benchmark: Any,
    validation_context: ValidationContext,
) -> tuple[dict[str, Any], TierAssessment]:
    """Recompute and classify persisted independent validation evidence."""

    path = experiment.artifacts.independent_validation_json
    if not path.is_file():
        assessment = TierAssessment(
            tier=INDEPENDENT_TIER,
            lineage_id=validation_context.lineage_id,
            passed=False,
            observables=(),
            errors=(f"Independent validation artifact does not exist: {path}",),
        )
        return (
            {
                "lineage_status": "missing",
                "lineage_reason": assessment.errors[0],
                "stored_result_matches": False,
                "assessment": assessment.to_serializable(),
            },
            assessment,
        )

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HardwareValidationGateError(
            f"Independent validation artifact is not readable JSON: {path}"
        ) from exc
    if not isinstance(payload, dict):
        raise HardwareValidationGateError(
            "Independent validation artifact must contain a JSON object."
        )
    lineage = classify_artifact_lineage(payload, validation_context)
    policy = independent_validation_policy(experiment)
    recomputed = compute_independent_validation(
        experiment.parameters,
        benchmark.final_statevector,
        benchmark.expected_observable_values(),
        policy,
    )
    expected_payload = independent_validation_to_serializable(
        experiment,
        recomputed,
        policy,
        validation_context,
    )
    exact_keys = (
        "experiment_name",
        "parameters",
        "truncation",
        "method",
        "policy",
    )
    computed_keys = (
        "official_reference",
        "independent_discrete_result",
        "continuum_reference",
        "convergence",
        "assessment",
    )
    comparison_absolute_tolerance = max(
        policy.statevector_tolerance,
        policy.observable_tolerance,
        policy.normalization_tolerance,
        policy.continuum_absolute_tolerance,
    )
    stored_result_matches = all(
        payload.get(key) == expected_payload[key] for key in exact_keys
    ) and all(
        computed_payloads_equivalent(
            payload.get(key),
            expected_payload[key],
            absolute_tolerance=comparison_absolute_tolerance,
            relative_tolerance=policy.continuum_relative_tolerance,
        )
        for key in computed_keys
    )
    errors: list[str] = []
    if lineage.status is not ArtifactLineageStatus.CURRENT:
        errors.append(lineage.reason or "Independent artifact lineage is not current.")
    if not stored_result_matches:
        errors.append(
            "Stored independent validation content does not match fresh computation."
        )
    if not recomputed.assessment.passed:
        errors.extend(recomputed.assessment.errors)
    assessment = TierAssessment(
        tier=INDEPENDENT_TIER,
        lineage_id=validation_context.lineage_id,
        passed=not errors,
        observables=(),
        errors=tuple(errors),
    )
    return (
        {
            "lineage_status": lineage.status.value,
            "lineage_reason": lineage.reason,
            "stored_result_matches": stored_result_matches,
            "recomputed_assessment": recomputed.assessment.to_serializable(),
            "assessment": assessment.to_serializable(),
            "artifact_path": repository_relative_path(path),
        },
        assessment,
    )


def require_independent_validation_artifact(
    experiment: ParticleCreationFLRWExperiment,
    benchmark: Any,
    validation_context: ValidationContext,
) -> TierAssessment:
    """Require current, reproducible, passing independent evidence."""

    record, assessment = independent_validation_record(
        experiment,
        benchmark,
        validation_context,
    )
    if not assessment.passed:
        reason = "; ".join(assessment.errors) or "unknown independent validation error"
        raise HardwareValidationGateError(
            f"Independent benchmark prerequisite failed: {reason}"
        )
    if record["lineage_status"] != ArtifactLineageStatus.CURRENT.value:
        raise HardwareValidationGateError(
            "Independent benchmark artifact lineage does not match the current configuration."
        )
    return assessment


def main(argv: list[str] | None = None) -> int:
    """Compute and persist independent validation evidence."""

    parser = argparse.ArgumentParser(
        description=(
            "Independently validate the reduced FLRW particle-creation benchmark "
            "with explicit four-dimensional matrices."
        )
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--output", default=None)
    parser.add_argument("--report-output", default=None)
    parser.add_argument("--table-output", default=None)
    args = parser.parse_args(argv)

    from experiments.particle_creation_flrw.benchmark import (
        compute_benchmark,
        validation_context_for_benchmark,
    )

    experiment = load_experiment_definition(args.config)
    benchmark = compute_benchmark(experiment.parameters)
    validation_context = validation_context_for_benchmark(experiment, benchmark)
    policy = independent_validation_policy(experiment)
    result = compute_independent_validation(
        experiment.parameters,
        benchmark.final_statevector,
        benchmark.expected_observable_values(),
        policy,
    )
    outputs = write_independent_validation_artifacts(
        experiment,
        result,
        policy,
        validation_context,
        json_path=args.output,
        report_path=args.report_output,
        table_path=args.table_output,
    )
    print(f"independent_validation: {'PASS' if result.assessment.passed else 'FAIL'}")
    print(f"lineage_id: {validation_context.lineage_id}")
    for label, path in outputs.items():
        print(f"{label}: {path}")
    return 0 if result.assessment.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
