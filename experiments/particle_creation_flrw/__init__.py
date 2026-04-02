"""Reduced FLRW particle-creation experiment package."""

from pathlib import Path
import sys

repository_root = Path(__file__).resolve().parents[2]
source_root = repository_root / "src"
if str(source_root) not in sys.path:
    sys.path.insert(0, str(source_root))

from experiments.particle_creation_flrw.benchmark import (
    ParticleCreationFLRWBenchmark,
    compute_benchmark,
)
from experiments.particle_creation_flrw.circuit import build_particle_creation_circuit
from experiments.particle_creation_flrw.common import (
    DEFAULT_CONFIG_PATH,
    ParticleCreationFLRWExperiment,
    ParticleCreationFLRWParameters,
    load_experiment_definition,
)
from experiments.particle_creation_flrw.observables import build_observables

__all__ = [
    "DEFAULT_CONFIG_PATH",
    "ParticleCreationFLRWBenchmark",
    "ParticleCreationFLRWExperiment",
    "ParticleCreationFLRWParameters",
    "build_observables",
    "build_particle_creation_circuit",
    "compute_benchmark",
    "load_experiment_definition",
]
