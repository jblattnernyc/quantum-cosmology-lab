"""Circuit construction for the reduced Grand-Unification-Epoch-context toy model."""

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

from experiments.grand_unification_epoch_toy.common import (
    DEFAULT_CONFIG_PATH,
    GrandUnificationToyParameters,
    ground_state_data,
    load_experiment_definition,
)


def build_ground_state_circuit(parameters: GrandUnificationToyParameters):
    """Build the circuit that prepares the benchmark ground state."""

    qiskit = require_dependency(
        "qiskit",
        "construct the Grand-Unification-Epoch-context toy circuit",
    )
    state_preparation_library = require_dependency(
        "qiskit.circuit.library",
        "construct state-preparation circuits for the two-site Z2 toy model",
    )
    _, ground_state = ground_state_data(parameters)
    circuit = qiskit.QuantumCircuit(2, name="grand_unification_epoch_toy_ground_state")
    circuit.append(state_preparation_library.StatePreparation(ground_state), range(2))
    circuit = circuit.decompose(reps=8)
    circuit.metadata = {
        "experiment": "grand_unification_epoch_toy",
        "state_preparation": "exact_ground_state_preparation",
    }
    return circuit


def build_ground_state_artifact(
    parameters: GrandUnificationToyParameters,
) -> CircuitArtifact:
    """Return the structured circuit artifact used by the shared package."""

    _, ground_state = ground_state_data(parameters)
    return CircuitArtifact(
        name="grand_unification_epoch_toy_ground_state",
        qubit_count=2,
        parameter_values={
            f"ground_state_amplitude_{index}": float(amplitude)
            for index, amplitude in enumerate(ground_state)
        },
        construction_summary=(
            "Two-qubit exact ground-state preparation for the reduced Z2 "
            "symmetry-breaking toy Hamiltonian."
        ),
        payload=build_ground_state_circuit(parameters),
        metadata={
            "qubit_encoding": "q0 and q1 encode the two retained Z2 order-parameter sites",
            "retained_basis": "|00>, |01>, |10>, |11>",
        },
    )


def main(argv: list[str] | None = None) -> int:
    """Print the default ground-state circuit."""

    parser = argparse.ArgumentParser(
        description=(
            "Construct the reduced Grand-Unification-Epoch-context toy circuit."
        )
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    experiment = load_experiment_definition(args.config)
    circuit = build_ground_state_circuit(experiment.parameters)
    print(circuit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

