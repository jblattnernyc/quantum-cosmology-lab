# Results and Provenance

## Purpose

This document defines the repository policy for persisting execution metadata and comparison outputs.

Reproducibility in this repository depends on preserving more than figures or notebook cells. At minimum, scientifically relevant runs should retain the information needed to identify what was executed, under which backend conditions, and how outputs were compared against references.

## Shared Serialization Path

The shared package now provides JSON serialization helpers for execution and comparison outputs:

- `qclab.backends.execution.write_execution_result_json`
- `qclab.analysis.write_comparison_records_json`
- `qclab.backends.hardware.write_ibm_hardware_metadata_json`
- `qclab.backends.hardware.write_hardware_report_markdown`

These helpers produce formatted JSON records suitable for storage in `data/processed/` or `results/reports/`, depending on the experiment workflow.

## Minimum Recorded Metadata

Execution records should preserve:

- execution tier,
- backend name,
- backend-selection policy,
- mitigation policy,
- primitive name,
- shot count or requested precision,
- seed, when applicable,
- optimization level, when applicable,
- job identifier, when available,
- UTC timestamp,
- observable names, labels, values, and uncertainties,
- job metadata returned by the primitive, when serializable.

IBM hardware metadata records should additionally preserve:

- service channel and instance context,
- selected backend summary,
- available backend calibration snapshot or properties payload,
- runtime job summary and runtime job payload when available,
- whether the run used IBM Runtime local testing mode rather than a real backend.

Comparison records should preserve:

- observable name,
- benchmark value,
- candidate value,
- absolute error,
- relative error when defined,
- a written interpretation string.

## Recommended Storage Pattern

For official experiments, the recommended pattern is:

- raw execution artifacts under `data/raw/` when direct backend outputs need preservation,
- normalized execution and comparison JSON under `data/processed/`,
- IBM hardware metadata JSON under `data/raw/<experiment>/` for calibration and runtime payload capture,
- human-readable synthesis under `results/reports/`,
- IBM hardware reports under `results/reports/<experiment>/`,
- figures under `results/figures/`,
- tables under `results/tables/`.

For the currently implemented official experiment lines, this pattern is realized explicitly in:

- `data/processed/minisuperspace_frw/` and `results/{reports,tables,figures}/minisuperspace_frw/`,
- `data/processed/particle_creation_flrw/` and `results/{reports,tables,figures}/particle_creation_flrw/`,
- `data/processed/gut_toy_gauge/` and `results/{reports,tables,figures}/gut_toy_gauge/`.

These directory groupings should be preserved as the reference provenance layout for later official experiment lines unless a documented repository-level reason justifies a change.

Phase 6 repository-level dissemination outputs extend this pattern in two conservative ways:

- versioned milestone reports under `results/reports/milestones/`,
- machine-readable archival release manifests under `data/processed/releases/`.

These repository-level outputs should point to the preserved experiment artifacts and IBM manifest records. They should not replace or flatten the underlying provenance structure.

## IBM Artifact Retention Policy

IBM Runtime workflows in this repository are expected to write their configured
artifacts automatically to disk when an IBM execution tier is run
successfully. This automation is part of the repository's reproducibility
standard and should not depend on ad hoc manual export steps.

For completed live IBM hardware runs, the shared Phase 4 writer now preserves
two layers automatically:

- the canonical "latest result" files at the configured fixed paths,
- immutable timestamped archive copies paired with a per-experiment JSON Lines
  manifest under `data/raw/<experiment>/ibm_runtime_runs.jsonl`.

The archive filenames include the UTC result timestamp, backend name, and IBM
job identifier when available. This keeps the current canonical interface
stable while preventing later hardware runs from erasing earlier provenance.

That automatic write behavior does not imply that every IBM run should become
part of the tracked repository history. Repository inclusion remains a curated
scientific decision.

As a default policy:

- IBM execution JSON, comparison JSON, metadata JSON, and hardware reports
  should be generated automatically on disk for completed IBM-tier runs.
- Completed live IBM hardware runs should additionally generate timestamped
  archive copies and a manifest entry automatically.
- Only benchmarked and scientifically retained IBM runs should ordinarily be
  committed to the repository.
- Local-testing-mode runs, backend-access checks, smoke runs, and other purely
  operational validation runs may remain untracked unless there is a clear
  repository-level reason to preserve them. By default, they are not added to
  the automatic IBM archive set, and they write to separate `_local_testing`
  IBM artifact paths so they do not overwrite the canonical live-hardware
  files.
- IBM metadata artifacts should be reviewed before commit to avoid preserving
  unnecessary account-specific or environment-specific details.

This distinction preserves two separate goals:

- automatic provenance capture for reproducibility at execution time,
- deliberate curation of the permanent tracked scientific record.

## Interpretive Policy

Serialized provenance improves reproducibility, but it does not confer physical meaning. Interpretation must still be provided separately in the experiment’s `results.md` and analysis code.
