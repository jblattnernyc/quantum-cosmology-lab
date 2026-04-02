"""Concrete execution wrappers for exact, Aer, and IBM estimator workflows."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from qclab.backends.base import BackendRequest, ExecutionTier
from qclab.backends.hardware import (
    parse_ibm_runtime_options,
    resolve_ibm_backend,
    summarize_backend,
    summarize_runtime_job,
)
from qclab.observables import (
    ObservableDefinition,
    ObservableEvaluation,
    coerce_observable_sequence,
    observable_to_qiskit,
)
from qclab.utils.optional import require_dependency
from qclab.utils.runtime import guard_aer_execution


@dataclass(frozen=True)
class ExecutionProvenance:
    """Provenance metadata for a single backend execution."""

    tier: ExecutionTier
    backend_name: str
    primitive_name: str
    shots: int | None = None
    seed: int | None = None
    precision: float | None = None
    optimization_level: int | None = None
    job_id: str | None = None
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EstimatorExecutionResult:
    """Normalized result from an estimator-style backend execution."""

    request: BackendRequest
    evaluations: tuple[ObservableEvaluation, ...]
    provenance: ExecutionProvenance
    raw_result: Any = None
    raw_job: Any = None
    raw_backend: Any = None
    job_metadata: dict[str, Any] = field(default_factory=dict)


def _normalize_parameter_values(
    parameter_values: Sequence[float] | None,
) -> tuple[float, ...] | None:
    """Normalize a single parameter binding set."""

    if parameter_values is None:
        return None
    normalized = tuple(float(value) for value in parameter_values)
    return normalized


def build_estimator_pub(
    circuit: Any,
    observables: Sequence[ObservableDefinition] | ObservableDefinition,
    *,
    parameter_values: Sequence[float] | None = None,
) -> tuple[Any, Any] | tuple[Any, Any, tuple[float, ...]]:
    """Build a single Primitive Unified Bloc for estimator execution."""

    normalized_observables = coerce_observable_sequence(observables)
    observable_payloads = [
        observable_to_qiskit(observable) for observable in normalized_observables
    ]
    observables_payload: Any
    if len(observable_payloads) == 1:
        observables_payload = observable_payloads[0]
    else:
        observables_payload = observable_payloads
    normalized_parameters = _normalize_parameter_values(parameter_values)
    if normalized_parameters is None:
        return (circuit, observables_payload)
    return (circuit, observables_payload, normalized_parameters)


def prepare_circuit_and_observables_for_backend(
    circuit: Any,
    observables: Sequence[ObservableDefinition] | ObservableDefinition,
    *,
    backend: Any,
    optimization_level: int = 1,
    seed_transpiler: int | None = None,
    pass_manager_factory: Callable[..., Any] | None = None,
) -> tuple[Any, Any]:
    """Prepare a circuit and observables for backend-specific layout.

    This follows the current Qiskit pattern of generating a preset pass manager
    for the target backend and applying the resulting layout to Pauli
    observables when the observable object exposes ``apply_layout``.
    """

    normalized_observables = coerce_observable_sequence(observables)
    observable_payloads = [
        _coerce_layout_aware_observable_payload(observable_to_qiskit(observable))
        for observable in normalized_observables
    ]
    if pass_manager_factory is None:
        transpiler_preset = require_dependency(
            "qiskit.transpiler.preset_passmanagers",
            "prepare circuits for backend-specific ISA execution",
        )
        pass_manager_factory = transpiler_preset.generate_preset_pass_manager
    pass_manager_kwargs: dict[str, Any] = {"optimization_level": optimization_level}
    if seed_transpiler is not None:
        pass_manager_kwargs["seed_transpiler"] = seed_transpiler
    target = getattr(backend, "target", None)
    if target is not None:
        pass_manager_kwargs["target"] = target
    else:
        pass_manager_kwargs["backend"] = backend
    pass_manager = pass_manager_factory(**pass_manager_kwargs)
    isa_circuit = pass_manager.run(circuit)
    isa_observable_payloads = [
        observable.apply_layout(isa_circuit.layout)
        if hasattr(observable, "apply_layout")
        else observable
        for observable in observable_payloads
    ]
    isa_observables: Any
    if len(isa_observable_payloads) == 1:
        isa_observables = isa_observable_payloads[0]
    else:
        isa_observables = isa_observable_payloads
    return isa_circuit, isa_observables


def _coerce_layout_aware_observable_payload(observable_payload: Any) -> Any:
    """Upgrade string Pauli payloads so backend layout can be applied uniformly."""

    if hasattr(observable_payload, "apply_layout"):
        return observable_payload
    if isinstance(observable_payload, str):
        normalized = observable_payload.strip().upper()
        if normalized and all(symbol in {"I", "X", "Y", "Z"} for symbol in normalized):
            quantum_info = require_dependency(
                "qiskit.quantum_info",
                "apply backend layout to Pauli observables for ISA execution",
            )
            return quantum_info.SparsePauliOp.from_list([(normalized, 1.0)])
    return observable_payload


def _json_safe(value: Any) -> Any:
    """Convert common runtime payloads into JSON-safe structures."""

    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if hasattr(value, "tolist"):
        return _json_safe(value.tolist())
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if hasattr(value, "value") and isinstance(getattr(value, "value"), str):
        return value.value
    return repr(value)


def execution_result_to_serializable(result: EstimatorExecutionResult) -> dict[str, Any]:
    """Convert an execution result into a JSON-safe record."""

    return {
        "request": {
            "tier": result.request.tier.value,
            "backend_name": result.request.backend_name,
            "shots": result.request.shots,
            "seed": result.request.seed,
            "mitigation_enabled": result.request.mitigation_enabled,
            "precision": result.request.precision,
            "optimization_level": result.request.optimization_level,
            "options": _json_safe(result.request.options),
        },
        "provenance": {
            "tier": result.provenance.tier.value,
            "backend_name": result.provenance.backend_name,
            "primitive_name": result.provenance.primitive_name,
            "shots": result.provenance.shots,
            "seed": result.provenance.seed,
            "precision": result.provenance.precision,
            "optimization_level": result.provenance.optimization_level,
            "job_id": result.provenance.job_id,
            "timestamp_utc": result.provenance.timestamp_utc,
            "metadata": _json_safe(result.provenance.metadata),
        },
        "evaluations": [
            {
                "observable_name": evaluation.observable.name,
                "operator_label": evaluation.observable.operator_label,
                "measurement_basis": evaluation.observable.measurement_basis,
                "physical_meaning": evaluation.observable.physical_meaning,
                "units": evaluation.observable.units,
                "value": evaluation.value,
                "uncertainty": evaluation.uncertainty,
                "shots": evaluation.shots,
                "metadata": _json_safe(evaluation.metadata),
            }
            for evaluation in result.evaluations
        ],
        "job_metadata": _json_safe(result.job_metadata),
    }


def write_execution_result_json(
    result: EstimatorExecutionResult,
    path: str | Path,
) -> Path:
    """Write a serialized execution result to disk as formatted JSON."""

    resolved_path = Path(path).expanduser().resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(
        json.dumps(execution_result_to_serializable(result), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return resolved_path


def _coerce_numeric_vector(values: Any) -> tuple[float, ...]:
    """Convert primitive result payloads into a flat tuple of floats."""

    if hasattr(values, "tolist"):
        values = values.tolist()
    if isinstance(values, (int, float)):
        return (float(values),)
    if isinstance(values, complex):
        if abs(values.imag) > 1e-12:
            raise ValueError("Complex expectation values with nonzero imaginary parts are not supported.")
        return (float(values.real),)
    if isinstance(values, (list, tuple)):
        if values and isinstance(values[0], (list, tuple)):
            if len(values) != 1:
                raise ValueError(
                    "Only a single parameter binding set per estimator execution is supported."
                )
            return _coerce_numeric_vector(values[0])
        return tuple(float(value) for value in values)
    raise TypeError(f"Unsupported primitive result payload type: {type(values)!r}")


def _extract_estimator_payload(
    primitive_result: Any,
) -> tuple[tuple[float, ...], tuple[float, ...], dict[str, Any]]:
    """Extract expectation values, uncertainties, and metadata from a result."""

    pub_result = primitive_result[0]
    data = getattr(pub_result, "data", pub_result)
    values = _coerce_numeric_vector(getattr(data, "evs"))
    std_values = getattr(data, "stds", None)
    if std_values is None:
        uncertainties = tuple(0.0 for _ in values)
    else:
        uncertainties = _coerce_numeric_vector(std_values)
    metadata = getattr(pub_result, "metadata", {})
    if metadata is None:
        metadata = {}
    return values, uncertainties, dict(metadata)


def _job_identifier(job: Any) -> str | None:
    """Return a primitive job identifier when available."""

    job_id = getattr(job, "job_id", None)
    if callable(job_id):
        return str(job_id())
    if job_id is not None:
        return str(job_id)
    return None


def _run_estimator_workload(
    *,
    primitive: Any,
    primitive_name: str,
    circuit: Any,
    observables: Sequence[ObservableDefinition] | ObservableDefinition,
    request: BackendRequest,
    parameter_values: Sequence[float] | None = None,
    provenance_metadata: dict[str, Any] | None = None,
    raw_job: Any = None,
    raw_backend: Any = None,
) -> EstimatorExecutionResult:
    """Execute a single estimator workload and normalize its result."""

    normalized_observables = coerce_observable_sequence(observables)
    pub = build_estimator_pub(
        circuit,
        normalized_observables,
        parameter_values=parameter_values,
    )
    run_kwargs: dict[str, Any] = {}
    if request.precision is not None:
        run_kwargs["precision"] = request.precision
    job = primitive.run([pub], **run_kwargs)
    primitive_result = job.result()
    values, uncertainties, job_metadata = _extract_estimator_payload(primitive_result)
    if len(values) != len(normalized_observables):
        raise ValueError(
            "The number of returned expectation values does not match the number of observables."
        )
    metadata_payload = {} if provenance_metadata is None else dict(provenance_metadata)
    if request.tier is ExecutionTier.IBM_HARDWARE:
        metadata_payload.setdefault("runtime_job_summary", summarize_runtime_job(job))
    evaluations = tuple(
        ObservableEvaluation(
            observable=observable,
            value=value,
            uncertainty=uncertainty,
            shots=request.shots,
            metadata={"backend_name": request.backend_name, "tier": request.tier.value},
        )
        for observable, value, uncertainty in zip(
            normalized_observables, values, uncertainties, strict=True
        )
    )
    provenance = ExecutionProvenance(
        tier=request.tier,
        backend_name=request.backend_name,
        primitive_name=primitive_name,
        shots=request.shots,
        seed=request.seed,
        precision=request.precision,
        optimization_level=request.optimization_level,
        job_id=_job_identifier(job),
        metadata=metadata_payload,
    )
    return EstimatorExecutionResult(
        request=request,
        evaluations=evaluations,
        provenance=provenance,
        raw_result=primitive_result,
        raw_job=job if raw_job is None else raw_job,
        raw_backend=raw_backend,
        job_metadata=job_metadata,
    )


class ExactLocalEstimatorExecutor:
    """Exact local execution through ``qiskit.primitives.StatevectorEstimator``."""

    primitive_name = "qiskit.primitives.StatevectorEstimator"

    def __init__(self, primitive_factory: Callable[..., Any] | None = None) -> None:
        self._primitive_factory = primitive_factory or self._default_primitive_factory

    @staticmethod
    def _default_primitive_factory(**kwargs: Any) -> Any:
        primitives_module = require_dependency(
            "qiskit.primitives",
            "run exact local estimator workflows",
        )
        return primitives_module.StatevectorEstimator(**kwargs)

    def run(
        self,
        circuit: Any,
        observables: Sequence[ObservableDefinition] | ObservableDefinition,
        *,
        request: BackendRequest | None = None,
        parameter_values: Sequence[float] | None = None,
    ) -> EstimatorExecutionResult:
        """Evaluate observables with the exact local estimator primitive."""

        effective_request = request or BackendRequest(
            tier=ExecutionTier.EXACT_LOCAL,
            backend_name="statevector_estimator",
            precision=0.0,
        )
        if effective_request.tier is not ExecutionTier.EXACT_LOCAL:
            raise ValueError("ExactLocalEstimatorExecutor requires EXACT_LOCAL requests.")
        primitive = self._primitive_factory(
            default_precision=effective_request.precision or 0.0,
            seed=effective_request.seed,
        )
        return _run_estimator_workload(
            primitive=primitive,
            primitive_name=self.primitive_name,
            circuit=circuit,
            observables=observables,
            request=effective_request,
            parameter_values=parameter_values,
        )


class AerEstimatorExecutor:
    """Noisy local execution through ``qiskit.primitives.BackendEstimatorV2``."""

    primitive_name = "qiskit.primitives.BackendEstimatorV2"

    def __init__(
        self,
        primitive_factory: Callable[..., Any] | None = None,
        backend_factory: Callable[..., Any] | None = None,
    ) -> None:
        self._primitive_factory = primitive_factory or self._default_primitive_factory
        self._backend_factory = backend_factory or self._default_backend_factory

    @staticmethod
    def _default_primitive_factory(**kwargs: Any) -> Any:
        primitives_module = require_dependency(
            "qiskit.primitives",
            "run noisy local estimator workflows with BackendEstimatorV2",
        )
        return primitives_module.BackendEstimatorV2(**kwargs)

    @staticmethod
    def _default_backend_factory(**kwargs: Any) -> Any:
        aer_module = require_dependency(
            "qiskit_aer",
            "construct AerSimulator backends for noisy local execution",
        )
        return aer_module.AerSimulator(**kwargs)

    def run(
        self,
        circuit: Any,
        observables: Sequence[ObservableDefinition] | ObservableDefinition,
        *,
        request: BackendRequest | None = None,
        parameter_values: Sequence[float] | None = None,
    ) -> EstimatorExecutionResult:
        """Evaluate observables with the Aer estimator primitive."""

        effective_request = request or BackendRequest(
            tier=ExecutionTier.NOISY_LOCAL,
            backend_name="aer_estimator",
        )
        if effective_request.tier is not ExecutionTier.NOISY_LOCAL:
            raise ValueError("AerEstimatorExecutor requires NOISY_LOCAL requests.")
        guard_aer_execution("Noisy local Aer execution")
        options = dict(effective_request.options)
        backend_options = dict(options.get("backend_options", {}))
        estimator_options = dict(options.get("estimator_options", {}))
        if effective_request.seed is not None:
            estimator_options.setdefault("seed_simulator", effective_request.seed)
        aer_backend = self._backend_factory(**backend_options)
        primitive = self._primitive_factory(
            backend=aer_backend,
            options=estimator_options or None,
        )
        return _run_estimator_workload(
            primitive=primitive,
            primitive_name=self.primitive_name,
            circuit=circuit,
            observables=observables,
            request=effective_request,
            parameter_values=parameter_values,
        )


class IBMRuntimeEstimatorExecutor:
    """IBM Runtime execution through ``qiskit_ibm_runtime.EstimatorV2``."""

    primitive_name = "qiskit_ibm_runtime.EstimatorV2"

    def __init__(
        self,
        *,
        service_factory: Callable[..., Any] | None = None,
        estimator_factory: Callable[..., Any] | None = None,
        pass_manager_factory: Callable[..., Any] | None = None,
    ) -> None:
        self._service_factory = service_factory or self._default_service_factory
        self._estimator_factory = estimator_factory or self._default_estimator_factory
        self._pass_manager_factory = pass_manager_factory

    @staticmethod
    def _default_service_factory(**kwargs: Any) -> Any:
        runtime_module = require_dependency(
            "qiskit_ibm_runtime",
            "connect to IBM Runtime backends",
        )
        return runtime_module.QiskitRuntimeService(**kwargs)

    @staticmethod
    def _default_estimator_factory(**kwargs: Any) -> Any:
        runtime_module = require_dependency(
            "qiskit_ibm_runtime",
            "create IBM Runtime estimator primitives",
        )
        return runtime_module.EstimatorV2(**kwargs)

    def run(
        self,
        circuit: Any,
        observables: Sequence[ObservableDefinition] | ObservableDefinition,
        *,
        request: BackendRequest,
        parameter_values: Sequence[float] | None = None,
        service: Any = None,
        service_kwargs: dict[str, Any] | None = None,
        backend: Any = None,
        transpile_for_backend: bool = True,
    ) -> EstimatorExecutionResult:
        """Evaluate observables on an IBM Runtime backend.

        Credentials must be supplied through the user's configured Runtime
        account or via ``service_kwargs``. Secrets must not be hard-coded into
        tracked source files.
        """

        if request.tier is not ExecutionTier.IBM_HARDWARE:
            raise ValueError("IBMRuntimeEstimatorExecutor requires IBM_HARDWARE requests.")
        service_kwargs = {} if service_kwargs is None else dict(service_kwargs)
        instance = service_kwargs.get("instance")
        runtime_service = service
        if backend is None:
            runtime_service = runtime_service or self._service_factory(**service_kwargs)
        selection_policy, mitigation_policy, options = parse_ibm_runtime_options(
            request.options,
            shots=request.shots,
            mitigation_enabled=request.mitigation_enabled,
        )
        resolved_backend, selection_metadata = resolve_ibm_backend(
            request_backend_name=request.backend_name,
            service=runtime_service,
            policy=selection_policy,
            instance=instance,
            provided_backend=backend,
        )
        if bool(selection_metadata.get("local_testing_mode", False)):
            guard_aer_execution(
                "IBM Runtime local testing with Aer-backed fake backends"
            )
        selected_backend_name = (
            selection_metadata.get("selected_backend_name") or request.backend_name
        )
        effective_request = BackendRequest(
            tier=request.tier,
            backend_name=str(selected_backend_name),
            shots=request.shots,
            seed=request.seed,
            mitigation_enabled=request.mitigation_enabled,
            precision=request.precision,
            optimization_level=request.optimization_level,
            options=dict(request.options),
        )
        service_metadata = {
            "channel": getattr(runtime_service, "channel", None),
            "instance": instance,
            "local_testing_mode": bool(
                selection_metadata.get("local_testing_mode", False)
            ),
        }
        prepared_circuit = circuit
        prepared_observables = coerce_observable_sequence(observables)
        if transpile_for_backend:
            prepared_circuit, observable_payloads = prepare_circuit_and_observables_for_backend(
                circuit,
                prepared_observables,
                backend=resolved_backend,
                optimization_level=request.optimization_level or 1,
                seed_transpiler=request.seed,
                pass_manager_factory=self._pass_manager_factory,
            )
            # Rebuild observable definitions only for execution payload replacement.
            prepared_pub = (
                prepared_circuit,
                observable_payloads,
            )
            normalized_parameters = _normalize_parameter_values(parameter_values)
            if normalized_parameters is not None:
                prepared_pub = prepared_pub + (normalized_parameters,)
            primitive = self._estimator_factory(
                mode=resolved_backend,
                options=options or None,
            )
            run_kwargs: dict[str, Any] = {}
            if effective_request.precision is not None:
                run_kwargs["precision"] = effective_request.precision
            job = primitive.run([prepared_pub], **run_kwargs)
            primitive_result = job.result()
            values, uncertainties, job_metadata = _extract_estimator_payload(primitive_result)
            if len(values) != len(prepared_observables):
                raise ValueError(
                    "The number of returned expectation values does not match the number of observables."
                )
            runtime_job_summary = summarize_runtime_job(job)
            evaluations = tuple(
                ObservableEvaluation(
                    observable=observable,
                    value=value,
                    uncertainty=uncertainty,
                    shots=effective_request.shots,
                    metadata={
                        "backend_name": effective_request.backend_name,
                        "tier": effective_request.tier.value,
                    },
                )
                for observable, value, uncertainty in zip(
                    prepared_observables, values, uncertainties, strict=True
                )
            )
            provenance = ExecutionProvenance(
                tier=effective_request.tier,
                backend_name=effective_request.backend_name,
                primitive_name=self.primitive_name,
                shots=effective_request.shots,
                seed=effective_request.seed,
                precision=effective_request.precision,
                optimization_level=effective_request.optimization_level,
                job_id=_job_identifier(job),
                metadata={
                    "service": service_metadata,
                    "backend_selection": selection_metadata,
                    "mitigation_policy": {
                        **_json_safe(mitigation_policy.__dict__),
                        "primitive_options": _json_safe(options),
                    },
                    "backend_summary": summarize_backend(resolved_backend),
                    "runtime_job_summary": runtime_job_summary,
                },
            )
            return EstimatorExecutionResult(
                request=effective_request,
                evaluations=evaluations,
                provenance=provenance,
                raw_result=primitive_result,
                raw_job=job,
                raw_backend=resolved_backend,
                job_metadata=job_metadata,
            )
        primitive = self._estimator_factory(
            mode=resolved_backend,
            options=options or None,
        )
        return _run_estimator_workload(
            primitive=primitive,
            primitive_name=self.primitive_name,
            circuit=prepared_circuit,
            observables=prepared_observables,
            request=effective_request,
            parameter_values=parameter_values,
            provenance_metadata={
                "service": service_metadata,
                "backend_selection": selection_metadata,
                "mitigation_policy": {
                    **_json_safe(mitigation_policy.__dict__),
                    "primitive_options": _json_safe(options),
                },
                "backend_summary": summarize_backend(resolved_backend),
            },
            raw_backend=resolved_backend,
        )
