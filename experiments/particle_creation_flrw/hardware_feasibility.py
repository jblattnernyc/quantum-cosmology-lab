"""Transpilation-only hardware-feasibility study for particle creation.

The study maps several time-slice discretizations to a fixed fake-backend ISA.
It never executes a circuit, creates a Runtime service, or submits a job.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import hashlib
from importlib.metadata import version
import json
import math
from pathlib import Path
import platform
from statistics import median
import sys
from typing import Any, Mapping

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from qclab.backends import instantiate_local_testing_backend
from qclab.backends.hardware import summarize_backend
from qclab.utils.optional import require_dependency
from qclab.utils.paths import repository_relative_path
from qclab.validation import ArtifactLineageStatus

from experiments.particle_creation_flrw.benchmark import (
    compute_benchmark,
    validation_context_for_benchmark,
)
from experiments.particle_creation_flrw.circuit import build_particle_creation_circuit
from experiments.particle_creation_flrw.common import (
    DEFAULT_CONFIG_PATH,
    ParticleCreationFLRWExperiment,
    load_experiment_definition,
)
from experiments.particle_creation_flrw.independent_benchmark import (
    require_independent_validation_artifact,
)


OFFICIAL_TRANSPILATION_GUIDE = "https://quantum.cloud.ibm.com/docs/en/guides/transpile"
OFFICIAL_OPTIMIZATION_GUIDE = (
    "https://quantum.cloud.ibm.com/docs/en/guides/set-optimization"
)


@dataclass(frozen=True)
class HardwareFeasibilityPolicy:
    """Configured scope for the exploratory transpilation study."""

    status: str
    backend_class: str
    time_steps: tuple[int, ...]
    transpiler_seeds: tuple[int, ...]
    optimization_level: int
    translation_method: str
    live_hardware_recommendation: str
    rationale: str

    def __post_init__(self) -> None:
        if self.status != "exploratory":
            raise ValueError("Hardware feasibility must remain exploratory.")
        if not self.backend_class:
            raise ValueError("A fake-backend class is required.")
        if not self.time_steps or any(value <= 0 for value in self.time_steps):
            raise ValueError("Hardware-feasibility time steps must be positive.")
        if len(set(self.time_steps)) != len(self.time_steps):
            raise ValueError("Hardware-feasibility time steps must be unique.")
        if any(
            current <= previous
            for previous, current in zip(self.time_steps, self.time_steps[1:])
        ):
            raise ValueError(
                "Hardware-feasibility time steps must be strictly increasing."
            )
        if not self.transpiler_seeds or any(
            value < 0 for value in self.transpiler_seeds
        ):
            raise ValueError("Transpiler seeds must be non-negative.")
        if len(set(self.transpiler_seeds)) != len(self.transpiler_seeds):
            raise ValueError("Transpiler seeds must be unique.")
        if self.optimization_level not in {0, 1, 2, 3}:
            raise ValueError("Optimization level must be one of {0, 1, 2, 3}.")
        if not self.translation_method:
            raise ValueError("A transpiler translation method is required.")
        if self.live_hardware_recommendation != "defer":
            raise ValueError("This exploratory study must defer live hardware.")

    def to_serializable(self) -> dict[str, Any]:
        """Return a JSON-safe policy record."""

        return {
            "status": self.status,
            "backend_class": self.backend_class,
            "time_steps": list(self.time_steps),
            "transpiler_seeds": list(self.transpiler_seeds),
            "optimization_level": self.optimization_level,
            "translation_method": self.translation_method,
            "live_hardware_recommendation": self.live_hardware_recommendation,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class TranspilationRecord:
    """Metrics for one time-step count and transpiler seed."""

    time_steps: int
    transpiler_seed: int
    logical_depth: int
    logical_size: int
    logical_operation_counts: dict[str, int]
    logical_two_qubit_gate_count: int
    transpiled_depth: int
    transpiled_size: int
    transpiled_operation_counts: dict[str, int]
    one_qubit_gate_count: int
    two_qubit_gate_count: int
    surviving_swap_count: int
    initial_layout: tuple[int, ...]
    final_layout: tuple[int, ...]
    initial_pair_adjacent: bool
    known_error_instruction_count: int
    unknown_error_instruction_count: int
    sum_instruction_duration_seconds: float
    aggregate_gate_error_proxy: float
    two_qubit_gate_error_proxy: float
    continuum_maximum_observable_error: float

    def to_serializable(self) -> dict[str, Any]:
        """Return the record as a JSON-safe mapping."""

        return {
            "time_steps": self.time_steps,
            "transpiler_seed": self.transpiler_seed,
            "logical_depth": self.logical_depth,
            "logical_size": self.logical_size,
            "logical_operation_counts": dict(self.logical_operation_counts),
            "logical_two_qubit_gate_count": self.logical_two_qubit_gate_count,
            "transpiled_depth": self.transpiled_depth,
            "transpiled_size": self.transpiled_size,
            "transpiled_operation_counts": dict(self.transpiled_operation_counts),
            "one_qubit_gate_count": self.one_qubit_gate_count,
            "two_qubit_gate_count": self.two_qubit_gate_count,
            "surviving_swap_count": self.surviving_swap_count,
            "initial_layout": list(self.initial_layout),
            "final_layout": list(self.final_layout),
            "initial_pair_adjacent": self.initial_pair_adjacent,
            "known_error_instruction_count": self.known_error_instruction_count,
            "unknown_error_instruction_count": self.unknown_error_instruction_count,
            "sum_instruction_duration_seconds": (self.sum_instruction_duration_seconds),
            "aggregate_gate_error_proxy": self.aggregate_gate_error_proxy,
            "two_qubit_gate_error_proxy": self.two_qubit_gate_error_proxy,
            "continuum_maximum_observable_error": (
                self.continuum_maximum_observable_error
            ),
        }


@dataclass(frozen=True)
class AggregateTranspilationRecord:
    """Seed-aggregated structural metrics for one discretization."""

    time_steps: int
    logical_depth: int
    logical_two_qubit_gate_count: int
    median_transpiled_depth: float
    minimum_transpiled_depth: int
    maximum_transpiled_depth: int
    median_two_qubit_gate_count: float
    minimum_two_qubit_gate_count: int
    maximum_two_qubit_gate_count: int
    maximum_surviving_swap_count: int
    unique_initial_layouts: tuple[tuple[int, ...], ...]
    all_initial_pairs_adjacent: bool
    median_aggregate_gate_error_proxy: float
    median_two_qubit_gate_error_proxy: float
    median_sum_instruction_duration_seconds: float
    continuum_maximum_observable_error: float

    def to_serializable(self) -> dict[str, Any]:
        """Return aggregate metrics as a JSON-safe mapping."""

        return {
            "time_steps": self.time_steps,
            "logical_depth": self.logical_depth,
            "logical_two_qubit_gate_count": self.logical_two_qubit_gate_count,
            "median_transpiled_depth": self.median_transpiled_depth,
            "minimum_transpiled_depth": self.minimum_transpiled_depth,
            "maximum_transpiled_depth": self.maximum_transpiled_depth,
            "median_two_qubit_gate_count": self.median_two_qubit_gate_count,
            "minimum_two_qubit_gate_count": self.minimum_two_qubit_gate_count,
            "maximum_two_qubit_gate_count": self.maximum_two_qubit_gate_count,
            "maximum_surviving_swap_count": self.maximum_surviving_swap_count,
            "unique_initial_layouts": [
                list(layout) for layout in self.unique_initial_layouts
            ],
            "all_initial_pairs_adjacent": self.all_initial_pairs_adjacent,
            "median_aggregate_gate_error_proxy": (
                self.median_aggregate_gate_error_proxy
            ),
            "median_two_qubit_gate_error_proxy": (
                self.median_two_qubit_gate_error_proxy
            ),
            "median_sum_instruction_duration_seconds": (
                self.median_sum_instruction_duration_seconds
            ),
            "continuum_maximum_observable_error": (
                self.continuum_maximum_observable_error
            ),
        }


@dataclass(frozen=True)
class HardwareFeasibilityStudy:
    """Complete transpilation-only feasibility evidence."""

    policy: HardwareFeasibilityPolicy
    backend_summary: dict[str, Any]
    records: tuple[TranspilationRecord, ...]
    aggregates: tuple[AggregateTranspilationRecord, ...]
    preferred_time_steps_by_hardware_cost: int
    validation_context: dict[str, Any]
    prerequisites: dict[str, Any]


def hardware_feasibility_policy(
    experiment: ParticleCreationFLRWExperiment,
) -> HardwareFeasibilityPolicy:
    """Load the exploratory study policy from experiment metadata."""

    raw_policy = experiment.configuration.metadata.get("hardware_feasibility")
    if not isinstance(raw_policy, Mapping):
        raise ValueError("config.yaml requires a hardware_feasibility mapping.")
    raw_time_steps = raw_policy.get("time_steps")
    raw_seeds = raw_policy.get("transpiler_seeds")
    if not isinstance(raw_time_steps, (list, tuple)):
        raise ValueError("hardware_feasibility.time_steps must be a sequence.")
    if not isinstance(raw_seeds, (list, tuple)):
        raise ValueError("hardware_feasibility.transpiler_seeds must be a sequence.")
    return HardwareFeasibilityPolicy(
        status=str(raw_policy["status"]),
        backend_class=str(raw_policy["backend_class"]),
        time_steps=tuple(int(value) for value in raw_time_steps),
        transpiler_seeds=tuple(int(value) for value in raw_seeds),
        optimization_level=int(raw_policy["optimization_level"]),
        translation_method=str(raw_policy["translation_method"]),
        live_hardware_recommendation=str(raw_policy["live_hardware_recommendation"]),
        rationale=str(raw_policy["rationale"]).strip(),
    )


def _operation_counts(circuit: Any) -> dict[str, int]:
    """Return sorted operation counts with plain integer values."""

    return {
        str(name): int(count) for name, count in sorted(circuit.count_ops().items())
    }


def _arity_gate_counts(circuit: Any) -> tuple[int, int]:
    """Return one- and two-qubit instruction counts."""

    one_qubit_count = 0
    two_qubit_count = 0
    for instruction in circuit.data:
        arity = len(instruction.qubits)
        if arity == 1:
            one_qubit_count += 1
        elif arity == 2:
            two_qubit_count += 1
    return one_qubit_count, two_qubit_count


def _layout_indices(circuit: Any, method_name: str) -> tuple[int, ...]:
    """Return filtered physical layout indices when Qiskit provides them."""

    layout = getattr(circuit, "layout", None)
    if layout is None:
        return ()
    method = getattr(layout, method_name, None)
    if not callable(method):
        return ()
    try:
        values = method(filter_ancillas=True)
    except TypeError:
        values = method()
    return tuple(int(value) for value in values)


def _initial_pair_adjacent(backend: Any, layout: tuple[int, ...]) -> bool:
    """Return whether the two logical qubits map to a calibrated two-qubit edge."""

    if len(layout) < 2:
        return False
    target = backend.target
    two_qubit_edges: set[tuple[int, int]] = set()
    for operation_name in backend.operation_names:
        try:
            qarg_properties = target[operation_name]
        except KeyError:
            continue
        for qargs in qarg_properties:
            if qargs is not None and len(qargs) == 2:
                two_qubit_edges.add(tuple(int(value) for value in qargs))
    pair = (layout[0], layout[1])
    return pair in two_qubit_edges or tuple(reversed(pair)) in two_qubit_edges


def _calibration_proxies(circuit: Any, backend: Any) -> dict[str, float | int]:
    """Accumulate simple independent-error and duration proxies.

    The proxy multiplies ``1 - instruction_error`` over calibrated operations.
    It omits measurement, idle errors, crosstalk, coherent accumulation, and
    mitigation, so it must not be interpreted as circuit fidelity.
    """

    all_gate_success_proxy = 1.0
    two_qubit_success_proxy = 1.0
    known_error_count = 0
    unknown_error_count = 0
    duration_sum = 0.0
    target = backend.target
    for instruction in circuit.data:
        operation_name = instruction.operation.name
        qargs = tuple(circuit.find_bit(qubit).index for qubit in instruction.qubits)
        try:
            properties = target[operation_name].get(qargs)
        except KeyError:
            properties = None
        error = None if properties is None else properties.error
        duration = None if properties is None else properties.duration
        if duration is not None and math.isfinite(float(duration)):
            duration_sum += float(duration)
        if error is None or not math.isfinite(float(error)):
            unknown_error_count += 1
            continue
        error_value = float(error)
        if not 0.0 <= error_value < 1.0:
            unknown_error_count += 1
            continue
        known_error_count += 1
        all_gate_success_proxy *= 1.0 - error_value
        if len(qargs) == 2:
            two_qubit_success_proxy *= 1.0 - error_value
    return {
        "known_error_instruction_count": known_error_count,
        "unknown_error_instruction_count": unknown_error_count,
        "sum_instruction_duration_seconds": duration_sum,
        "aggregate_gate_error_proxy": 1.0 - all_gate_success_proxy,
        "two_qubit_gate_error_proxy": 1.0 - two_qubit_success_proxy,
    }


def _load_continuum_errors(
    experiment: ParticleCreationFLRWExperiment,
) -> tuple[dict[int, float], dict[str, Any]]:
    """Load independent refinement errors and exact input-file provenance."""

    path = experiment.artifacts.independent_validation_json
    raw_bytes = path.read_bytes()
    payload = json.loads(raw_bytes.decode("utf-8"))
    continuum_errors = {
        int(record["time_steps"]): float(record["maximum_observable_absolute_error"])
        for record in payload["convergence"]
    }
    provenance = {
        "artifact_path": repository_relative_path(path),
        "artifact_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "digest_scope": "exact_file_bytes",
        "schema_version": payload.get("schema_version"),
    }
    return continuum_errors, provenance


def _transpilation_record(
    *,
    experiment: ParticleCreationFLRWExperiment,
    backend: Any,
    policy: HardwareFeasibilityPolicy,
    time_steps: int,
    transpiler_seed: int,
    continuum_error: float,
) -> TranspilationRecord:
    """Transpile one circuit without invoking any backend execution method."""

    qiskit_transpiler = require_dependency(
        "qiskit.transpiler",
        "run the particle-creation transpilation-only feasibility study",
    )
    parameters = replace(experiment.parameters, time_steps=time_steps)
    logical_circuit = build_particle_creation_circuit(parameters)
    pass_manager = qiskit_transpiler.generate_preset_pass_manager(
        optimization_level=policy.optimization_level,
        backend=backend,
        seed_transpiler=transpiler_seed,
        translation_method=policy.translation_method,
    )
    transpiled_circuit = pass_manager.run(logical_circuit)
    _, logical_two_qubit = _arity_gate_counts(logical_circuit)
    one_qubit_count, two_qubit_count = _arity_gate_counts(transpiled_circuit)
    operation_counts = _operation_counts(transpiled_circuit)
    initial_layout = _layout_indices(
        transpiled_circuit,
        "initial_index_layout",
    )
    final_layout = _layout_indices(
        transpiled_circuit,
        "final_index_layout",
    )
    calibration = _calibration_proxies(transpiled_circuit, backend)
    return TranspilationRecord(
        time_steps=time_steps,
        transpiler_seed=transpiler_seed,
        logical_depth=int(logical_circuit.depth()),
        logical_size=int(logical_circuit.size()),
        logical_operation_counts=_operation_counts(logical_circuit),
        logical_two_qubit_gate_count=logical_two_qubit,
        transpiled_depth=int(transpiled_circuit.depth()),
        transpiled_size=int(transpiled_circuit.size()),
        transpiled_operation_counts=operation_counts,
        one_qubit_gate_count=one_qubit_count,
        two_qubit_gate_count=two_qubit_count,
        surviving_swap_count=int(operation_counts.get("swap", 0)),
        initial_layout=initial_layout,
        final_layout=final_layout,
        initial_pair_adjacent=_initial_pair_adjacent(backend, initial_layout),
        known_error_instruction_count=int(calibration["known_error_instruction_count"]),
        unknown_error_instruction_count=int(
            calibration["unknown_error_instruction_count"]
        ),
        sum_instruction_duration_seconds=float(
            calibration["sum_instruction_duration_seconds"]
        ),
        aggregate_gate_error_proxy=float(calibration["aggregate_gate_error_proxy"]),
        two_qubit_gate_error_proxy=float(calibration["two_qubit_gate_error_proxy"]),
        continuum_maximum_observable_error=continuum_error,
    )


def _aggregate_records(
    records: tuple[TranspilationRecord, ...],
    time_steps_values: tuple[int, ...],
) -> tuple[AggregateTranspilationRecord, ...]:
    """Aggregate transpilation metrics across deterministic seeds."""

    aggregates: list[AggregateTranspilationRecord] = []
    for time_steps in time_steps_values:
        matching = tuple(
            record for record in records if record.time_steps == time_steps
        )
        depths = [record.transpiled_depth for record in matching]
        two_qubit_counts = [record.two_qubit_gate_count for record in matching]
        layouts = tuple(sorted({record.initial_layout for record in matching}))
        aggregates.append(
            AggregateTranspilationRecord(
                time_steps=time_steps,
                logical_depth=matching[0].logical_depth,
                logical_two_qubit_gate_count=(matching[0].logical_two_qubit_gate_count),
                median_transpiled_depth=float(median(depths)),
                minimum_transpiled_depth=min(depths),
                maximum_transpiled_depth=max(depths),
                median_two_qubit_gate_count=float(median(two_qubit_counts)),
                minimum_two_qubit_gate_count=min(two_qubit_counts),
                maximum_two_qubit_gate_count=max(two_qubit_counts),
                maximum_surviving_swap_count=max(
                    record.surviving_swap_count for record in matching
                ),
                unique_initial_layouts=layouts,
                all_initial_pairs_adjacent=all(
                    record.initial_pair_adjacent for record in matching
                ),
                median_aggregate_gate_error_proxy=float(
                    median(record.aggregate_gate_error_proxy for record in matching)
                ),
                median_two_qubit_gate_error_proxy=float(
                    median(record.two_qubit_gate_error_proxy for record in matching)
                ),
                median_sum_instruction_duration_seconds=float(
                    median(
                        record.sum_instruction_duration_seconds for record in matching
                    )
                ),
                continuum_maximum_observable_error=(
                    matching[0].continuum_maximum_observable_error
                ),
            )
        )
    return tuple(aggregates)


def run_hardware_feasibility_study(
    experiment: ParticleCreationFLRWExperiment,
    *,
    backend: Any | None = None,
) -> HardwareFeasibilityStudy:
    """Run local transpilation only and return structured advisory evidence."""

    policy = hardware_feasibility_policy(experiment)
    benchmark = compute_benchmark(experiment.parameters)
    validation_context = validation_context_for_benchmark(experiment, benchmark)
    independent_assessment = require_independent_validation_artifact(
        experiment,
        benchmark,
        validation_context,
    )
    selected_backend = backend or instantiate_local_testing_backend(
        policy.backend_class
    )
    continuum_errors, independent_provenance = _load_continuum_errors(experiment)
    independent_provenance.update(
        {
            "validation_gate": "require_independent_validation_artifact",
            "passed": bool(independent_assessment.passed),
            "lineage_status": ArtifactLineageStatus.CURRENT.value,
            "lineage_id": independent_assessment.lineage_id,
            "stored_content_matches_fresh_computation": True,
        }
    )
    missing_steps = set(policy.time_steps) - set(continuum_errors)
    if missing_steps:
        raise ValueError(
            "Independent convergence evidence lacks time steps: "
            + ", ".join(str(value) for value in sorted(missing_steps))
        )
    records = tuple(
        _transpilation_record(
            experiment=experiment,
            backend=selected_backend,
            policy=policy,
            time_steps=time_steps,
            transpiler_seed=seed,
            continuum_error=continuum_errors[time_steps],
        )
        for time_steps in policy.time_steps
        for seed in policy.transpiler_seeds
    )
    aggregates = _aggregate_records(records, policy.time_steps)
    preferred = min(
        aggregates,
        key=lambda record: (
            record.median_two_qubit_gate_error_proxy,
            record.median_two_qubit_gate_count,
            record.median_transpiled_depth,
        ),
    )
    backend_summary = summarize_backend(selected_backend)
    operation_names = backend_summary.get("operation_names")
    if isinstance(operation_names, list):
        backend_summary["operation_names"] = sorted(
            str(name) for name in operation_names
        )
    return HardwareFeasibilityStudy(
        policy=policy,
        backend_summary=backend_summary,
        records=records,
        aggregates=aggregates,
        preferred_time_steps_by_hardware_cost=preferred.time_steps,
        validation_context=validation_context.to_serializable(),
        prerequisites={"independent_validation": independent_provenance},
    )


def hardware_feasibility_to_serializable(
    experiment: ParticleCreationFLRWExperiment,
    study: HardwareFeasibilityStudy,
) -> dict[str, Any]:
    """Serialize study evidence without implying hardware validation."""

    return {
        "schema_version": 1,
        "experiment_name": experiment.configuration.experiment_name,
        "status": "exploratory_transpilation_only",
        "execution_performed": False,
        "runtime_service_created": False,
        "job_submitted": False,
        "policy": study.policy.to_serializable(),
        "prerequisites": dict(study.prerequisites),
        "validation_context": dict(study.validation_context),
        "backend_summary": dict(study.backend_summary),
        "software": {
            "python": platform.python_version(),
            "qiskit": version("qiskit"),
            "qiskit_ibm_runtime": version("qiskit-ibm-runtime"),
        },
        "method": {
            "transpiler": "qiskit.transpiler.generate_preset_pass_manager",
            "official_references": [
                OFFICIAL_TRANSPILATION_GUIDE,
                OFFICIAL_OPTIMIZATION_GUIDE,
            ],
            "gate_error_proxy": (
                "1 - product(1 - calibrated_instruction_error) over the "
                "transpiled state-preparation circuit"
            ),
            "gate_error_proxy_omissions": [
                "measurement and readout error",
                "idle-time decoherence",
                "crosstalk and coherent error accumulation",
                "observable-measurement synthesis",
                "error mitigation",
            ],
            "swap_metric_limitation": (
                "The surviving SWAP count is measured after ISA translation; "
                "decomposed routing operations may not retain the name swap."
            ),
        },
        "records": [record.to_serializable() for record in study.records],
        "aggregates": [record.to_serializable() for record in study.aggregates],
        "decision": {
            "preferred_time_steps_by_hardware_cost": (
                study.preferred_time_steps_by_hardware_cost
            ),
            "live_hardware_recommendation": "defer",
            "scientific_interpretation": (
                "The preferred value minimizes structural hardware cost among "
                "the compared discretizations; it is not the most accurate "
                "continuum interpolation."
            ),
            "required_next_evidence": [
                "current real-backend calibration and transpilation assessment",
                "acceptable noisy or local-testing observable assessment",
                "explicit review of discretization-versus-noise tradeoffs",
            ],
        },
    }


def _write_summary_table(
    study: HardwareFeasibilityStudy,
    output_path: Path,
) -> Path:
    """Write seed-aggregated feasibility metrics as Markdown."""

    lines = [
        "# Particle-Creation FLRW Hardware-Feasibility Summary",
        "",
        (
            "This table reports fake-backend transpilation metrics only. The "
            "error columns are calibration-based proxies, not fidelities."
        ),
        "",
        "|Time steps|Logical depth|Logical 2Q gates|Transpiled depth median [range]|2Q gates median [range]|Max surviving SWAPs|Median 2Q error proxy|Median all-gate error proxy|Continuum observable error|",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for record in study.aggregates:
        lines.append(
            "|"
            f"{record.time_steps}|"
            f"{record.logical_depth}|"
            f"{record.logical_two_qubit_gate_count}|"
            f"{record.median_transpiled_depth:.1f} "
            f"[{record.minimum_transpiled_depth}, {record.maximum_transpiled_depth}]|"
            f"{record.median_two_qubit_gate_count:.1f} "
            f"[{record.minimum_two_qubit_gate_count}, {record.maximum_two_qubit_gate_count}]|"
            f"{record.maximum_surviving_swap_count}|"
            f"{record.median_two_qubit_gate_error_proxy:.6f}|"
            f"{record.median_aggregate_gate_error_proxy:.6f}|"
            f"{record.continuum_maximum_observable_error:.6e}|"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def _write_report(
    experiment: ParticleCreationFLRWExperiment,
    study: HardwareFeasibilityStudy,
    json_path: Path,
    table_path: Path,
    output_path: Path,
) -> Path:
    """Write the exploratory feasibility interpretation."""

    preferred = next(
        record
        for record in study.aggregates
        if record.time_steps == study.preferred_time_steps_by_hardware_cost
    )
    highest = max(study.aggregates, key=lambda record: record.time_steps)
    lines = [
        "# Particle-Creation FLRW Hardware-Feasibility Report",
        "",
        "## Status",
        "",
        "**Exploratory transpilation only. Live hardware recommendation: DEFER.**",
        "",
        (
            "No circuit was executed, no Runtime service was created, and no job "
            "was submitted."
        ),
        "",
        "## Method",
        "",
        (
            f"Circuits with `N = {', '.join(str(value) for value in study.policy.time_steps)}` "
            f"were mapped to `{study.backend_summary.get('backend_class')}` at "
            f"optimization level `{study.policy.optimization_level}` with the "
            f"`{study.policy.translation_method}` translation method across "
            f"{len(study.policy.transpiler_seeds)} deterministic seeds."
        ),
        (
            "The aggregate error proxy multiplies independent calibrated gate "
            "success probabilities. It omits readout, idling, crosstalk, coherent "
            "effects, observable synthesis, and mitigation and is not fidelity."
        ),
        (
            "The study required current, passing independent-validation evidence; "
            "the exact input path and SHA-256 digest are recorded in the JSON "
            "artifact."
        ),
        "",
        "## Result",
        "",
        (
            f"`N = {preferred.time_steps}` has the lowest structural hardware cost "
            "among the compared candidates. Its median transpiled depth is "
            f"`{preferred.median_transpiled_depth:.1f}`, its median two-qubit gate "
            f"count is `{preferred.median_two_qubit_gate_count:.1f}`, and its median "
            "two-qubit calibration-error proxy is "
            f"`{preferred.median_two_qubit_gate_error_proxy:.6f}`."
        ),
        (
            f"At `N = {highest.time_steps}`, the continuum-interpolation observable "
            f"error decreases to `{highest.continuum_maximum_observable_error:.6e}`, "
            "but the two-qubit burden and calibration-error proxy increase."
        ),
        "",
        "## Decision",
        "",
        (
            f"Retain `N = {preferred.time_steps}` only as the least costly declared "
            "discrete candidate. "
            "The study does not authorize a live run because the calibration is a "
            "fixed fake-backend snapshot and structural proxies do not establish "
            "observable accuracy."
        ),
        (
            "A current real-backend transpilation assessment and an acceptable "
            "noisy or local-testing observable assessment remain required. If the "
            "noise-versus-discretization tradeoff remains unacceptable, investigate "
            "a symmetric splitting refinement before increasing the slice count."
        ),
        "",
        "## Artifacts",
        "",
        f"- JSON evidence: `{repository_relative_path(json_path)}`",
        f"- Summary table: `{repository_relative_path(table_path)}`",
        "",
        "## Method References",
        "",
        f"- [IBM Quantum transpilation guide]({OFFICIAL_TRANSPILATION_GUIDE})",
        f"- [IBM Quantum optimization-level guide]({OFFICIAL_OPTIMIZATION_GUIDE})",
        "",
        (
            "This result concerns the reduced experiment "
            f"`{experiment.configuration.experiment_name}` only."
        ),
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def write_hardware_feasibility_artifacts(
    experiment: ParticleCreationFLRWExperiment,
    study: HardwareFeasibilityStudy,
    *,
    json_path: str | Path | None = None,
    report_path: str | Path | None = None,
    table_path: str | Path | None = None,
) -> dict[str, Path]:
    """Write deterministic JSON, report, and summary-table artifacts."""

    resolved_json = (
        experiment.artifacts.hardware_feasibility_json
        if json_path is None
        else Path(json_path).expanduser().resolve()
    )
    resolved_report = (
        experiment.artifacts.hardware_feasibility_report_markdown
        if report_path is None
        else Path(report_path).expanduser().resolve()
    )
    resolved_table = (
        experiment.artifacts.hardware_feasibility_table_markdown
        if table_path is None
        else Path(table_path).expanduser().resolve()
    )
    resolved_json.parent.mkdir(parents=True, exist_ok=True)
    resolved_json.write_text(
        json.dumps(
            hardware_feasibility_to_serializable(experiment, study),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    _write_summary_table(study, resolved_table)
    _write_report(
        experiment,
        study,
        resolved_json,
        resolved_table,
        resolved_report,
    )
    return {
        "hardware_feasibility_json": resolved_json,
        "hardware_feasibility_report_markdown": resolved_report,
        "hardware_feasibility_table_markdown": resolved_table,
    }


def main(argv: list[str] | None = None) -> int:
    """Run and persist the transpilation-only feasibility study."""

    parser = argparse.ArgumentParser(
        description=(
            "Compare particle-creation discretizations through local fake-backend "
            "transpilation without executing a circuit or submitting a job."
        )
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--output", default=None)
    parser.add_argument("--report-output", default=None)
    parser.add_argument("--table-output", default=None)
    args = parser.parse_args(argv)

    experiment = load_experiment_definition(args.config)
    study = run_hardware_feasibility_study(experiment)
    outputs = write_hardware_feasibility_artifacts(
        experiment,
        study,
        json_path=args.output,
        report_path=args.report_output,
        table_path=args.table_output,
    )
    print("execution_performed: False")
    print("job_submitted: False")
    print(
        "preferred_time_steps_by_hardware_cost: "
        f"{study.preferred_time_steps_by_hardware_cost}"
    )
    print("live_hardware_recommendation: DEFER")
    for label, path in outputs.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
