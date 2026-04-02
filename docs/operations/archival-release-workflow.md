# Archival Release Workflow

## Purpose

This document defines the conservative Phase 6 workflow for preparing a repository-level archival release. The workflow is designed to preserve the current official experiment set, the benchmark-before-hardware policy, and the already implemented IBM provenance structure.

It is not a license to reclassify exploratory material as official or to replace experiment-level interpretation with release-level summary prose.

## Release Preconditions

Before preparing an archival release:

1. Confirm that the repository remains limited to the currently implemented official experiment lines.
2. Confirm that benchmark, exact-local, and noisy-local artifacts remain present for each official experiment.
3. Confirm that any live IBM hardware discussion is supported by the canonical artifacts, archived artifacts, and per-experiment `ibm_runtime_runs.jsonl` manifest entries.
4. Confirm that `_local_testing` IBM artifacts remain operationally separate from the live-hardware scientific record.
5. Run the relevant automated tests and any Phase 6 release-reporting smoke commands.

## Release Assembly Steps

From the repository root with the environment active:

```bash
python scripts/release/build_phase6_milestone_report.py
python scripts/release/build_archival_release_manifest.py
```

The default public Phase 6 baseline writes:

- `results/reports/milestones/v1.0.0-phase6-20260402.md`
- `data/processed/releases/v1.0.0-phase6-20260402_manifest.json`

If a later dated milestone is being assembled, supply a different `--date-label` or an explicit `--milestone-id` and `--release-id`.

The preserved `v0.1.0` and `v0.2.0` Phase 6 artifacts should be retained as internal developmental records rather than treated as the first public release.

## Required Review of the Release Outputs

Review the generated milestone report and release manifest for the following points:

- all three official experiment lines are present,
- the governance documents are referenced correctly,
- the latest live IBM run for each experiment is taken from the preserved manifest rather than inferred informally,
- canonical IBM artifact paths and archived IBM artifact paths are both preserved,
- local-testing artifacts are not promoted into the canonical release record.

## Contents of a Conservative Archival Release

A conservative archival release should preserve:

- repository-root governance documents,
- the official experiment directories and their model statements,
- shared package code under `src/qclab/`,
- tests required to validate the implemented repository baseline,
- canonical benchmark, exact-local, noisy-local, analysis, table, and figure artifacts,
- canonical IBM hardware artifacts for preserved live runs,
- timestamped archived IBM hardware artifacts for preserved live runs,
- per-experiment `ibm_runtime_runs.jsonl` manifests,
- the Phase 6 milestone report and archival release manifest.

## Exclusions and Restraints

Do not treat the following as part of the canonical archival scientific record unless there is a documented repository-level reason:

- `_local_testing` IBM artifacts,
- host-specific caches,
- ad hoc screenshots,
- temporary debugging logs,
- unreviewed exploratory notebooks.

## Interpretation Boundary

The archival release workflow preserves provenance and dissemination structure. It does not change the scientific meaning of the underlying experiment lines.
