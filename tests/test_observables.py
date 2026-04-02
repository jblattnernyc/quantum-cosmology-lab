"""Observable-construction tests."""

from __future__ import annotations

import unittest

from tests.path_setup import ensure_src_path

ensure_src_path()

from qclab.observables import (
    ObservableDefinition,
    infer_pauli_qubit_count,
    make_pauli_observable,
    observable_to_qiskit,
)
from qclab.observables.base import PauliTerm


class ObservableConstructionTests(unittest.TestCase):
    """Verify observable construction and normalization helpers."""

    def test_make_pauli_observable_builds_explicit_pauli_terms(self) -> None:
        observable = make_pauli_observable(
            name="single_qubit_z",
            terms={"Z": 1.0},
            physical_meaning="Infrastructure-only Pauli-Z observable.",
        )
        self.assertEqual(observable.pauli_terms, (PauliTerm(label="Z", coefficient=1.0),))
        self.assertEqual(infer_pauli_qubit_count(observable), 1)
        self.assertEqual(observable_to_qiskit(observable), "Z")

    def test_observable_rejects_inconsistent_pauli_term_lengths(self) -> None:
        with self.assertRaises(ValueError):
            ObservableDefinition(
                name="bad_observable",
                operator_label="X + ZZ",
                physical_meaning="Invalid mixed-length Pauli decomposition.",
                measurement_basis="pauli",
                pauli_terms=(PauliTerm("X"), PauliTerm("ZZ")),
            )
