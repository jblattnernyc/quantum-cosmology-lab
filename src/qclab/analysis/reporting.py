"""Reporting helpers for execution and comparison records."""

from __future__ import annotations

import json
from pathlib import Path

from qclab.analysis.comparison import ComparisonRecord, comparison_records_to_rows
from qclab.backends.execution import (
    EstimatorExecutionResult,
    execution_result_to_serializable,
    write_execution_result_json,
)
from qclab.utils.optional import require_dependency


def execution_result_to_rows(
    result: EstimatorExecutionResult,
) -> list[dict[str, float | str | None]]:
    """Convert an execution result into row dictionaries."""

    rows: list[dict[str, float | str | None]] = []
    for evaluation in result.evaluations:
        rows.append(
            {
                "observable_name": evaluation.observable.name,
                "operator_label": evaluation.observable.operator_label,
                "value": evaluation.value,
                "uncertainty": evaluation.uncertainty,
                "units": evaluation.observable.units,
                "backend_name": result.provenance.backend_name,
                "tier": result.provenance.tier.value,
                "primitive_name": result.provenance.primitive_name,
                "job_id": result.provenance.job_id,
                "timestamp_utc": result.provenance.timestamp_utc,
            }
        )
    return rows


def comparison_records_to_dataframe(records: list[ComparisonRecord] | tuple[ComparisonRecord, ...]):
    """Convert comparison records into a pandas DataFrame."""

    pandas = require_dependency(
        "pandas",
        "convert comparison records into a DataFrame",
    )
    return pandas.DataFrame(comparison_records_to_rows(records))


def execution_result_to_dataframe(result: EstimatorExecutionResult):
    """Convert an execution result into a pandas DataFrame."""

    pandas = require_dependency(
        "pandas",
        "convert execution results into a DataFrame",
    )
    return pandas.DataFrame(execution_result_to_rows(result))


def comparison_records_to_serializable(
    records: list[ComparisonRecord] | tuple[ComparisonRecord, ...],
) -> list[dict[str, float | str | None]]:
    """Convert comparison records into a JSON-safe list."""

    return comparison_records_to_rows(records)


def write_comparison_records_json(
    records: list[ComparisonRecord] | tuple[ComparisonRecord, ...],
    path: str | Path,
) -> Path:
    """Write comparison records to disk as formatted JSON."""

    resolved_path = Path(path).expanduser().resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(
        json.dumps(comparison_records_to_serializable(records), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return resolved_path
