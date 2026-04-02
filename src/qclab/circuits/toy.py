"""Infrastructure-only circuit builders.

These utilities are intentionally non-cosmological. They exist only to verify
that the shared repository machinery can pass a small object through circuit
construction, benchmark comparison, and analysis without implying an official
scientific experiment.
"""

from __future__ import annotations

from qclab.circuits.base import CircuitArtifact
from qclab.utils.optional import require_dependency


def build_infrastructure_toy_circuit(rotation_angle: float) -> CircuitArtifact:
    """Return a metadata-only single-qubit rotation specification."""

    return CircuitArtifact(
        name="infrastructure_toy_single_qubit_rotation",
        qubit_count=1,
        parameter_values={"theta": rotation_angle},
        construction_summary=(
            "Single-qubit rotation used only for shared infrastructure "
            "validation. This object is not a cosmological model."
        ),
        metadata={
            "gate_sequence": ("ry(theta, q0)",),
            "status": "infrastructure_validation_only",
        },
    )


def build_qiskit_infrastructure_toy_circuit(rotation_angle: float) -> CircuitArtifact:
    """Return the same infrastructure toy circuit with a Qiskit payload.

    The function performs a lazy import so that the repository can still be
    imported in environments where the scientific stack has not yet been
    installed.
    """

    qiskit = require_dependency(
        "qiskit",
        "construct Qiskit circuits for shared infrastructure validation",
    )
    quantum_circuit = qiskit.QuantumCircuit(1)
    quantum_circuit.ry(rotation_angle, 0)
    return CircuitArtifact(
        name="infrastructure_toy_single_qubit_rotation",
        qubit_count=1,
        parameter_values={"theta": rotation_angle},
        construction_summary=(
            "Single-qubit rotation used only for shared infrastructure "
            "validation. This object is not a cosmological model."
        ),
        payload=quantum_circuit,
        metadata={
            "gate_sequence": ("ry(theta, q0)",),
            "status": "infrastructure_validation_only",
        },
    )
