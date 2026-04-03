# Release Scripts

This directory contains the repository-level historical Phase 6 scripts for milestone reporting and archival release manifests.

These scripts do not replace the experiment-level benchmark, execution, analysis, or IBM provenance workflows. They summarize and package the already preserved Version 1 repository baseline for dissemination, internal review, and archival release preparation.

The directory also contains phase-neutral current-state scripts that report the presently official experiment set discovered from repository metadata under the active Version 1.1 governance posture.

## Scripts

### Historical Version 1 Archival Scripts

- `build_phase6_milestone_report.py`: write a versioned repository milestone report from the current official experiments and preserved IBM hardware record.
- `build_archival_release_manifest.py`: write a machine-readable archival release manifest that points to the milestone report, governance documents, official experiment artifacts, canonical IBM outputs, archived IBM outputs, and per-experiment run manifests.

### Current-State Scripts

- `build_current_repository_report.py`: write a phase-neutral report of the current official experiment set discovered from repository metadata.
- `build_current_official_experiment_manifest.py`: write a machine-readable phase-neutral manifest for the current official experiment set.

Both current-state scripts accept `--generated-at-utc <iso-8601-utc>` so tracked outputs can be regenerated deterministically when no substantive repository-state change has occurred.

## Default Outputs

By default, the scripts write:

- milestone reports under `results/reports/milestones/`,
- archival manifests under `data/processed/releases/`,
- current official experiment reports under `results/reports/repository/`,
- current official experiment manifests under `data/processed/repository/`.

## Example Usage

```bash
python scripts/release/build_phase6_milestone_report.py
python scripts/release/build_archival_release_manifest.py
python scripts/release/build_current_repository_report.py --generated-at-utc 2026-04-03T00:00:00+00:00
python scripts/release/build_current_official_experiment_manifest.py --generated-at-utc 2026-04-03T00:00:00+00:00
```

The current public Phase 6 archival baseline for the preserved Version 1 build record uses the repository package version together with the UTC date label `20260402`, producing:

- `results/reports/milestones/v1.0.0-phase6-20260402.md`
- `data/processed/releases/v1.0.0-phase6-20260402_manifest.json`

Earlier `v0.1.0` and `v0.2.0` Phase 6 artifacts remain preserved as internal development milestones.

The phase-neutral current-state scripts instead default to:

- `results/reports/repository/current_official_experiments.md`
- `data/processed/repository/current_official_experiments.json`

The current formal Version `1.1.0` repository snapshot is also preserved in versioned form at:

- `results/reports/repository/v1.1.0-current-20260403.md`
- `data/processed/repository/v1.1.0-current-20260403_manifest.json`
