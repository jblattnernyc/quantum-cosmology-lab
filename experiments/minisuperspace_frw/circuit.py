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
    ground_state_data,
    ground_state_rotation_angle,
    load_experiment_definition,
)


def build_ground_state_circuit(parameters: MinisuperspaceFRWParameters):
    """Build the circuit that prepares the benchmark ground state."""

    qiskit = require_dependency(
        "qiskit",
        "construct the reduced FRW minisuperspace circuit",
    )
    circuit = qiskit.QuantumCircuit(
        parameters.qubit_count,
        name="frw_minisuperspace_ground_state",
    )
    rotation_angle = ground_state_rotation_angle(parameters)
    if rotation_angle is not None:
        circuit.ry(rotation_angle, 0)
        state_preparation = "ground_state_rotation"
    else:
        _, ground_state = ground_state_data(parameters)
        state_preparation_library = require_dependency(
            "qiskit.circuit.library",
            "construct multi-qubit state-preparation circuits for minisuperspace refinements",
        )
        circuit.append(
            state_preparation_library.StatePreparation(ground_state),
            range(parameters.qubit_count),
        )
        circuit = circuit.decompose(reps=8)
        state_preparation = "state_preparation"
    circuit.metadata = {
        "experiment": "minisuperspace_frw",
        "state_preparation": state_preparation,
    }
    return circuit


def build_ground_state_artifact(
    parameters: MinisuperspaceFRWParameters,
) -> CircuitArtifact:
    """Return the structured circuit artifact used by the shared package."""

    rotation_angle = ground_state_rotation_angle(parameters)
    return CircuitArtifact(
        name="frw_minisuperspace_ground_state",
        qubit_count=parameters.qubit_count,
        parameter_values={} if rotation_angle is None else {"theta": rotation_angle},
        construction_summary=(
            "Exact benchmark ground-state preparation for the reduced FRW "
            "minisuperspace model defined by the selected configuration."
        ),
        payload=build_ground_state_circuit(parameters),
        metadata={
            "qubit_encoding": (
                "|0> -> lower scale-factor bin, |1> -> higher scale-factor bin"
                if parameters.qubit_count == 1
                else "Binary encoding of retained positive-scale-factor bins across two qubits"
            ),
            "rotation_angle": rotation_angle,
            "retained_scale_factor_bins": list(parameters.scale_factor_bins),
            "model_variant": parameters.model_variant,
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
