"""Phase 6 milestone-report and archival-release helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from qclab.utils.configuration import load_model_configuration
from qclab.utils.paths import repository_relative_path


REPO_ROOT = Path(__file__).resolve().parents[3]
OFFICIAL_EXPERIMENTS = (
    "minisuperspace_frw",
    "particle_creation_flrw",
    "gut_toy_gauge",
)
PHASE6_GOVERNANCE_DOCUMENTS = {
    "citation_policy": REPO_ROOT
    / "docs"
    / "references"
    / "citation-and-bibliography-policy.md",
    "figure_table_style_guide": REPO_ROOT
    / "docs"
    / "methods"
    / "figure-and-table-style-guide.md",
    "internal_review_checklist": REPO_ROOT
    / "docs"
    / "operations"
    / "internal-review-checklist.md",
    "replication_checklist": REPO_ROOT
    / "docs"
    / "operations"
    / "replication-checklist.md",
    "archival_release_workflow": REPO_ROOT
    / "docs"
    / "operations"
    / "archival-release-workflow.md",
}


@dataclass(frozen=True)
class IBMRunRecord:
    """Structured representation of one preserved IBM Runtime manifest entry."""

    timestamp_utc: str | None
    backend_name: str | None
    job_id: str | None
    local_testing_mode: bool
    canonical_artifacts: dict[str, Path]
    archived_artifacts: dict[str, Path]
    manifest_path: Path


@dataclass(frozen=True)
class OfficialExperimentRecord:
    """Repository-level dissemination record for one official experiment."""

    experiment_name: str
    scientific_question: str
    readme_path: Path
    model_path: Path
    results_path: Path
    config_path: Path
    benchmark_json: Path
    exact_local_json: Path
    exact_local_comparisons_json: Path
    noisy_local_json: Path
    noisy_local_comparisons_json: Path
    ibm_runtime_json: Path
    ibm_runtime_comparisons_json: Path
    ibm_runtime_metadata_json: Path
    ibm_runtime_report_markdown: Path
    analysis_summary_json: Path
    analysis_report_markdown: Path
    observable_summary_table_markdown: Path
    comparison_figure: Path
    runs_manifest_path: Path
    live_ibm_run_count: int
    latest_live_ibm_run: IBMRunRecord | None
    local_testing_artifacts_present: bool


@dataclass(frozen=True)
class Phase6Snapshot:
    """Current repository snapshot used by the Phase 6 dissemination layer."""

    repository_root: Path
    package_version: str
    roadmap_phase: int
    generated_at_utc: str
    governance_documents: dict[str, Path]
    official_experiments: tuple[OfficialExperimentRecord, ...]


def _current_timestamp_utc() -> str:
    """Return the current UTC timestamp in ISO 8601 form."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _parse_timestamp(timestamp_utc: str | None) -> datetime:
    """Parse a possibly missing ISO 8601 timestamp into a sortable datetime."""

    if timestamp_utc is None:
        return datetime.min.replace(tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(timestamp_utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _qclab_package_version(repository_root: Path) -> str:
    """Read the package version from ``src/qclab/__init__.py``."""

    init_text = (repository_root / "src" / "qclab" / "__init__.py").read_text(
        encoding="utf-8"
    )
    match = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)
    if match is None:
        raise ValueError("Could not determine the qclab package version.")
    return match.group(1)


def _resolve_path(repository_root: Path, raw_path: str | Path) -> Path:
    """Resolve a possibly relative repository artifact path."""

    candidate = Path(raw_path).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (repository_root / candidate).resolve()


def _required_artifact_path(
    repository_root: Path,
    artifacts: dict[str, Any],
    key: str,
) -> Path:
    """Resolve a required artifact path from experiment metadata."""

    if key not in artifacts:
        raise KeyError(f"Missing required Phase 6 artifact path in configuration: {key}")
    return _resolve_path(repository_root, artifacts[key])


def _local_testing_path(canonical_path: Path) -> Path:
    """Return the `_local_testing` variant of a canonical IBM artifact path."""

    return canonical_path.with_name(
        f"{canonical_path.stem}_local_testing{canonical_path.suffix}"
    )


def _load_json(path: Path) -> Any:
    """Load a JSON file from disk."""

    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a JSON Lines file from disk."""

    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        payload = json.loads(stripped)
        if not isinstance(payload, dict):
            raise TypeError(f"Expected JSON object records in manifest: {path}")
        records.append(payload)
    return records


def _path_mapping_from_record(
    repository_root: Path,
    mapping: dict[str, Any] | None,
) -> dict[str, Path]:
    """Normalize a manifest artifact mapping into resolved paths."""

    if mapping is None:
        return {}
    return {
        str(key): _resolve_path(repository_root, value)
        for key, value in mapping.items()
    }


def _ibm_run_record_from_manifest(
    repository_root: Path,
    manifest_path: Path,
    payload: dict[str, Any],
) -> IBMRunRecord:
    """Convert one manifest record into a typed IBM run record."""

    return IBMRunRecord(
        timestamp_utc=(
            None if payload.get("timestamp_utc") is None else str(payload["timestamp_utc"])
        ),
        backend_name=(
            None if payload.get("backend_name") is None else str(payload["backend_name"])
        ),
        job_id=None if payload.get("job_id") is None else str(payload["job_id"]),
        local_testing_mode=bool(payload.get("local_testing_mode", False)),
        canonical_artifacts=_path_mapping_from_record(
            repository_root,
            payload.get("canonical_artifacts"),
        ),
        archived_artifacts=_path_mapping_from_record(
            repository_root,
            payload.get("archived_artifacts"),
        ),
        manifest_path=manifest_path.resolve(),
    )


def load_official_experiment_record(
    experiment_name: str,
    *,
    repository_root: Path = REPO_ROOT,
) -> OfficialExperimentRecord:
    """Load the dissemination record for one official experiment."""

    experiment_root = repository_root / "experiments" / experiment_name
    configuration = load_model_configuration(experiment_root / "config.yaml")
    artifacts = dict(configuration.metadata.get("artifacts", {}))

    benchmark_json = _required_artifact_path(repository_root, artifacts, "benchmark_json")
    exact_local_json = _required_artifact_path(repository_root, artifacts, "exact_local_json")
    exact_local_comparisons_json = _required_artifact_path(
        repository_root,
        artifacts,
        "exact_local_comparisons_json",
    )
    noisy_local_json = _required_artifact_path(repository_root, artifacts, "noisy_local_json")
    noisy_local_comparisons_json = _required_artifact_path(
        repository_root,
        artifacts,
        "noisy_local_comparisons_json",
    )
    ibm_runtime_json = _required_artifact_path(repository_root, artifacts, "ibm_runtime_json")
    ibm_runtime_comparisons_json = _required_artifact_path(
        repository_root,
        artifacts,
        "ibm_runtime_comparisons_json",
    )
    ibm_runtime_metadata_json = _required_artifact_path(
        repository_root,
        artifacts,
        "ibm_runtime_metadata_json",
    )
    ibm_runtime_report_markdown = _required_artifact_path(
        repository_root,
        artifacts,
        "ibm_runtime_report_markdown",
    )
    analysis_summary_json = _required_artifact_path(
        repository_root,
        artifacts,
        "analysis_summary_json",
    )
    analysis_report_markdown = _required_artifact_path(
        repository_root,
        artifacts,
        "analysis_report_markdown",
    )
    observable_summary_table_markdown = _required_artifact_path(
        repository_root,
        artifacts,
        "observable_summary_table_markdown",
    )
    comparison_figure = _required_artifact_path(repository_root, artifacts, "comparison_figure")

    runs_manifest_path = (
        repository_root / "data" / "raw" / experiment_name / "ibm_runtime_runs.jsonl"
    ).resolve()
    manifest_payloads = _load_jsonl(runs_manifest_path)
    live_records = [
        _ibm_run_record_from_manifest(repository_root, runs_manifest_path, payload)
        for payload in manifest_payloads
        if not bool(payload.get("local_testing_mode", False))
    ]
    latest_live_record = None
    if live_records:
        latest_live_record = sorted(
            live_records,
            key=lambda record: _parse_timestamp(record.timestamp_utc),
        )[-1]

    local_testing_artifacts_present = any(
        path.exists()
        for path in (
            _local_testing_path(ibm_runtime_json),
            _local_testing_path(ibm_runtime_comparisons_json),
            _local_testing_path(ibm_runtime_metadata_json),
            _local_testing_path(ibm_runtime_report_markdown),
        )
    )

    return OfficialExperimentRecord(
        experiment_name=experiment_name,
        scientific_question=configuration.scientific_question.strip(),
        readme_path=(experiment_root / "README.md").resolve(),
        model_path=(experiment_root / "model.md").resolve(),
        results_path=(experiment_root / "results.md").resolve(),
        config_path=(experiment_root / "config.yaml").resolve(),
        benchmark_json=benchmark_json,
        exact_local_json=exact_local_json,
        exact_local_comparisons_json=exact_local_comparisons_json,
        noisy_local_json=noisy_local_json,
        noisy_local_comparisons_json=noisy_local_comparisons_json,
        ibm_runtime_json=ibm_runtime_json,
        ibm_runtime_comparisons_json=ibm_runtime_comparisons_json,
        ibm_runtime_metadata_json=ibm_runtime_metadata_json,
        ibm_runtime_report_markdown=ibm_runtime_report_markdown,
        analysis_summary_json=analysis_summary_json,
        analysis_report_markdown=analysis_report_markdown,
        observable_summary_table_markdown=observable_summary_table_markdown,
        comparison_figure=comparison_figure,
        runs_manifest_path=runs_manifest_path,
        live_ibm_run_count=len(live_records),
        latest_live_ibm_run=latest_live_record,
        local_testing_artifacts_present=local_testing_artifacts_present,
    )


def collect_phase6_snapshot(
    *,
    repository_root: Path = REPO_ROOT,
) -> Phase6Snapshot:
    """Collect the current repository state relevant to Phase 6."""

    return Phase6Snapshot(
        repository_root=repository_root.resolve(),
        package_version=_qclab_package_version(repository_root.resolve()),
        roadmap_phase=6,
        generated_at_utc=_current_timestamp_utc(),
        governance_documents={
            key: value.resolve() for key, value in PHASE6_GOVERNANCE_DOCUMENTS.items()
        },
        official_experiments=tuple(
            load_official_experiment_record(
                experiment_name,
                repository_root=repository_root.resolve(),
            )
            for experiment_name in OFFICIAL_EXPERIMENTS
        ),
    )


def default_phase6_milestone_id(
    package_version: str,
    *,
    date_label: str | None = None,
) -> str:
    """Return the default versioned Phase 6 milestone identifier."""

    if date_label is None:
        date_label = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"v{package_version}-phase6-{date_label}"


def default_phase6_milestone_report_path(
    milestone_id: str,
    *,
    repository_root: Path = REPO_ROOT,
) -> Path:
    """Return the default milestone-report output path."""

    return (
        repository_root
        / "results"
        / "reports"
        / "milestones"
        / f"{milestone_id}.md"
    ).resolve()


def default_archival_release_manifest_path(
    release_id: str,
    *,
    repository_root: Path = REPO_ROOT,
) -> Path:
    """Return the default archival-release manifest output path."""

    return (
        repository_root
        / "data"
        / "processed"
        / "releases"
        / f"{release_id}_manifest.json"
    ).resolve()


def _bullet_list(lines: list[str], values: list[str]) -> None:
    """Append a flat bullet list to a markdown line buffer."""

    for value in values:
        lines.append(f"- {value}")


def _snapshot_relative_path(snapshot: Phase6Snapshot, path: str | Path) -> str:
    """Return a repository-relative path string for rendered Phase 6 outputs."""

    return repository_relative_path(path, repository_root=snapshot.repository_root)


def render_phase6_milestone_report(
    snapshot: Phase6Snapshot,
    *,
    milestone_id: str,
) -> str:
    """Render the repository-level Phase 6 milestone report as Markdown."""

    live_timestamps = [
        _parse_timestamp(record.latest_live_ibm_run.timestamp_utc)
        for record in snapshot.official_experiments
        if record.latest_live_ibm_run is not None
        and record.latest_live_ibm_run.timestamp_utc is not None
    ]
    live_record_span = "No live IBM hardware record detected."
    if live_timestamps:
        live_record_span = (
            f"{min(live_timestamps).isoformat()} through "
            f"{max(live_timestamps).isoformat()}"
        )

    lines = [
        f"# Quantum Cosmology Lab Milestone Report: {milestone_id}",
        "",
        "## Purpose",
        "",
        (
            "This report records the Phase 6 dissemination-and-governance "
            "baseline of the repository. It summarizes the current official "
            "experiment set, the preserved IBM hardware provenance, and the "
            "repository-level documentation and release controls added for "
            "durable internal and archival use."
        ),
        "",
        "## Repository Status",
        "",
    ]
    _bullet_list(
        lines,
        [
            f"Roadmap phase completed: `{snapshot.roadmap_phase}`",
            f"Repository package version: `v{snapshot.package_version}`",
            f"Report generation timestamp (UTC): `{snapshot.generated_at_utc}`",
            (
                "Implemented official experiment lines: "
                f"`{len(snapshot.official_experiments)}`"
            ),
            f"Preserved live IBM hardware record span (UTC): `{live_record_span}`",
        ],
    )
    lines.extend(
        [
            "",
            "## Phase 6 Governance Deliverables",
            "",
        ]
    )
    _bullet_list(
        lines,
        [
            (
                "Citation and bibliography policy: "
                f"`{_snapshot_relative_path(snapshot, snapshot.governance_documents['citation_policy'])}`"
            ),
            (
                "Figure and table style guide: "
                f"`{_snapshot_relative_path(snapshot, snapshot.governance_documents['figure_table_style_guide'])}`"
            ),
            (
                "Internal review checklist: "
                f"`{_snapshot_relative_path(snapshot, snapshot.governance_documents['internal_review_checklist'])}`"
            ),
            (
                "Replication checklist: "
                f"`{_snapshot_relative_path(snapshot, snapshot.governance_documents['replication_checklist'])}`"
            ),
            (
                "Archival release workflow: "
                f"`{_snapshot_relative_path(snapshot, snapshot.governance_documents['archival_release_workflow'])}`"
            ),
        ],
    )
    lines.extend(["", "## Official Experiments", ""])
    for record in snapshot.official_experiments:
        lines.extend(
            [
                f"### {record.experiment_name}",
                "",
                f"- Scientific question: {record.scientific_question}",
                f"- README: `{_snapshot_relative_path(snapshot, record.readme_path)}`",
                (
                    "- Model statement: "
                    f"`{_snapshot_relative_path(snapshot, record.model_path)}`"
                ),
                (
                    "- Results interpretation: "
                    f"`{_snapshot_relative_path(snapshot, record.results_path)}`"
                ),
                (
                    "- Benchmark artifact: "
                    f"`{_snapshot_relative_path(snapshot, record.benchmark_json)}`"
                ),
                (
                    "- Exact local artifact: "
                    f"`{_snapshot_relative_path(snapshot, record.exact_local_json)}`"
                ),
                (
                    "- Noisy local artifact: "
                    f"`{_snapshot_relative_path(snapshot, record.noisy_local_json)}`"
                ),
                (
                    "- Analysis summary: "
                    f"`{_snapshot_relative_path(snapshot, record.analysis_summary_json)}`"
                ),
                (
                    "- Analysis report: "
                    f"`{_snapshot_relative_path(snapshot, record.analysis_report_markdown)}`"
                ),
                (
                    "- Summary table: "
                    f"`{_snapshot_relative_path(snapshot, record.observable_summary_table_markdown)}`"
                ),
                (
                    "- Comparison figure: "
                    f"`{_snapshot_relative_path(snapshot, record.comparison_figure)}`"
                ),
            ]
        )
        if record.latest_live_ibm_run is None:
            lines.append("- Latest live IBM run: none preserved in the manifest.")
        else:
            live_run = record.latest_live_ibm_run
            lines.extend(
                [
                    (
                        "- Latest live IBM run (UTC): "
                        f"`{live_run.timestamp_utc}` on "
                        f"`{live_run.backend_name}` with job id "
                        f"`{live_run.job_id}`"
                    ),
                    (
                        "- Live IBM manifest: "
                        f"`{_snapshot_relative_path(snapshot, record.runs_manifest_path)}`"
                    ),
                    (
                        "- Canonical IBM report: "
                        f"`{_snapshot_relative_path(snapshot, record.ibm_runtime_report_markdown)}`"
                    ),
                    (
                        "- Archived IBM report: "
                        f"`{_snapshot_relative_path(snapshot, live_run.archived_artifacts.get('report_markdown'))}`"
                    ),
                    (
                        "- Canonical IBM metadata JSON: "
                        f"`{_snapshot_relative_path(snapshot, record.ibm_runtime_metadata_json)}`"
                    ),
                ]
            )
        lines.append(
            (
                "- Separate `_local_testing` IBM artifacts present: "
                f"`{record.local_testing_artifacts_present}`"
            )
        )
        lines.append("")
    lines.extend(
        [
            "## Archival Release Scope",
            "",
            (
                "Phase 6 archival releases are expected to point to the "
                "canonical latest-result artifacts, the immutable archived live "
                "IBM copies, and the per-experiment JSON Lines manifests rather "
                "than replacing those provenance structures."
            ),
            "",
        ]
    )
    _bullet_list(
        lines,
        [
            "Preserve repository-root governance documents together with the official experiment definitions and tests.",
            "Preserve canonical benchmark, exact-local, noisy-local, analysis, table, and figure artifacts for each official experiment.",
            "Preserve the per-experiment live IBM canonical outputs, timestamped archive copies, and `ibm_runtime_runs.jsonl` manifests.",
            "Keep `_local_testing` artifacts operationally separate from the live-hardware scientific record.",
            "Do not treat the milestone report or release manifest as substitutes for experiment-level `results.md` interpretation.",
        ],
    )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            (
                "This milestone implements Phase 6 only. It does not introduce "
                "a Phase 7 roadmap item, a new official experiment line, or a "
                "new physical interpretation beyond the preserved benchmarked "
                "records."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _artifact_payload(record: OfficialExperimentRecord) -> dict[str, str]:
    """Return the resolved artifact payload for one official experiment."""

    return {
        "benchmark_json": repository_relative_path(record.benchmark_json),
        "exact_local_json": repository_relative_path(record.exact_local_json),
        "exact_local_comparisons_json": repository_relative_path(
            record.exact_local_comparisons_json
        ),
        "noisy_local_json": repository_relative_path(record.noisy_local_json),
        "noisy_local_comparisons_json": repository_relative_path(
            record.noisy_local_comparisons_json
        ),
        "ibm_runtime_json": repository_relative_path(record.ibm_runtime_json),
        "ibm_runtime_comparisons_json": repository_relative_path(
            record.ibm_runtime_comparisons_json
        ),
        "ibm_runtime_metadata_json": repository_relative_path(
            record.ibm_runtime_metadata_json
        ),
        "ibm_runtime_report_markdown": repository_relative_path(
            record.ibm_runtime_report_markdown
        ),
        "analysis_summary_json": repository_relative_path(record.analysis_summary_json),
        "analysis_report_markdown": repository_relative_path(
            record.analysis_report_markdown
        ),
        "observable_summary_table_markdown": repository_relative_path(
            record.observable_summary_table_markdown
        ),
        "comparison_figure": repository_relative_path(record.comparison_figure),
    }


def _ibm_run_payload(record: IBMRunRecord | None) -> dict[str, Any] | None:
    """Return a JSON-safe payload for the latest live IBM run."""

    if record is None:
        return None
    return {
        "timestamp_utc": record.timestamp_utc,
        "backend_name": record.backend_name,
        "job_id": record.job_id,
        "local_testing_mode": record.local_testing_mode,
        "manifest_path": repository_relative_path(record.manifest_path),
        "canonical_artifacts": {
            key: repository_relative_path(value)
            for key, value in record.canonical_artifacts.items()
        },
        "archived_artifacts": {
            key: repository_relative_path(value)
            for key, value in record.archived_artifacts.items()
        },
    }


def build_archival_release_manifest(
    snapshot: Phase6Snapshot,
    *,
    release_id: str,
    milestone_report_path: str | Path,
) -> dict[str, Any]:
    """Build a machine-readable archival release manifest."""

    return {
        "release_id": release_id,
        "roadmap_phase": snapshot.roadmap_phase,
        "package_version": snapshot.package_version,
        "generated_at_utc": snapshot.generated_at_utc,
        "repository_root": ".",
        "milestone_report_markdown": repository_relative_path(
            Path(milestone_report_path).expanduser().resolve(),
            repository_root=snapshot.repository_root,
        ),
        "governance_documents": {
            key: repository_relative_path(value, repository_root=snapshot.repository_root)
            for key, value in snapshot.governance_documents.items()
        },
        "official_experiments": [
            {
                "experiment_name": record.experiment_name,
                "scientific_question": record.scientific_question,
                "documents": {
                    "readme_markdown": repository_relative_path(
                        record.readme_path,
                        repository_root=snapshot.repository_root,
                    ),
                    "model_markdown": repository_relative_path(
                        record.model_path,
                        repository_root=snapshot.repository_root,
                    ),
                    "results_markdown": repository_relative_path(
                        record.results_path,
                        repository_root=snapshot.repository_root,
                    ),
                    "config_yaml": repository_relative_path(
                        record.config_path,
                        repository_root=snapshot.repository_root,
                    ),
                },
                "artifacts": _artifact_payload(record),
                "runs_manifest_jsonl": repository_relative_path(
                    record.runs_manifest_path,
                    repository_root=snapshot.repository_root,
                ),
                "live_ibm_run_count": record.live_ibm_run_count,
                "latest_live_ibm_run": _ibm_run_payload(record.latest_live_ibm_run),
                "local_testing_artifacts_present": record.local_testing_artifacts_present,
            }
            for record in snapshot.official_experiments
        ],
        "repository_policies": {
            "benchmark_before_hardware": True,
            "local_testing_artifacts_are_noncanonical": True,
            "phase7_or_later_implemented": False,
        },
    }


def write_phase6_milestone_report(
    snapshot: Phase6Snapshot,
    *,
    milestone_id: str,
    output_path: str | Path,
) -> Path:
    """Write the versioned Phase 6 milestone report to disk."""

    resolved_path = Path(output_path).expanduser().resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(
        render_phase6_milestone_report(snapshot, milestone_id=milestone_id) + "\n",
        encoding="utf-8",
    )
    return resolved_path


def write_archival_release_manifest(
    snapshot: Phase6Snapshot,
    *,
    release_id: str,
    milestone_report_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Write the archival release manifest to disk as formatted JSON."""

    resolved_path = Path(output_path).expanduser().resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_archival_release_manifest(
        snapshot,
        release_id=release_id,
        milestone_report_path=milestone_report_path,
    )
    resolved_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return resolved_path
