"""Concrete scalar benchmark helpers."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from qclab.benchmarks.base import BenchmarkResult


@dataclass(frozen=True)
class CallableScalarBenchmark:
    """Benchmark wrapper for a closed-form or trusted scalar callable."""

    name: str
    evaluation_callable: Callable[..., float]
    scientific_context: str
    parameters: Mapping[str, Any] = field(default_factory=dict)
    units: str = "dimensionless"
    metadata: dict[str, Any] = field(default_factory=dict)

    def evaluate(self) -> BenchmarkResult:
        """Evaluate the callable and package the scalar result."""

        value = float(self.evaluation_callable(**dict(self.parameters)))
        return BenchmarkResult(
            name=self.name,
            value=value,
            units=self.units,
            reference_summary=self.scientific_context,
            parameters=dict(self.parameters),
            metadata=dict(self.metadata),
        )


def evaluate_benchmark_suite(
    benchmarks: Iterable[CallableScalarBenchmark],
) -> tuple[BenchmarkResult, ...]:
    """Evaluate a collection of scalar benchmarks."""

    return tuple(benchmark.evaluate() for benchmark in benchmarks)
