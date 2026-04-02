"""Shared infrastructure smoke example.

The functions in this module intentionally avoid cosmological claims. They
exist only to verify that the reusable repository infrastructure can pass a
small, clearly labeled toy object through benchmark, circuit, and analysis
layers during Phase 1 development.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from qclab.analysis.comparison import ComparisonRecord, compare_scalar_observable
from qclab.benchmarks.base import BenchmarkResult
from qclab.benchmarks.toy import SingleQubitRotationZBenchmark
from qclab.circuits.base import CircuitArtifact
from qclab.circuits.toy import build_infrastructure_toy_circuit
from qclab.observables.base import ObservableDefinition


@dataclass(frozen=True)
class FoundationPipelineResult:
    """Result bundle for the infrastructure smoke example."""

    benchmark: BenchmarkResult
    circuit: CircuitArtifact
    observable: ObservableDefinition
    comparison: ComparisonRecord
    interpretation_note: str


def run_foundation_smoke_example(rotation_angle: float) -> FoundationPipelineResult:
    """Run a minimal benchmark-circuit-analysis pass for infrastructure tests."""

    benchmark = SingleQubitRotationZBenchmark(rotation_angle=rotation_angle).evaluate()
    circuit = build_infrastructure_toy_circuit(rotation_angle=rotation_angle)
    observable = ObservableDefinition(
        name="toy_pauli_z_expectation",
        operator_label="Z",
        physical_meaning=(
            "Infrastructure-only scalar used to test shared repository plumbing. "
            "It has no cosmological interpretation."
        ),
        measurement_basis="computational_basis",
        metadata={"status": "infrastructure_validation_only"},
    )
    analytic_value = math.cos(rotation_angle)
    comparison = compare_scalar_observable(
        observable_name=observable.name,
        benchmark_value=benchmark.value,
        candidate_value=analytic_value,
        interpretation=(
            "Closed-form agreement check for the infrastructure smoke example. "
            "This record is not an official scientific result."
        ),
    )
    return FoundationPipelineResult(
        benchmark=benchmark,
        circuit=circuit,
        observable=observable,
        comparison=comparison,
        interpretation_note=(
            "Infrastructure-only toy example. It exists to validate shared "
            "repository machinery before model-specific experiment code is added."
        ),
    )
