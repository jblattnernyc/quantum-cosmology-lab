"""Backend-execution tests with fake primitives and services."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from tests.path_setup import ensure_src_path

ensure_src_path()

from qclab.backends import (
    AerEstimatorExecutor,
    BackendRequest,
    ExactLocalEstimatorExecutor,
    IBMRuntimeEstimatorExecutor,
    build_estimator_pub,
    prepare_circuit_and_observables_for_backend,
)
from qclab.backends.base import ExecutionTier, validate_execution_progression
from qclab.observables import make_pauli_observable


class _FakeEstimatorData:
    def __init__(self, evs, stds) -> None:
        self.evs = evs
        self.stds = stds


class _FakePubResult:
    def __init__(self, evs, stds, metadata=None) -> None:
        self.data = _FakeEstimatorData(evs, stds)
        self.metadata = {} if metadata is None else metadata


class _FakeJob:
    def __init__(self, result_payload, job_id="fake-job-001") -> None:
        self._result_payload = result_payload
        self._job_id = job_id

    def result(self):
        return self._result_payload

    def job_id(self):
        return self._job_id


class _FakePrimitive:
    def __init__(self, result_payload, **kwargs) -> None:
        self.result_payload = result_payload
        self.init_kwargs = kwargs
        self.run_calls = []

    def run(self, pubs, **kwargs):
        self.run_calls.append({"pubs": pubs, "kwargs": kwargs})
        return _FakeJob(self.result_payload)


class _FactoryRecorder:
    def __init__(self, instance) -> None:
        self.instance = instance
        self.calls = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return self.instance


class _BackendFactoryRecorder(_FactoryRecorder):
    pass


class _FakeBackend:
    def __init__(self, name: str) -> None:
        self.name = name
        self.target = object()
        self.num_qubits = 5
        self.max_circuits = 100

    def operation_names(self):
        return ["rz", "sx", "cx"]

    def calibration_id(self):
        return "cal-001"

    def status(self):
        class _Status:
            backend_name = "fake_backend"
            backend_version = "1.0"
            operational = True
            pending_jobs = 7
            status_msg = "active"

        return _Status()

    def properties(self, refresh=False):
        del refresh

        class _Properties:
            last_update_date = "2026-04-01T12:00:00+00:00"

            @staticmethod
            def to_dict():
                return {"last_update_date": "2026-04-01T12:00:00+00:00"}

        return _Properties()


class _FakeRuntimeService:
    channel = "ibm_quantum_platform"

    def __init__(self) -> None:
        self.backend_calls = []
        self.least_busy_calls = []

    def backend(self, name, instance=None):
        self.backend_calls.append({"name": name, "instance": instance})
        return _FakeBackend(name)

    def least_busy(self, **kwargs):
        self.least_busy_calls.append(kwargs)
        return _FakeBackend("ibm_least_busy")


class _FakePassManager:
    def run(self, circuit):
        class _CircuitWithLayout:
            def __init__(self, original):
                self.original = original
                self.layout = "fake-layout"

        return _CircuitWithLayout(circuit)


class _FakeLayoutAwareObservable:
    def __init__(self):
        self.applied_layouts = []

    def apply_layout(self, layout):
        self.applied_layouts.append(layout)
        return f"observable-with-{layout}"


class _FakeSparsePauliOp:
    def __init__(self, pauli_terms) -> None:
        self.pauli_terms = pauli_terms
        self.applied_layouts = []

    def apply_layout(self, layout):
        self.applied_layouts.append(layout)
        return f"sparse-pauli-with-{layout}"


class _FakeQuantumInfoModule:
    class SparsePauliOp:
        @staticmethod
        def from_list(pauli_terms):
            return _FakeSparsePauliOp(pauli_terms)


class BackendExecutionTests(unittest.TestCase):
    """Verify estimator-wrapper behavior without live dependencies."""

    def test_build_estimator_pub_uses_qiskit_compatible_observable_payloads(self) -> None:
        observable = make_pauli_observable(
            name="z_expectation",
            terms={"Z": 1.0},
            physical_meaning="Infrastructure-only Pauli-Z observable.",
        )
        pub = build_estimator_pub("circuit", observable, parameter_values=(0.1,))
        self.assertEqual(pub, ("circuit", "Z", (0.1,)))

    def test_exact_local_executor_normalizes_fake_primitive_result(self) -> None:
        observable = make_pauli_observable(
            name="z_expectation",
            terms={"Z": 1.0},
            physical_meaning="Infrastructure-only Pauli-Z observable.",
        )
        primitive = _FakePrimitive([_FakePubResult(evs=(0.25,), stds=(0.01,))])
        factory = _FactoryRecorder(primitive)
        executor = ExactLocalEstimatorExecutor(primitive_factory=factory)
        result = executor.run(
            "circuit",
            observable,
            request=BackendRequest(
                tier=ExecutionTier.EXACT_LOCAL,
                backend_name="statevector_estimator",
                precision=0.0,
                seed=7,
            ),
            parameter_values=(0.2,),
        )
        self.assertEqual(factory.calls[0]["seed"], 7)
        self.assertAlmostEqual(result.evaluations[0].value, 0.25)
        self.assertAlmostEqual(result.evaluations[0].uncertainty, 0.01)
        self.assertEqual(result.provenance.job_id, "fake-job-001")

    def test_aer_executor_builds_run_options_from_request(self) -> None:
        observable = make_pauli_observable(
            name="z_expectation",
            terms={"Z": 1.0},
            physical_meaning="Infrastructure-only Pauli-Z observable.",
        )
        primitive = _FakePrimitive([_FakePubResult(evs=(0.5,), stds=(0.02,))])
        primitive_factory = _FactoryRecorder(primitive)
        backend_factory = _BackendFactoryRecorder(_FakeBackend("aer_simulator"))
        executor = AerEstimatorExecutor(
            primitive_factory=primitive_factory,
            backend_factory=backend_factory,
        )
        with patch("qclab.backends.execution.guard_aer_execution"):
            executor.run(
                "circuit",
                observable,
                request=BackendRequest(
                    tier=ExecutionTier.NOISY_LOCAL,
                    backend_name="aer_estimator",
                    shots=2048,
                    seed=11,
                ),
            )
        self.assertEqual(backend_factory.calls[0], {})
        self.assertEqual(primitive_factory.calls[0]["backend"].name, "aer_simulator")
        self.assertEqual(primitive_factory.calls[0]["options"]["seed_simulator"], 11)

    def test_aer_executor_raises_guard_before_backend_initialization(self) -> None:
        observable = make_pauli_observable(
            name="z_expectation",
            terms={"Z": 1.0},
            physical_meaning="Infrastructure-only Pauli-Z observable.",
        )
        primitive_factory = _FactoryRecorder(_FakePrimitive([_FakePubResult(evs=(0.5,), stds=(0.02,))]))
        backend_factory = _BackendFactoryRecorder(_FakeBackend("aer_simulator"))
        executor = AerEstimatorExecutor(
            primitive_factory=primitive_factory,
            backend_factory=backend_factory,
        )
        with patch(
            "qclab.backends.execution.guard_aer_execution",
            side_effect=RuntimeError("OpenMP shared-memory initialization guard"),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "OpenMP shared-memory initialization",
            ):
                executor.run(
                    "circuit",
                    observable,
                    request=BackendRequest(
                        tier=ExecutionTier.NOISY_LOCAL,
                        backend_name="aer_estimator",
                    ),
                )
        self.assertEqual(backend_factory.calls, [])
        self.assertEqual(primitive_factory.calls, [])

    def test_backend_preparation_applies_layout_when_payload_supports_it(self) -> None:
        fake_payload = _FakeLayoutAwareObservable()
        with patch(
            "qclab.backends.execution.observable_to_qiskit",
            return_value=fake_payload,
        ):
            circuit, observables = prepare_circuit_and_observables_for_backend(
                "logical-circuit",
                (
                    make_pauli_observable(
                        name="z_expectation",
                        terms={"Z": 1.0},
                        physical_meaning="Infrastructure-only Pauli-Z observable.",
                    ),
                ),
                backend=_FakeBackend("fake_backend"),
                pass_manager_factory=lambda **kwargs: _FakePassManager(),
            )
        self.assertEqual(circuit.layout, "fake-layout")
        self.assertEqual(observables, "observable-with-fake-layout")

    def test_backend_preparation_upgrades_single_term_strings_for_layout(self) -> None:
        with patch(
            "qclab.backends.execution.observable_to_qiskit",
            return_value="XX",
        ), patch(
            "qclab.backends.execution.require_dependency",
            return_value=_FakeQuantumInfoModule(),
        ):
            circuit, observables = prepare_circuit_and_observables_for_backend(
                "logical-circuit",
                (
                    make_pauli_observable(
                        name="xx_expectation",
                        terms={"XX": 1.0},
                        physical_meaning="Infrastructure-only Pauli-XX observable.",
                    ),
                ),
                backend=_FakeBackend("fake_backend"),
                pass_manager_factory=lambda **kwargs: _FakePassManager(),
            )
        self.assertEqual(circuit.layout, "fake-layout")
        self.assertEqual(observables, "sparse-pauli-with-fake-layout")

    def test_ibm_executor_uses_service_backend_and_options(self) -> None:
        observable = make_pauli_observable(
            name="z_expectation",
            terms={"Z": 1.0},
            physical_meaning="Infrastructure-only Pauli-Z observable.",
        )
        service = _FakeRuntimeService()
        primitive = _FakePrimitive([_FakePubResult(evs=(0.75,), stds=(0.03,))])
        service_factory = _FactoryRecorder(service)
        estimator_factory = _FactoryRecorder(primitive)
        executor = IBMRuntimeEstimatorExecutor(
            service_factory=service_factory,
            estimator_factory=estimator_factory,
        )
        result = executor.run(
            "circuit",
            observable,
            request=BackendRequest(
                tier=ExecutionTier.IBM_HARDWARE,
                backend_name="ibm_fake_backend",
                mitigation_enabled=True,
                options={"optimization_hint": "test"},
            ),
            service_kwargs={"instance": "ibm-q/open/main"},
            transpile_for_backend=False,
        )
        self.assertEqual(service.backend_calls[0]["name"], "ibm_fake_backend")
        self.assertEqual(service.backend_calls[0]["instance"], "ibm-q/open/main")
        self.assertEqual(estimator_factory.calls[0]["options"]["resilience_level"], 1)
        self.assertEqual(
            result.provenance.metadata["service"]["channel"],
            "ibm_quantum_platform",
        )
        self.assertEqual(
            result.provenance.metadata["backend_selection"]["selected_backend_name"],
            "ibm_fake_backend",
        )

    def test_ibm_executor_can_select_least_busy_backend(self) -> None:
        observable = make_pauli_observable(
            name="z_expectation",
            terms={"Z": 1.0},
            physical_meaning="Infrastructure-only Pauli-Z observable.",
        )
        service = _FakeRuntimeService()
        primitive = _FakePrimitive([_FakePubResult(evs=(0.42,), stds=(0.02,))])
        executor = IBMRuntimeEstimatorExecutor(
            service_factory=_FactoryRecorder(service),
            estimator_factory=_FactoryRecorder(primitive),
        )
        result = executor.run(
            "circuit",
            observable,
            request=BackendRequest(
                tier=ExecutionTier.IBM_HARDWARE,
                backend_name="ibm_backend_required",
                options={
                    "selection_policy": {
                        "strategy": "least_busy",
                        "min_num_qubits": 2,
                        "operational": True,
                        "simulator": False,
                    }
                },
            ),
            service=service,
            transpile_for_backend=False,
        )
        self.assertEqual(service.least_busy_calls[0]["min_num_qubits"], 2)
        self.assertEqual(result.provenance.backend_name, "ibm_least_busy")

    def test_hardware_execution_requires_exact_local_and_noisy_local_validation(self) -> None:
        with self.assertRaises(ValueError):
            validate_execution_progression(
                ExecutionTier.IBM_HARDWARE,
                benchmark_complete=True,
                exact_local_complete=False,
                noisy_local_complete=True,
            )
