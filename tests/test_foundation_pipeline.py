"""Smoke tests for the Phase 1 shared infrastructure example."""

from __future__ import annotations

import math
import unittest

from tests.path_setup import ensure_src_path

ensure_src_path()

from qclab.backends.base import ExecutionTier, validate_execution_progression
from qclab.utils.foundation import run_foundation_smoke_example


class FoundationPipelineTests(unittest.TestCase):
    """Verify the minimal shared benchmark-circuit-analysis pass."""

    def test_smoke_example_produces_zero_error_against_closed_form(self) -> None:
        result = run_foundation_smoke_example(rotation_angle=math.pi / 3)
        self.assertEqual(result.circuit.qubit_count, 1)
        self.assertAlmostEqual(result.benchmark.value, 0.5)
        self.assertAlmostEqual(result.comparison.absolute_error, 0.0)
        self.assertIn("not an official scientific result", result.comparison.interpretation)

    def test_hardware_progression_requires_noisy_validation(self) -> None:
        with self.assertRaises(ValueError):
            validate_execution_progression(
                ExecutionTier.IBM_HARDWARE,
                benchmark_complete=True,
                noisy_local_complete=False,
            )
