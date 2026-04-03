"""Tests for the phase-neutral current repository-state layer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.path_setup import ensure_src_path

ensure_src_path()

from qclab.analysis.repository_state import (
    collect_current_repository_snapshot,
    discover_current_official_experiment_names,
    write_current_official_experiment_manifest,
    write_current_repository_report,
)


class CurrentRepositoryStateTests(unittest.TestCase):
    """Verify the current official experiment discovery and reporting helpers."""

    def test_discovery_includes_founding_official_experiments(self) -> None:
        experiment_names = set(discover_current_official_experiment_names())
        self.assertTrue(
            {
                "minisuperspace_frw",
                "particle_creation_flrw",
                "gut_toy_gauge",
            }.issubset(experiment_names)
        )

    def test_current_snapshot_loads_phase_neutral_official_records(self) -> None:
        snapshot = collect_current_repository_snapshot(
            generated_at_utc="2026-04-03T00:00:00+00:00"
        )
        self.assertEqual(snapshot.package_version, "1.1.0")
        self.assertEqual(snapshot.generated_at_utc, "2026-04-03T00:00:00+00:00")
        experiment_names = {record.experiment_name for record in snapshot.official_experiments}
        self.assertTrue(
            {
                "minisuperspace_frw",
                "particle_creation_flrw",
                "gut_toy_gauge",
            }.issubset(experiment_names)
        )
        for record in snapshot.official_experiments:
            with self.subTest(experiment=record.experiment_name):
                self.assertTrue(record.readme_path.exists())
                self.assertTrue(record.model_path.exists())
                self.assertTrue(record.results_path.exists())
                self.assertTrue(record.config_path.exists())
                self.assertTrue(record.benchmark_json.exists())
                self.assertTrue(record.exact_local_json.exists())
                self.assertTrue(record.noisy_local_json.exists())

    def test_current_repository_report_writer_mentions_active_governance(self) -> None:
        snapshot = collect_current_repository_snapshot(
            generated_at_utc="2026-04-03T00:00:00+00:00"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "current_official_experiments.md"
            write_current_repository_report(snapshot, output_path=output_path)
            report_text = output_path.read_text(encoding="utf-8")
        self.assertIn("# Quantum Cosmology Lab Current Official Experiment Report", report_text)
        self.assertIn("2026-04-03T00:00:00+00:00", report_text)
        self.assertIn("AGENTS.md", report_text)
        self.assertIn("minisuperspace_frw", report_text)
        self.assertIn("particle_creation_flrw", report_text)
        self.assertIn("gut_toy_gauge", report_text)
        self.assertIn("does not alter the preserved historical Phase 6", report_text)

    def test_current_official_experiment_manifest_writer_serializes_records(self) -> None:
        snapshot = collect_current_repository_snapshot(
            generated_at_utc="2026-04-03T00:00:00+00:00"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            report_path = temp_root / "current_official_experiments.md"
            manifest_path = temp_root / "current_official_experiments.json"
            write_current_repository_report(snapshot, output_path=report_path)
            write_current_official_experiment_manifest(
                snapshot,
                report_path=report_path,
                output_path=manifest_path,
            )
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["report_kind"], "current_official_experiments")
        self.assertEqual(payload["generated_at_utc"], "2026-04-03T00:00:00+00:00")
        self.assertEqual(payload["repository_root"], ".")
        self.assertTrue(payload["repository_policies"]["agents_primary_active_governance"])
        self.assertTrue(
            payload["repository_policies"]["plans_required_for_major_expansion_only"]
        )
        experiment_names = {record["experiment_name"] for record in payload["official_experiments"]}
        self.assertTrue(
            {
                "minisuperspace_frw",
                "particle_creation_flrw",
                "gut_toy_gauge",
            }.issubset(experiment_names)
        )
        for record in payload["official_experiments"]:
            with self.subTest(experiment=record["experiment_name"]):
                self.assertFalse(record["documents"]["readme_markdown"].startswith("/"))
                self.assertFalse(record["documents"]["config_yaml"].startswith("/"))
                self.assertTrue(record["runs_manifest_jsonl"].endswith("ibm_runtime_runs.jsonl"))

    def test_current_snapshot_normalizes_naive_generated_at_to_utc(self) -> None:
        snapshot = collect_current_repository_snapshot(generated_at_utc="2026-04-03T00:00:00")
        self.assertEqual(snapshot.generated_at_utc, "2026-04-03T00:00:00+00:00")
