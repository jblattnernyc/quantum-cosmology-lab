"""Analysis helpers for comparing benchmark and execution outputs."""

from qclab.analysis.comparison import (
    ComparisonRecord,
    compare_scalar_observable,
    comparison_within_tolerance,
    comparison_records_to_rows,
)
from qclab.analysis.milestones import (
    build_archival_release_manifest,
    collect_phase6_snapshot,
    default_archival_release_manifest_path,
    default_phase6_milestone_id,
    default_phase6_milestone_report_path,
    load_official_experiment_record,
    render_phase6_milestone_report,
    write_archival_release_manifest,
    write_phase6_milestone_report,
)
from qclab.analysis.reporting import (
    comparison_records_to_dataframe,
    comparison_records_to_serializable,
    execution_result_to_dataframe,
    execution_result_to_serializable,
    execution_result_to_rows,
    write_comparison_records_json,
    write_execution_result_json,
)

__all__ = [
    "ComparisonRecord",
    "build_archival_release_manifest",
    "collect_phase6_snapshot",
    "compare_scalar_observable",
    "comparison_records_to_dataframe",
    "comparison_records_to_serializable",
    "comparison_within_tolerance",
    "comparison_records_to_rows",
    "default_archival_release_manifest_path",
    "default_phase6_milestone_id",
    "default_phase6_milestone_report_path",
    "execution_result_to_dataframe",
    "execution_result_to_serializable",
    "execution_result_to_rows",
    "load_official_experiment_record",
    "render_phase6_milestone_report",
    "write_archival_release_manifest",
    "write_comparison_records_json",
    "write_execution_result_json",
    "write_phase6_milestone_report",
]
