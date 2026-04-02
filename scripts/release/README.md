# Release Scripts

This directory contains the repository-level Phase 6 scripts for milestone reporting and archival release manifests.

These scripts do not replace the experiment-level benchmark, execution, analysis, or IBM provenance workflows. They summarize and package the already preserved repository state for dissemination, internal review, and archival release preparation.

## Scripts

- `build_phase6_milestone_report.py`: write a versioned repository milestone report from the current official experiments and preserved IBM hardware record.
- `build_archival_release_manifest.py`: write a machine-readable archival release manifest that points to the milestone report, governance documents, official experiment artifacts, canonical IBM outputs, archived IBM outputs, and per-experiment run manifests.

## Default Outputs

By default, the scripts write:

- milestone reports under `results/reports/milestones/`,
- archival manifests under `data/processed/releases/`.

## Example Usage

```bash
python scripts/release/build_phase6_milestone_report.py
python scripts/release/build_archival_release_manifest.py
```

The current public Phase 6 archival baseline uses the repository package version together with the UTC date label `20260402`, producing:

- `results/reports/milestones/v1.0.0-phase6-20260402.md`
- `data/processed/releases/v1.0.0-phase6-20260402_manifest.json`

Earlier `v0.1.0` and `v0.2.0` Phase 6 artifacts remain preserved as internal development milestones.
