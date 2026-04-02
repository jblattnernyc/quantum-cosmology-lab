# Replication Checklist

## Purpose

This checklist defines the minimum steps for reproducing an official experiment workflow or a repository-level archival release snapshot after Phase 6.

## Environment and Installation

- [ ] The repository root is identified correctly.
- [ ] The Python environment satisfies the declared version and dependency requirements in `pyproject.toml`.
- [ ] The editable install or equivalent import path is configured so the `src/` package is importable.
- [ ] The baseline automated tests run successfully or any skipped or failed items are documented explicitly.

## Experiment Reproduction

- [ ] The target experiment `config.yaml` is identified and preserved.
- [ ] The benchmark script is run or the preserved benchmark artifact is verified.
- [ ] The exact-local workflow is run or the preserved exact-local artifact is verified.
- [ ] The noisy-local workflow is run or the preserved noisy-local artifact is verified.
- [ ] The analysis workflow is run or the preserved analysis report, table, and figure artifacts are verified.

## IBM Hardware Reproduction or Verification

- [ ] IBM Runtime access is configured only through approved local credential mechanisms when live hardware access is required.
- [ ] The benchmark-before-hardware policy is satisfied before any live IBM submission.
- [ ] The per-experiment `ibm_runtime_runs.jsonl` manifest is checked.
- [ ] Canonical IBM artifacts and timestamped archived IBM artifacts are both verified when live hardware provenance is part of the replication target.
- [ ] `_local_testing` IBM artifacts are treated as operational validation outputs rather than as live QPU records.

## Repository-Level Phase 6 Outputs

- [ ] The milestone report under `results/reports/milestones/` is regenerated or verified.
- [ ] The archival release manifest under `data/processed/releases/` is regenerated or verified.
- [ ] Governance documents referenced by the milestone report or release manifest are present and readable.

## Interpretation and Reporting

- [ ] The replicated document distinguishes benchmark, exact-local, noisy-local, and IBM tiers.
- [ ] Any deviations from the preserved artifacts are recorded explicitly rather than silently replacing prior outputs.
