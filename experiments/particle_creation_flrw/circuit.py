"""Circuit construction for the reduced FLRW particle-creation toy model."""

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

from experiments.particle_creation_flrw.common import (
    DEFAULT_CONFIG_PATH,
    ParticleCreationFLRWParameters,
    evolution_slices,
    load_experiment_definition,
)


def build_particle_creation_circuit(parameters: ParticleCreationFLRWParameters):
    """Build the two-qubit circuit for the discrete particle-creation model."""

    qiskit = require_dependency(
        "qiskit",
        "construct the reduced FLRW particle-creation circuit",
    )
    circuit = qiskit.QuantumCircuit(2, name="flrw_particle_creation")
    for evolution_slice in evolution_slices(parameters):
        circuit.rz(-evolution_slice.phase_angle, 0)
        circuit.rz(-evolution_slice.phase_angle, 1)
        circuit.rxx(evolution_slice.squeezing_angle, 0, 1)
        circuit.ryy(-evolution_slice.squeezing_angle, 0, 1)
    circuit.metadata = {
        "experiment": "particle_creation_flrw",
        "time_steps": parameters.time_steps,
        "state_preparation": "discrete_pair_creation_from_vacuum",
    }
    return circuit


def build_particle_creation_artifact(
    parameters: ParticleCreationFLRWParameters,
) -> CircuitArtifact:
    """Return the structured circuit artifact used by the shared package."""

    slices = evolution_slices(parameters)
    return CircuitArtifact(
        name="flrw_particle_creation",
        qubit_count=2,
        parameter_values={
            "delta_eta": parameters.delta_eta,
            "time_steps": float(parameters.time_steps),
            "total_phase_angle": float(sum(item.phase_angle for item in slices)),
            "total_squeezing_angle": float(
                sum(item.squeezing_angle for item in slices)
            ),
        },
        construction_summary=(
            "Two-qubit stepwise evolution from the vacuum using discrete "
            "frequency phases and Bogoliubov-inspired pairing rotations."
        ),
        payload=build_particle_creation_circuit(parameters),
        metadata={
            "qubit_encoding": "q0 -> k mode occupation, q1 -> -k mode occupation",
            "retained_subspace": "|00>, |11>",
            "time_steps": parameters.time_steps,
        },
    )


def main(argv: list[str] | None = None) -> int:
    """Print the default particle-creation circuit."""

    parser = argparse.ArgumentParser(
        description="Construct the reduced FLRW particle-creation circuit."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    experiment = load_experiment_definition(args.config)
    circuit = build_particle_creation_circuit(experiment.parameters)
    print(circuit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
