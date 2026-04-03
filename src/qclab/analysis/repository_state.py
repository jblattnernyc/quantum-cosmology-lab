"""Phase-neutral current repository-state reporting helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from qclab.analysis.milestones import (
    IBMRunRecord,
    OfficialExperimentRecord,
    load_official_experiment_record,
)
from qclab.utils.configuration import load_model_configuration
from qclab.utils.paths import repository_relative_path


REPO_ROOT = Path(__file__).resolve().parents[3]
CURRENT_GOVERNANCE_DOCUMENTS = {
    "agents": REPO_ROOT / "AGENTS.md",
    "plans": REPO_ROOT / "PLANS.md",
    "readme": REPO_ROOT / "README.md",
    "experiment_standard": REPO_ROOT / "docs" / "methods" / "experiment-standard.md",
    "results_and_provenance": REPO_ROOT
    / "docs"
    / "operations"
    / "results-and-provenance.md",
}


@dataclass(frozen=True)
class CurrentRepositorySnapshot:
    """Current official-experiment repository view under active governance."""

    repository_root: Path
    package_version: str
    generated_at_utc: str
    governance_documents: dict[str, Path]
    official_experiments: tuple[OfficialExperimentRecord, ...]


def _current_timestamp_utc() -> str:
    """Return the current UTC timestamp in ISO 8601 form."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _normalize_generated_at_utc(generated_at_utc: str | None) -> str:
    """Normalize an optional generated-at timestamp to canonical UTC ISO 8601."""

    if generated_at_utc is None:
        return _current_timestamp_utc()
    parsed = datetime.fromisoformat(generated_at_utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _qclab_package_version(repository_root: Path) -> str:
    """Read the package version from ``src/qclab/__init__.py``."""

    init_text = (repository_root / "src" / "qclab" / "__init__.py").read_text(
        encoding="utf-8"
    )
    match = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)
    if match is None:
        raise ValueError("Could not determine the qclab package version.")
    return match.group(1)


def discover_current_official_experiment_names(
    *,
    repository_root: Path = REPO_ROOT,
) -> tuple[str, ...]:
    """Return the current official experiment directories from repository metadata."""

    experiments_root = repository_root.resolve() / "experiments"
    experiment_names: list[str] = []
    for experiment_root in sorted(path for path in experiments_root.iterdir() if path.is_dir()):
        config_path = experiment_root / "config.yaml"
        if not config_path.exists():
            continue
        configuration = load_model_configuration(config_path)
        if configuration.experiment_name != experiment_root.name:
            raise ValueError(
                "Experiment configuration name does not match directory name: "
                f"{configuration.experiment_name!r} != {experiment_root.name!r}"
            )
        if not configuration.official_experiment:
            continue
        if configuration.status != "official":
            raise ValueError(
                "Official experiment metadata must use status='official': "
                f"{configuration.experiment_name!r} has status={configuration.status!r}."
            )
        experiment_names.append(experiment_root.name)
    return tuple(experiment_names)


def collect_current_repository_snapshot(
    *,
    repository_root: Path = REPO_ROOT,
    generated_at_utc: str | None = None,
) -> CurrentRepositorySnapshot:
    """Collect the current phase-neutral official repository state."""

    resolved_root = repository_root.resolve()
    return CurrentRepositorySnapshot(
        repository_root=resolved_root,
        package_version=_qclab_package_version(resolved_root),
        generated_at_utc=_normalize_generated_at_utc(generated_at_utc),
        governance_documents={
            key: value.resolve() for key, value in CURRENT_GOVERNANCE_DOCUMENTS.items()
        },
        official_experiments=tuple(
            load_official_experiment_record(
                experiment_name,
                repository_root=resolved_root,
            )
            for experiment_name in discover_current_official_experiment_names(
                repository_root=resolved_root
            )
        ),
    )


def default_current_repository_report_path(
    *,
    repository_root: Path = REPO_ROOT,
) -> Path:
    """Return the default current repository-report output path."""

    return (
        repository_root / "results" / "reports" / "repository" / "current_official_experiments.md"
    ).resolve()


def default_current_official_experiment_manifest_path(
    *,
    repository_root: Path = REPO_ROOT,
) -> Path:
    """Return the default current official-experiment manifest output path."""

    return (
        repository_root / "data" / "processed" / "repository" / "current_official_experiments.json"
    ).resolve()


def _bullet_list(lines: list[str], values: list[str]) -> None:
    """Append a flat bullet list to a markdown line buffer."""

    for value in values:
        lines.append(f"- {value}")


def _snapshot_relative_path(
    snapshot: CurrentRepositorySnapshot,
    path: str | Path,
) -> str:
    """Return a repository-relative path string for rendered outputs."""

    return repository_relative_path(path, repository_root=snapshot.repository_root)


def _artifact_payload(
    record: OfficialExperimentRecord,
    *,
    repository_root: Path,
) -> dict[str, str]:
    """Return the resolved artifact payload for one official experiment."""

    return {
        "benchmark_json": repository_relative_path(
            record.benchmark_json,
            repository_root=repository_root,
        ),
        "exact_local_json": repository_relative_path(
            record.exact_local_json,
            repository_root=repository_root,
        ),
        "exact_local_comparisons_json": repository_relative_path(
            record.exact_local_comparisons_json,
            repository_root=repository_root,
        ),
        "noisy_local_json": repository_relative_path(
            record.noisy_local_json,
            repository_root=repository_root,
        ),
        "noisy_local_comparisons_json": repository_relative_path(
            record.noisy_local_comparisons_json,
            repository_root=repository_root,
        ),
        "ibm_runtime_json": repository_relative_path(
            record.ibm_runtime_json,
            repository_root=repository_root,
        ),
        "ibm_runtime_comparisons_json": repository_relative_path(
            record.ibm_runtime_comparisons_json,
            repository_root=repository_root,
        ),
        "ibm_runtime_metadata_json": repository_relative_path(
            record.ibm_runtime_metadata_json,
            repository_root=repository_root,
        ),
        "ibm_runtime_report_markdown": repository_relative_path(
            record.ibm_runtime_report_markdown,
            repository_root=repository_root,
        ),
        "analysis_summary_json": repository_relative_path(
            record.analysis_summary_json,
            repository_root=repository_root,
        ),
        "analysis_report_markdown": repository_relative_path(
            record.analysis_report_markdown,
            repository_root=repository_root,
        ),
        "observable_summary_table_markdown": repository_relative_path(
            record.observable_summary_table_markdown,
            repository_root=repository_root,
        ),
        "comparison_figure": repository_relative_path(
            record.comparison_figure,
            repository_root=repository_root,
        ),
    }


def _ibm_run_payload(
    record: IBMRunRecord | None,
    *,
    repository_root: Path,
) -> dict[str, Any] | None:
    """Return a JSON-safe payload for the latest live IBM run."""

    if record is None:
        return None
    return {
        "timestamp_utc": record.timestamp_utc,
        "backend_name": record.backend_name,
        "job_id": record.job_id,
        "local_testing_mode": record.local_testing_mode,
        "manifest_path": repository_relative_path(
            record.manifest_path,
            repository_root=repository_root,
        ),
        "canonical_artifacts": {
            key: repository_relative_path(value, repository_root=repository_root)
            for key, value in record.canonical_artifacts.items()
        },
        "archived_artifacts": {
            key: repository_relative_path(value, repository_root=repository_root)
            for key, value in record.archived_artifacts.items()
        },
    }


def render_current_repository_report(snapshot: CurrentRepositorySnapshot) -> str:
    """Render the current official repository report as Markdown."""

    lines = [
        "# Quantum Cosmology Lab Current Official Experiment Report",
        "",
        "## Purpose",
        "",
        (
            "This report records the current official experiment state of the repository "
            "under the active Version 1.1 governance posture. It is phase-neutral and is "
            "intended to complement, not replace, the preserved historical Phase 6 Version 1 "
            "archival baseline."
        ),
        "",
        "## Repository Status",
        "",
    ]
    _bullet_list(
        lines,
        [
            f"Repository package version: `v{snapshot.package_version}`",
            f"Report generation timestamp (UTC): `{snapshot.generated_at_utc}`",
            (
                "Current official experiment lines discovered from repository metadata: "
                f"`{len(snapshot.official_experiments)}`"
            ),
        ],
    )
    lines.extend(
        [
            "",
            "## Governance Context",
            "",
        ]
    )
    _bullet_list(
        lines,
        [
            (
                "Primary active governance document: "
                f"`{_snapshot_relative_path(snapshot, snapshot.governance_documents['agents'])}`"
            ),
            (
                "Historical charter and major-expansion control document: "
                f"`{_snapshot_relative_path(snapshot, snapshot.governance_documents['plans'])}`"
            ),
            (
                "Public repository overview: "
                f"`{_snapshot_relative_path(snapshot, snapshot.governance_documents['readme'])}`"
            ),
            (
                "Official experiment admission standard: "
                f"`{_snapshot_relative_path(snapshot, snapshot.governance_documents['experiment_standard'])}`"
            ),
            (
                "Results and provenance policy: "
                f"`{_snapshot_relative_path(snapshot, snapshot.governance_documents['results_and_provenance'])}`"
            ),
        ],
    )
    lines.extend(["", "## Current Official Experiments", ""])
    for record in snapshot.official_experiments:
        lines.extend(
            [
                f"### {record.experiment_name}",
                "",
                f"- Scientific question: {record.scientific_question}",
                f"- README: `{_snapshot_relative_path(snapshot, record.readme_path)}`",
                f"- Model statement: `{_snapshot_relative_path(snapshot, record.model_path)}`",
                f"- Results interpretation: `{_snapshot_relative_path(snapshot, record.results_path)}`",
                f"- Benchmark artifact: `{_snapshot_relative_path(snapshot, record.benchmark_json)}`",
                f"- Exact local artifact: `{_snapshot_relative_path(snapshot, record.exact_local_json)}`",
                f"- Noisy local artifact: `{_snapshot_relative_path(snapshot, record.noisy_local_json)}`",
                f"- Analysis summary: `{_snapshot_relative_path(snapshot, record.analysis_summary_json)}`",
                f"- Analysis report: `{_snapshot_relative_path(snapshot, record.analysis_report_markdown)}`",
            ]
        )
        if record.latest_live_ibm_run is None:
            lines.append("- Latest preserved live IBM run: none recorded in the manifest.")
        else:
            live_run = record.latest_live_ibm_run
            lines.extend(
                [
                    (
                        "- Latest preserved live IBM run (UTC): "
                        f"`{live_run.timestamp_utc}` on `{live_run.backend_name}` with job id "
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
                ]
            )
        lines.append(
            "- Separate `_local_testing` IBM artifacts present: "
            f"`{record.local_testing_artifacts_present}`"
        )
        lines.append("")
    lines.extend(
        [
            "## Boundary",
            "",
            (
                "This current-state report does not alter the preserved historical Phase 6 "
                "Version 1 archival record, does not imply a new roadmap phase, and does not "
                "change the scientific meaning of any underlying experiment."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def build_current_official_experiment_manifest(
    snapshot: CurrentRepositorySnapshot,
    *,
    report_path: str | Path,
) -> dict[str, Any]:
    """Build a machine-readable manifest for current official experiment state."""

    return {
        "report_kind": "current_official_experiments",
        "package_version": snapshot.package_version,
        "generated_at_utc": snapshot.generated_at_utc,
        "repository_root": ".",
        "report_markdown": repository_relative_path(
            Path(report_path).expanduser().resolve(),
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
                "artifacts": _artifact_payload(
                    record,
                    repository_root=snapshot.repository_root,
                ),
                "runs_manifest_jsonl": repository_relative_path(
                    record.runs_manifest_path,
                    repository_root=snapshot.repository_root,
                ),
                "live_ibm_run_count": record.live_ibm_run_count,
                "latest_live_ibm_run": _ibm_run_payload(
                    record.latest_live_ibm_run,
                    repository_root=snapshot.repository_root,
                ),
                "local_testing_artifacts_present": record.local_testing_artifacts_present,
            }
            for record in snapshot.official_experiments
        ],
        "repository_policies": {
            "agents_primary_active_governance": True,
            "plans_required_for_major_expansion_only": True,
            "benchmark_before_hardware": True,
            "local_testing_artifacts_are_noncanonical": True,
        },
    }


def write_current_repository_report(
    snapshot: CurrentRepositorySnapshot,
    *,
    output_path: str | Path,
) -> Path:
    """Write the current official repository report to disk."""

    resolved_path = Path(output_path).expanduser().resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(
        render_current_repository_report(snapshot) + "\n",
        encoding="utf-8",
    )
    return resolved_path


def write_current_official_experiment_manifest(
    snapshot: CurrentRepositorySnapshot,
    *,
    report_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Write the current official-experiment manifest to disk as JSON."""

    resolved_path = Path(output_path).expanduser().resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_current_official_experiment_manifest(
        snapshot,
        report_path=report_path,
    )
    resolved_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return resolved_path
