"""Infrastructure-only benchmark implementations."""

from __future__ import annotations

import math
from dataclasses import dataclass

from qclab.benchmarks.base import BenchmarkResult


@dataclass(frozen=True)
class SingleQubitRotationZBenchmark:
    """Closed-form reference for an infrastructure-only toy circuit."""

    rotation_angle: float
    name: str = "single_qubit_rotation_z_expectation"

    def evaluate(self) -> BenchmarkResult:
        return BenchmarkResult(
            name=self.name,
            value=math.cos(self.rotation_angle),
            reference_summary=(
                "Analytic expectation value for a one-qubit RY(theta) rotation "
                "measured in the Pauli-Z basis. Used only for infrastructure "
                "validation."
            ),
            metadata={
                "analytic_expression": "cos(theta)",
                "status": "infrastructure_validation_only",
            },
        )
