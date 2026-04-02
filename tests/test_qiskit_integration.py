"""Guarded live integration tests against installed Qiskit primitives."""

from __future__ import annotations

import importlib.util
import math
import platform
import sys
import unittest

from tests.path_setup import ensure_src_path

ensure_src_path()

from qclab.backends import (
    AerEstimatorExecutor,
    BackendRequest,
    ExactLocalEstimatorExecutor,
    IBMRuntimeEstimatorExecutor,
)
from qclab.backends.base import ExecutionTier
from qclab.observables import make_pauli_observable


QISKIT_AVAILABLE = importlib.util.find_spec("qiskit") is not None
QISKIT_AER_AVAILABLE = importlib.util.find_spec("qiskit_aer") is not None
QISKIT_RUNTIME_AVAILABLE = importlib.util.find_spec("qiskit_ibm_runtime") is not None
AER_LOCAL_GUARD = (
    platform.system() == "Darwin"
    and platform.machine() == "arm64"
    and sys.version_info >= (3, 14)
)


@unittest.skipUnless(QISKIT_AVAILABLE, "qiskit is not installed")
class ExactLocalQiskitIntegrationTests(unittest.TestCase):
    """Verify the exact-local wrapper against the installed Qiskit stack."""

    def test_exact_local_executor_matches_closed_form_rotation_value(self) -> None:
        from qiskit import QuantumCircuit

        theta = math.pi / 3
        circuit = QuantumCircuit(1)
        circuit.ry(theta, 0)
        observable = make_pauli_observable(
            name="z_expectation",
            terms={"Z": 1.0},
            physical_meaning="Infrastructure-only Pauli-Z observable.",
        )
        result = ExactLocalEstimatorExecutor().run(
            circuit,
            observable,
            request=BackendRequest(
                tier=ExecutionTier.EXACT_LOCAL,
                backend_name="statevector_estimator",
                precision=0.0,
            ),
        )
        self.assertAlmostEqual(result.evaluations[0].value, math.cos(theta), places=10)
        self.assertIn("target_precision", result.job_metadata)

    def test_multiple_observables_are_accepted_by_statevector_estimator(self) -> None:
        from qiskit import QuantumCircuit
        from qiskit.primitives import StatevectorEstimator

        theta = math.pi / 3
        circuit = QuantumCircuit(1)
        circuit.ry(theta, 0)
        z_observable = make_pauli_observable(
            name="z_expectation",
            terms={"Z": 1.0},
            physical_meaning="Infrastructure-only Pauli-Z observable.",
        )
        identity_observable = make_pauli_observable(
            name="identity_expectation",
            terms={"I": 1.0},
            physical_meaning="Infrastructure-only identity observable.",
        )
        from qclab.backends import build_estimator_pub

        pub = build_estimator_pub(circuit, (z_observable, identity_observable))
        result = StatevectorEstimator(default_precision=0.0).run([pub]).result()
        values = result[0].data.evs.tolist()
        self.assertAlmostEqual(values[0], math.cos(theta), places=10)
        self.assertAlmostEqual(values[1], 1.0, places=10)


@unittest.skipUnless(
    QISKIT_AVAILABLE and QISKIT_AER_AVAILABLE,
    "qiskit and qiskit_aer are both required for Aer integration tests",
)
@unittest.skipIf(
    AER_LOCAL_GUARD,
    "Aer live integration is guarded on macOS arm64 with Python 3.14+ due to local libomp runtime aborts; use Python 3.10-3.13 for validated Aer coverage.",
)
class AerQiskitIntegrationTests(unittest.TestCase):
    """Verify the noisy-local wrapper when Aer is installed."""

    def test_aer_executor_runs_simple_single_qubit_observable(self) -> None:
        from qiskit import QuantumCircuit

        theta = math.pi / 3
        circuit = QuantumCircuit(1)
        circuit.ry(theta, 0)
        observable = make_pauli_observable(
            name="z_expectation",
            terms={"Z": 1.0},
            physical_meaning="Infrastructure-only Pauli-Z observable.",
        )
        result = AerEstimatorExecutor().run(
            circuit,
            observable,
            request=BackendRequest(
                tier=ExecutionTier.NOISY_LOCAL,
                backend_name="aer_estimator",
                seed=123,
                precision=0.05,
            ),
        )
        self.assertLess(abs(result.evaluations[0].value - math.cos(theta)), 0.15)


@unittest.skipUnless(
    QISKIT_AVAILABLE and QISKIT_RUNTIME_AVAILABLE,
    "qiskit and qiskit_ibm_runtime are both required for IBM Runtime integration tests",
)
@unittest.skipIf(
    AER_LOCAL_GUARD,
    "IBM Runtime local testing uses Aer-backed fake backends and is guarded on macOS arm64 with Python 3.14+ in this environment.",
)
class IBMRuntimeLocalTestingIntegrationTests(unittest.TestCase):
    """Verify the IBM Runtime wrapper against local testing mode when available."""

    def test_ibm_runtime_executor_accepts_fake_backend_local_mode(self) -> None:
        from qiskit import QuantumCircuit
        from qiskit_ibm_runtime.fake_provider import FakeManilaV2

        circuit = QuantumCircuit(1)
        circuit.ry(math.pi / 4, 0)
        observable = make_pauli_observable(
            name="z_expectation",
            terms={"Z": 1.0},
            physical_meaning="Infrastructure-only Pauli-Z observable.",
        )
        result = IBMRuntimeEstimatorExecutor().run(
            circuit,
            observable,
            request=BackendRequest(
                tier=ExecutionTier.IBM_HARDWARE,
                backend_name="FakeManilaV2",
                precision=0.1,
                optimization_level=1,
            ),
            backend=FakeManilaV2(),
            transpile_for_backend=True,
        )
        self.assertGreaterEqual(result.evaluations[0].value, -1.0)
        self.assertLessEqual(result.evaluations[0].value, 1.0)
        self.assertTrue(result.provenance.metadata["service"]["local_testing_mode"])
