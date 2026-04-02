"""Tests for the Phase 6 milestone-report and archival-release layer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.path_setup import ensure_src_path

ensure_src_path()

from qclab.analysis.milestones import (
    collect_phase6_snapshot,
    write_archival_release_manifest,
    write_phase6_milestone_report,
)


class Phase6MilestoneTests(unittest.TestCase):
    """Verify the repository-level Phase 6 dissemination helpers."""

    def test_collect_phase6_snapshot_reads_official_experiments_and_live_ibm_runs(self) -> None:
        snapshot = collect_phase6_snapshot()
        self.assertEqual(snapshot.roadmap_phase, 6)
        self.assertEqual(snapshot.package_version, "1.0.0")
        experiment_names = tuple(
            record.experiment_name for record in snapshot.official_experiments
        )
        self.assertEqual(
            experiment_names,
            (
                "minisuperspace_frw",
                "particle_creation_flrw",
                "gut_toy_gauge",
            ),
        )
        for record in snapshot.official_experiments:
            with self.subTest(experiment=record.experiment_name):
                self.assertTrue(record.readme_path.exists())
                self.assertTrue(record.model_path.exists())
                self.assertTrue(record.results_path.exists())
                self.assertTrue(record.benchmark_json.exists())
                self.assertTrue(record.exact_local_json.exists())
                self.assertTrue(record.noisy_local_json.exists())
                self.assertTrue(record.runs_manifest_path.exists())
                self.assertIsNotNone(record.latest_live_ibm_run)
                self.assertEqual(record.live_ibm_run_count, 1)
                self.assertFalse(record.latest_live_ibm_run.local_testing_mode)
                self.assertEqual(record.latest_live_ibm_run.backend_name, "ibm_fez")

    def test_phase6_milestone_report_writer_mentions_governance_and_boundary(self) -> None:
        snapshot = collect_phase6_snapshot()
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "phase6_report.md"
            write_phase6_milestone_report(
                snapshot,
                milestone_id="v1.0.0-phase6-test",
                output_path=output_path,
            )
            report_text = output_path.read_text(encoding="utf-8")
        self.assertIn("# Quantum Cosmology Lab Milestone Report", report_text)
        self.assertIn("Phase 6 Governance Deliverables", report_text)
        self.assertIn("minisuperspace_frw", report_text)
        self.assertIn("particle_creation_flrw", report_text)
        self.assertIn("gut_toy_gauge", report_text)
        self.assertIn("Phase 6 only", report_text)

    def test_archival_release_manifest_writer_serializes_official_records(self) -> None:
        snapshot = collect_phase6_snapshot()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            milestone_report = temp_root / "phase6_report.md"
            manifest_path = temp_root / "phase6_manifest.json"
            write_phase6_milestone_report(
                snapshot,
                milestone_id="v1.0.0-phase6-test",
                output_path=milestone_report,
            )
            write_archival_release_manifest(
                snapshot,
                release_id="v1.0.0-phase6-test",
                milestone_report_path=milestone_report,
                output_path=manifest_path,
            )
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["release_id"], "v1.0.0-phase6-test")
        self.assertEqual(payload["roadmap_phase"], 6)
        self.assertEqual(payload["repository_root"], ".")
        self.assertFalse(payload["repository_policies"]["phase7_or_later_implemented"])
        self.assertEqual(len(payload["official_experiments"]), 3)
        for record in payload["official_experiments"]:
            with self.subTest(experiment=record["experiment_name"]):
                self.assertEqual(record["latest_live_ibm_run"]["backend_name"], "ibm_fez")
                self.assertFalse(record["latest_live_ibm_run"]["local_testing_mode"])
                self.assertFalse(record["documents"]["readme_markdown"].startswith("/"))
                self.assertTrue(record["runs_manifest_jsonl"].endswith("ibm_runtime_runs.jsonl"))
