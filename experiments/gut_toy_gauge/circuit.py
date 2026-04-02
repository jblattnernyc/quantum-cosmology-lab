"""Circuit construction for the reduced two-link Z2 gauge toy model."""

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

from experiments.gut_toy_gauge.common import (
    DEFAULT_CONFIG_PATH,
    GutToyGaugeParameters,
    ground_state_rotation_angle,
    load_experiment_definition,
)


def build_ground_state_circuit(parameters: GutToyGaugeParameters):
    """Build the two-qubit circuit for the benchmark ground state."""

    qiskit = require_dependency(
        "qiskit",
        "construct the reduced two-link Z2 gauge circuit",
    )
    circuit = qiskit.QuantumCircuit(2, name="gut_toy_gauge_ground_state")
    circuit.ry(ground_state_rotation_angle(parameters), 0)
    circuit.cx(0, 1)
    circuit.metadata = {
        "experiment": "gut_toy_gauge",
        "state_preparation": "gauge_invariant_ground_state_rotation",
    }
    return circuit


def build_ground_state_artifact(parameters: GutToyGaugeParameters) -> CircuitArtifact:
    """Return the structured circuit artifact used by the shared package."""

    rotation_angle = ground_state_rotation_angle(parameters)
    return CircuitArtifact(
        name="gut_toy_gauge_ground_state",
        qubit_count=2,
        parameter_values={"theta": rotation_angle},
        construction_summary=(
            "Two-qubit RY plus CX preparation of the exact gauge-invariant "
            "ground state of the reduced two-link Z2 gauge toy Hamiltonian."
        ),
        payload=build_ground_state_circuit(parameters),
        metadata={
            "qubit_encoding": "q0 -> first retained Z2 link, q1 -> second retained Z2 link",
            "physical_sector": "|00>, |11>",
            "rotation_angle": rotation_angle,
        },
    )


def main(argv: list[str] | None = None) -> int:
    """Print the default ground-state circuit."""

    parser = argparse.ArgumentParser(
        description="Construct the reduced two-link Z2 gauge toy-model circuit."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    experiment = load_experiment_definition(args.config)
    circuit = build_ground_state_circuit(experiment.parameters)
    print(circuit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
