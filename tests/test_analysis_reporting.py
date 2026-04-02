"""Analysis-reporting tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.path_setup import ensure_src_path

ensure_src_path()

from qclab.analysis import (
    comparison_within_tolerance,
    execution_result_to_rows,
    write_comparison_records_json,
    write_execution_result_json,
)
from qclab.analysis.comparison import ComparisonRecord
from qclab.backends.base import BackendRequest, ExecutionTier
from qclab.backends.execution import (
    EstimatorExecutionResult,
    ExecutionProvenance,
    execution_result_to_serializable,
)
from qclab.observables import ObservableDefinition, ObservableEvaluation


class AnalysisReportingTests(unittest.TestCase):
    """Verify provenance-aware analysis helpers."""

    def test_comparison_tolerance_helper(self) -> None:
        record = ComparisonRecord(
            observable_name="toy_observable",
            benchmark_value=1.0,
            candidate_value=0.95,
            absolute_error=0.05,
            relative_error=0.05,
            interpretation="Infrastructure-only comparison.",
        )
        self.assertTrue(
            comparison_within_tolerance(
                record,
                absolute_tolerance=0.1,
                relative_tolerance=0.1,
            )
        )
        self.assertFalse(comparison_within_tolerance(record, absolute_tolerance=0.01))

    def test_execution_result_rows_include_provenance(self) -> None:
        observable = ObservableDefinition(
            name="toy_observable",
            operator_label="Z",
            physical_meaning="Infrastructure-only observable.",
            measurement_basis="pauli",
        )
        result = EstimatorExecutionResult(
            request=BackendRequest(
                tier=ExecutionTier.EXACT_LOCAL,
                backend_name="statevector_estimator",
            ),
            evaluations=(
                ObservableEvaluation(observable=observable, value=1.0, uncertainty=0.0),
            ),
            provenance=ExecutionProvenance(
                tier=ExecutionTier.EXACT_LOCAL,
                backend_name="statevector_estimator",
                primitive_name="qiskit.primitives.StatevectorEstimator",
                job_id="job-001",
            ),
        )
        rows = execution_result_to_rows(result)
        self.assertEqual(rows[0]["observable_name"], "toy_observable")
        self.assertEqual(rows[0]["backend_name"], "statevector_estimator")
        self.assertEqual(rows[0]["job_id"], "job-001")

    def test_execution_result_serialization_writes_json(self) -> None:
        observable = ObservableDefinition(
            name="toy_observable",
            operator_label="Z",
            physical_meaning="Infrastructure-only observable.",
            measurement_basis="pauli",
        )
        result = EstimatorExecutionResult(
            request=BackendRequest(
                tier=ExecutionTier.EXACT_LOCAL,
                backend_name="statevector_estimator",
                options={"seed_strategy": "deterministic"},
            ),
            evaluations=(
                ObservableEvaluation(observable=observable, value=1.0, uncertainty=0.0),
            ),
            provenance=ExecutionProvenance(
                tier=ExecutionTier.EXACT_LOCAL,
                backend_name="statevector_estimator",
                primitive_name="qiskit.primitives.StatevectorEstimator",
                job_id="job-001",
            ),
            job_metadata={"target_precision": 0.0},
        )
        serializable = execution_result_to_serializable(result)
        self.assertEqual(serializable["provenance"]["job_id"], "job-001")
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "execution.json"
            write_execution_result_json(result, output_path)
            loaded = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(loaded["request"]["tier"], "exact_local")
        self.assertEqual(loaded["job_metadata"]["target_precision"], 0.0)

    def test_comparison_record_serialization_writes_json(self) -> None:
        records = [
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
            output_path = Path(temp_dir) / "comparison.json"
            write_comparison_records_json(records, output_path)
            loaded = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(loaded[0]["observable_name"], "toy_observable")
        self.assertEqual(loaded[0]["absolute_error"], 0.1)
