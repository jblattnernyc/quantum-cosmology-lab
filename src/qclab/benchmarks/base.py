"""Benchmark interfaces for exact or trusted reference calculations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class BenchmarkResult:
    """Numeric result from an exact or trusted reference workflow."""

    name: str
    value: float
    units: str = "dimensionless"
    reference_summary: str = ""
    uncertainty: float = 0.0
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("BenchmarkResult.name must be non-empty.")
        if self.uncertainty < 0:
            raise ValueError("BenchmarkResult.uncertainty must be non-negative.")


class BenchmarkProtocol(Protocol):
    """Protocol for benchmark providers used by shared infrastructure."""

    name: str

    def evaluate(self) -> BenchmarkResult:
        """Return a reference result suitable for later comparison."""
