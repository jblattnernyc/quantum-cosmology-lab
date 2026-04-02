"""Benchmark interfaces and infrastructure smoke examples."""

from qclab.benchmarks.base import BenchmarkResult
from qclab.benchmarks.scalar import CallableScalarBenchmark, evaluate_benchmark_suite
from qclab.benchmarks.toy import SingleQubitRotationZBenchmark

__all__ = [
    "BenchmarkResult",
    "CallableScalarBenchmark",
    "SingleQubitRotationZBenchmark",
    "evaluate_benchmark_suite",
]
