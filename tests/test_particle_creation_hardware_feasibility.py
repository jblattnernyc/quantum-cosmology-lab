"""Tests for particle-creation transpilation-only feasibility evidence."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import platform
import tempfile
import unittest
from unittest.mock import patch

from tests.path_setup import ensure_src_path

ensure_src_path()

from experiments.particle_creation_flrw.common import load_experiment_definition
from experiments.particle_creation_flrw.hardware_feasibility import (
    hardware_feasibility_policy,
    hardware_feasibility_to_serializable,
    run_hardware_feasibility_study,
    write_hardware_feasibility_artifacts,
)
from qclab.backends import instantiate_local_testing_backend


class ParticleCreationHardwareFeasibilityTests(unittest.TestCase):
    """Verify structural metrics without permitting backend execution."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.experiment = load_experiment_definition()
        cls.policy = hardware_feasibility_policy(cls.experiment)
        cls.backend = instantiate_local_testing_backend(cls.policy.backend_class)
        with patch.object(cls.backend, "run") as backend_run:
            cls.study = run_hardware_feasibility_study(
                cls.experiment,
                backend=cls.backend,
            )
        backend_run.assert_not_called()

    def test_policy_is_exploratory_deterministic_and_deferred(self) -> None:
        self.assertEqual(self.policy.status, "exploratory")
        self.assertEqual(self.policy.backend_class, "FakeManilaV2")
        self.assertEqual(self.policy.time_steps, (6, 12, 24))
        self.assertEqual(self.policy.transpiler_seeds, (11, 29, 47, 71, 101))
        self.assertEqual(self.policy.optimization_level, 1)
        self.assertEqual(self.policy.translation_method, "translator")
        self.assertEqual(self.policy.live_hardware_recommendation, "defer")
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            replace(self.policy, time_steps=(12, 6, 24))

    def test_study_records_each_seed_without_execution(self) -> None:
        self.assertEqual(
            len(self.study.records),
            len(self.policy.time_steps) * len(self.policy.transpiler_seeds),
        )
        self.assertEqual(
            {
                (record.time_steps, record.transpiler_seed)
                for record in self.study.records
            },
            {
                (time_steps, seed)
                for time_steps in self.policy.time_steps
                for seed in self.policy.transpiler_seeds
            },
        )
        payload = hardware_feasibility_to_serializable(
            self.experiment,
            self.study,
        )
        self.assertFalse(payload["execution_performed"])
        self.assertFalse(payload["runtime_service_created"])
        self.assertFalse(payload["job_submitted"])
        self.assertEqual(
            payload["decision"]["live_hardware_recommendation"],
            "defer",
        )
        prerequisite = payload["prerequisites"]["independent_validation"]
        expected_digest = hashlib.sha256(
            self.experiment.artifacts.independent_validation_json.read_bytes()
        ).hexdigest()
        self.assertEqual(
            prerequisite["artifact_path"],
            "data/processed/particle_creation_flrw/independent_validation.json",
        )
        self.assertEqual(prerequisite["artifact_sha256"], expected_digest)
        self.assertEqual(prerequisite["digest_scope"], "exact_file_bytes")
        self.assertEqual(prerequisite["lineage_status"], "current")
        self.assertTrue(prerequisite["passed"])
        self.assertTrue(prerequisite["stored_content_matches_fresh_computation"])
        self.assertEqual(
            prerequisite["lineage_id"],
            payload["validation_context"]["lineage_id"],
        )
        self.assertEqual(payload["software"]["python"], platform.python_version())

    def test_transpilation_metrics_expose_noise_discretization_tradeoff(self) -> None:
        aggregates = {record.time_steps: record for record in self.study.aggregates}
        self.assertEqual(set(aggregates), {6, 12, 24})
        for time_steps, record in aggregates.items():
            self.assertEqual(record.logical_two_qubit_gate_count, 2 * time_steps)
            self.assertGreaterEqual(
                record.median_two_qubit_gate_count,
                record.logical_two_qubit_gate_count,
            )
            self.assertTrue(record.all_initial_pairs_adjacent)
            self.assertEqual(record.maximum_surviving_swap_count, 0)
            self.assertGreaterEqual(record.median_two_qubit_gate_error_proxy, 0.0)
            self.assertLess(record.median_two_qubit_gate_error_proxy, 1.0)
            self.assertGreaterEqual(record.median_aggregate_gate_error_proxy, 0.0)
            self.assertLess(record.median_aggregate_gate_error_proxy, 1.0)

        self.assertEqual(self.study.preferred_time_steps_by_hardware_cost, 6)
        self.assertLess(
            aggregates[6].median_two_qubit_gate_error_proxy,
            aggregates[12].median_two_qubit_gate_error_proxy,
        )
        self.assertLess(
            aggregates[12].median_two_qubit_gate_error_proxy,
            aggregates[24].median_two_qubit_gate_error_proxy,
        )
        self.assertGreater(
            aggregates[6].continuum_maximum_observable_error,
            aggregates[12].continuum_maximum_observable_error,
        )
        self.assertGreater(
            aggregates[12].continuum_maximum_observable_error,
            aggregates[24].continuum_maximum_observable_error,
        )

    def test_artifact_writers_preserve_no_execution_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            outputs = write_hardware_feasibility_artifacts(
                self.experiment,
                self.study,
                json_path=temp_root / "hardware_feasibility.json",
                report_path=temp_root / "hardware_feasibility_report.md",
                table_path=temp_root / "hardware_feasibility_summary.md",
            )
            payload = json.loads(
                outputs["hardware_feasibility_json"].read_text(encoding="utf-8")
            )
            report = outputs["hardware_feasibility_report_markdown"].read_text(
                encoding="utf-8"
            )
            table = outputs["hardware_feasibility_table_markdown"].read_text(
                encoding="utf-8"
            )
        self.assertFalse(payload["execution_performed"])
        self.assertFalse(payload["job_submitted"])
        self.assertIn("Live hardware recommendation: DEFER", report)
        self.assertIn("No circuit was executed", report)
        self.assertIn("|6|24|12|", table)

    def test_report_uses_selected_and_highest_configured_time_steps(self) -> None:
        reordered_study = replace(
            self.study,
            aggregates=tuple(reversed(self.study.aggregates)),
            preferred_time_steps_by_hardware_cost=12,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            outputs = write_hardware_feasibility_artifacts(
                self.experiment,
                reordered_study,
                json_path=temp_root / "hardware_feasibility.json",
                report_path=temp_root / "hardware_feasibility_report.md",
                table_path=temp_root / "hardware_feasibility_summary.md",
            )
            report = outputs["hardware_feasibility_report_markdown"].read_text(
                encoding="utf-8"
            )
        self.assertIn("`N = 12` has the lowest structural hardware cost", report)
        self.assertIn("Retain `N = 12`", report)
        self.assertIn("At `N = 24`", report)


if __name__ == "__main__":
    unittest.main()
