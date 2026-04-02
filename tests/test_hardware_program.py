"""Tests for the shared Phase 4 hardware-and-mitigation framework."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.path_setup import ensure_src_path

ensure_src_path()

from qclab.analysis.comparison import ComparisonRecord
from qclab.backends.base import BackendRequest, ExecutionTier
from qclab.backends.execution import EstimatorExecutionResult, ExecutionProvenance
from qclab.backends.hardware import (
    backend_selection_policy_from_mapping,
    parse_ibm_runtime_options,
    resolve_ibm_runtime_artifact_paths,
    write_ibm_runtime_artifacts,
    write_hardware_report_markdown,
    write_ibm_hardware_metadata_json,
)
from qclab.observables.base import ObservableDefinition, ObservableEvaluation


class _FakeBackend:
    name = "ibm_fake_sherbrooke"
    num_qubits = 127
    max_circuits = 300

    @staticmethod
    def operation_names():
        return ["rz", "sx", "x", "ecr"]

    @staticmethod
    def calibration_id():
        return "cal-123"

    @staticmethod
    def status():
        class _Status:
            backend_name = "ibm_fake_sherbrooke"
            backend_version = "2026.1"
            operational = True
            pending_jobs = 11
            status_msg = "active"

        return _Status()

    @staticmethod
    def properties(refresh=False):
        del refresh

        class _Properties:
            last_update_date = "2026-04-01T10:30:00+00:00"

            @staticmethod
            def to_dict():
                return {
                    "backend_name": "ibm_fake_sherbrooke",
                    "last_update_date": "2026-04-01T10:30:00+00:00",
                }

        return _Properties()


class _FakeJob:
    @staticmethod
    def job_id():
        return "job-123"

    @staticmethod
    def status():
        return "DONE"

    @staticmethod
    def creation_date():
        return "2026-04-01T11:00:00+00:00"

    @staticmethod
    def session_id():
        return "session-456"

    @staticmethod
    def primitive_id():
        return "estimator"

    usage_estimation = {"quantum_seconds": 2.5}
    usage = {"quantum_seconds": 2.7}

    @staticmethod
    def metrics():
        return {"timestamps": {"created": "2026-04-01T11:00:00+00:00"}}

    @staticmethod
    def inputs():
        return {"pub_count": 1}

    @staticmethod
    def tags():
        return ["qclab", "test"]


class HardwareProgramTests(unittest.TestCase):
    """Verify Phase 4 hardware policy, metadata capture, and reporting."""

    def _build_result(
        self,
        *,
        local_testing_mode: bool = False,
        timestamp_utc: str = "2026-04-01T11:05:00+00:00",
        job_id: str = "job-123",
    ) -> EstimatorExecutionResult:
        observable = ObservableDefinition(
            name="toy_observable",
            operator_label="Z",
            physical_meaning="Infrastructure-only observable.",
            measurement_basis="pauli",
        )
        return EstimatorExecutionResult(
            request=BackendRequest(
                tier=ExecutionTier.IBM_HARDWARE,
                backend_name="ibm_fake_sherbrooke",
                precision=0.05,
                optimization_level=1,
                options={
                    "selection_policy": {"strategy": "explicit"},
                    "mitigation_policy": {"resilience_level": 1},
                },
            ),
            evaluations=(
                ObservableEvaluation(
                    observable=observable,
                    value=0.9,
                    uncertainty=0.02,
                    shots=None,
                ),
            ),
            provenance=ExecutionProvenance(
                tier=ExecutionTier.IBM_HARDWARE,
                backend_name="ibm_fake_sherbrooke",
                primitive_name="qiskit_ibm_runtime.EstimatorV2",
                job_id=job_id,
                timestamp_utc=timestamp_utc,
                metadata={
                    "service": {
                        "channel": "ibm_quantum_platform",
                        "instance": "ibm-q/open/main",
                        "local_testing_mode": local_testing_mode,
                    },
                    "backend_selection": {
                        "strategy": "explicit",
                        "requested_backend_name": "ibm_fake_sherbrooke",
                        "selected_backend_name": "ibm_fake_sherbrooke",
                    },
                    "mitigation_policy": {
                        "resilience_level": 1,
                        "measure_mitigation": True,
                        "twirling_enable_measure": True,
                    },
                    "backend_summary": {
                        "backend_class": "FakeBackend",
                        "num_qubits": 127,
                        "calibration_id": "cal-123",
                        "properties_last_update_date": "2026-04-01T10:30:00+00:00",
                        "status": {"operational": True, "pending_jobs": 11},
                    },
                    "runtime_job_summary": {
                        "job_id": "job-123",
                        "status": "DONE",
                        "creation_date": "2026-04-01T11:00:00+00:00",
                        "session_id": "session-456",
                        "usage_estimation": {"quantum_seconds": 2.5},
                    },
                },
            ),
            raw_job=_FakeJob(),
            raw_backend=_FakeBackend(),
            job_metadata={"target_precision": 0.05},
        )

    def test_parse_ibm_runtime_options_separates_policy_from_primitive_options(self) -> None:
        selection_policy, mitigation_policy, runtime_options = parse_ibm_runtime_options(
            {
                "selection_policy": {"strategy": "least_busy", "min_num_qubits": 5},
                "mitigation_policy": {"resilience_level": 2},
                "runtime_options": {
                    "environment": {"job_tags": ["qclab", "phase4"]},
                },
                "max_execution_time": 1200,
            },
            shots=4096,
        )
        self.assertEqual(selection_policy.strategy.value, "least_busy")
        self.assertEqual(selection_policy.min_num_qubits, 5)
        self.assertEqual(mitigation_policy.resilience_level, 2)
        self.assertEqual(runtime_options["default_shots"], 4096)
        self.assertEqual(runtime_options["environment"]["job_tags"], ["qclab", "phase4"])
        self.assertEqual(runtime_options["max_execution_time"], 1200)

    def test_resolve_ibm_runtime_artifact_paths_uses_local_testing_suffix(self) -> None:
        canonical_paths = resolve_ibm_runtime_artifact_paths(
            execution_json_path="data/processed/example/ibm_runtime.json",
            comparison_json_path="data/processed/example/ibm_runtime_comparisons.json",
            metadata_json_path="data/raw/example/ibm_runtime_metadata.json",
            report_markdown_path="results/reports/example/ibm_runtime_report.md",
            local_testing_mode=False,
        )
        local_testing_paths = resolve_ibm_runtime_artifact_paths(
            execution_json_path="data/processed/example/ibm_runtime.json",
            comparison_json_path="data/processed/example/ibm_runtime_comparisons.json",
            metadata_json_path="data/raw/example/ibm_runtime_metadata.json",
            report_markdown_path="results/reports/example/ibm_runtime_report.md",
            local_testing_mode=True,
        )
        self.assertTrue(str(canonical_paths["execution_json_path"]).endswith("ibm_runtime.json"))
        self.assertTrue(
            str(local_testing_paths["execution_json_path"]).endswith(
                "ibm_runtime_local_testing.json"
            )
        )
        self.assertTrue(
            str(local_testing_paths["comparison_json_path"]).endswith(
                "ibm_runtime_comparisons_local_testing.json"
            )
        )
        self.assertTrue(
            str(local_testing_paths["metadata_json_path"]).endswith(
                "ibm_runtime_metadata_local_testing.json"
            )
        )
        self.assertTrue(
            str(local_testing_paths["report_markdown_path"]).endswith(
                "ibm_runtime_report_local_testing.md"
            )
        )

    def test_backend_selection_policy_loader_supports_least_busy(self) -> None:
        policy = backend_selection_policy_from_mapping(
            {"strategy": "least_busy", "min_num_qubits": 2, "simulator": False}
        )
        self.assertEqual(policy.strategy.value, "least_busy")
        self.assertEqual(policy.min_num_qubits, 2)
        self.assertFalse(policy.simulator)

    def test_hardware_metadata_json_capture_writes_backend_and_job_payload(self) -> None:
        result = self._build_result()
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "hardware_metadata.json"
            write_ibm_hardware_metadata_json(result, output_path)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["backend_selection"]["strategy"], "explicit")
        self.assertEqual(payload["backend_calibration"]["summary"]["num_qubits"], 127)
        self.assertEqual(payload["runtime_job_payload"]["job_id"], "job-123")

    def test_hardware_report_markdown_includes_policy_and_comparison_table(self) -> None:
        result = self._build_result()
        comparison_records = [
            ComparisonRecord(
                observable_name="toy_observable",
                benchmark_value=1.0,
                candidate_value=0.9,
                absolute_error=0.1,
                relative_error=0.1,
                interpretation="Infrastructure-only comparison.",
            )
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "hardware_report.md"
            write_hardware_report_markdown(
                experiment_name="phase4_test",
                scientific_question="Does the shared hardware report preserve backend policy and comparison context?",
                result=result,
                comparison_records=comparison_records,
                benchmark_complete=True,
                exact_local_complete=True,
                noisy_local_complete=True,
                path=report_path,
                metadata_json_path=Path(temp_dir) / "hardware_metadata.json",
            )
            report_text = report_path.read_text(encoding="utf-8")
        self.assertIn("# IBM Runtime Hardware Report", report_text)
        self.assertIn("- Strategy: `explicit`", report_text)
        self.assertIn("| toy_observable | 1.000000 | 0.900000 | 0.100000 | 0.100000 | 0.020000 |", report_text)

    def test_ibm_runtime_artifacts_archive_completed_live_runs(self) -> None:
        result = self._build_result()
        comparison_records = [
            ComparisonRecord(
                observable_name="toy_observable",
                benchmark_value=1.0,
                candidate_value=0.9,
                absolute_error=0.1,
                relative_error=0.1,
                interpretation="Infrastructure-only comparison.",
            )
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            outputs = write_ibm_runtime_artifacts(
                experiment_name="phase4_test",
                scientific_question="Does the shared writer preserve canonical and archive IBM artifacts?",
                result=result,
                comparison_records=comparison_records,
                benchmark_complete=True,
                exact_local_complete=True,
                noisy_local_complete=True,
                execution_json_path=temp_root / "processed" / "ibm_runtime.json",
                comparison_json_path=temp_root / "processed" / "ibm_runtime_comparisons.json",
                metadata_json_path=temp_root / "raw" / "ibm_runtime_metadata.json",
                report_markdown_path=temp_root / "reports" / "ibm_runtime_report.md",
            )
            manifest_path = outputs["ibm_runtime_runs_manifest_jsonl"]
            manifest_lines = manifest_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(manifest_lines), 1)
            manifest_record = json.loads(manifest_lines[0])
            self.assertIn("ibm_runtime_archive_json", outputs)
            self.assertIn("ibm_runtime_archive_report_markdown", outputs)
            self.assertTrue(outputs["ibm_runtime_json"].exists())
            self.assertTrue(outputs["ibm_runtime_archive_json"].exists())
            self.assertEqual(
                outputs["ibm_runtime_json"].read_text(encoding="utf-8"),
                outputs["ibm_runtime_archive_json"].read_text(encoding="utf-8"),
            )
            self.assertIn(
                "20260401T110500Z_ibm_fake_sherbrooke_job-123",
                outputs["ibm_runtime_archive_json"].name,
            )
            self.assertEqual(manifest_record["backend_name"], "ibm_fake_sherbrooke")
            self.assertEqual(manifest_record["job_id"], "job-123")
            self.assertFalse(manifest_record["local_testing_mode"])

    def test_ibm_runtime_artifacts_skip_archiving_for_local_testing_mode(self) -> None:
        result = self._build_result(local_testing_mode=True, job_id="job-local")
        comparison_records = [
            ComparisonRecord(
                observable_name="toy_observable",
                benchmark_value=1.0,
                candidate_value=0.9,
                absolute_error=0.1,
                relative_error=0.1,
                interpretation="Infrastructure-only comparison.",
            )
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            outputs = write_ibm_runtime_artifacts(
                experiment_name="phase4_test",
                scientific_question="Does the shared writer avoid archiving local-testing runs by default?",
                result=result,
                comparison_records=comparison_records,
                benchmark_complete=True,
                exact_local_complete=True,
                noisy_local_complete=True,
                execution_json_path=temp_root / "processed" / "ibm_runtime.json",
                comparison_json_path=temp_root / "processed" / "ibm_runtime_comparisons.json",
                metadata_json_path=temp_root / "raw" / "ibm_runtime_metadata.json",
                report_markdown_path=temp_root / "reports" / "ibm_runtime_report.md",
            )
            manifest_path = temp_root / "raw" / "ibm_runtime_runs.jsonl"
            self.assertNotIn("ibm_runtime_archive_json", outputs)
            self.assertFalse(manifest_path.exists())
            self.assertTrue(outputs["ibm_runtime_json"].exists())
