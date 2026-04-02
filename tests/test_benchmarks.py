"""Benchmark-helper tests."""

from __future__ import annotations

import math
import unittest

from tests.path_setup import ensure_src_path

ensure_src_path()

from qclab.benchmarks import CallableScalarBenchmark, evaluate_benchmark_suite


class BenchmarkHelperTests(unittest.TestCase):
    """Verify scalar benchmark helpers."""

    def test_callable_scalar_benchmark_evaluates_and_preserves_parameters(self) -> None:
        benchmark = CallableScalarBenchmark(
            name="cosine_reference",
            evaluation_callable=lambda x: math.cos(x),
            scientific_context="Closed-form cosine benchmark.",
            parameters={"x": math.pi / 3},
        )
        result = benchmark.evaluate()
        self.assertAlmostEqual(result.value, 0.5)
        self.assertEqual(result.parameters["x"], math.pi / 3)

    def test_benchmark_suite_evaluates_all_members(self) -> None:
        suite = (
            CallableScalarBenchmark(
                name="zero_reference",
                evaluation_callable=lambda value: value,
                scientific_context="Identity benchmark.",
                parameters={"value": 0.0},
            ),
            CallableScalarBenchmark(
                name="unity_reference",
                evaluation_callable=lambda value: value,
                scientific_context="Identity benchmark.",
                parameters={"value": 1.0},
            ),
        )
        results = evaluate_benchmark_suite(suite)
        self.assertEqual(tuple(result.value for result in results), (0.0, 1.0))
