"""Circuit construction for the reduced FRW minisuperspace toy model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from qclab.circuits.base import CircuitArtifact
from qclab.utils.optional import require_dependency

from experiments.minisuperspace_frw.common import (
    DEFAULT_CONFIG_PATH,
    MinisuperspaceFRWParameters,
    ground_state_rotation_angle,
    load_experiment_definition,
)


def build_ground_state_circuit(parameters: MinisuperspaceFRWParameters):
    """Build the one-qubit circuit for the benchmark ground state."""

    qiskit = require_dependency(
        "qiskit",
        "construct the reduced FRW minisuperspace circuit",
    )
    circuit = qiskit.QuantumCircuit(1, name="frw_minisuperspace_ground_state")
    circuit.ry(ground_state_rotation_angle(parameters), 0)
    circuit.metadata = {
        "experiment": "minisuperspace_frw",
        "state_preparation": "ground_state_rotation",
    }
    return circuit


def build_ground_state_artifact(
    parameters: MinisuperspaceFRWParameters,
) -> CircuitArtifact:
    """Return the structured circuit artifact used by the shared package."""

    rotation_angle = ground_state_rotation_angle(parameters)
    return CircuitArtifact(
        name="frw_minisuperspace_ground_state",
        qubit_count=1,
        parameter_values={"theta": rotation_angle},
        construction_summary=(
            "Single-qubit RY rotation that prepares the exact ground state of "
            "the reduced two-state FRW minisuperspace toy Hamiltonian."
        ),
        payload=build_ground_state_circuit(parameters),
        metadata={
            "qubit_encoding": "|0> -> lower scale-factor bin, |1> -> higher scale-factor bin",
            "rotation_angle": rotation_angle,
        },
    )


def main(argv: list[str] | None = None) -> int:
    """Print the default ground-state circuit."""

    parser = argparse.ArgumentParser(
        description="Construct the reduced FRW minisuperspace state-preparation circuit."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    experiment = load_experiment_definition(args.config)
    circuit = build_ground_state_circuit(experiment.parameters)
    print(circuit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
