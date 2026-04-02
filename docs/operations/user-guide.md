# User Guide

## Purpose

This guide explains how to install, validate, and use the Quantum Cosmology Lab repository as it currently exists. It is intended for users who want to reproduce the implemented workflows, inspect generated artifacts, and understand the repository's operating conventions without treating it as a general-purpose quantum-computing sandbox.

At the present repository state, the lab is implemented through Phase 6 of the roadmap. The official experiment lines are `experiments/minisuperspace_frw/`, `experiments/particle_creation_flrw/`, and `experiments/gut_toy_gauge/`.

## Scientific Operating Principle

All official work in this repository follows the same methodological order:

1. define the model,
2. define the observable,
3. compute or verify a benchmark,
4. validate exact local execution,
5. validate noisy local execution,
6. consider IBM hardware only after the benchmark, exact-local, and noisy-local tiers are scientifically interpretable.

This ordering is not optional. Hardware execution is a later validation tier rather than the primary source of scientific meaning.

## Prerequisites

Before using the repository, ensure that the following are available on the local system:

- Python 3.10 or later,
- a standard shell environment such as `zsh` or `bash`,
- network access for package installation when the environment is first created,
- IBM Quantum credentials only if the IBM Runtime workflow is to be used.

The repository declares its primary dependencies in `pyproject.toml`, including Qiskit, qiskit-aer, qiskit-ibm-runtime, NumPy, SciPy, SymPy, pandas, matplotlib, pytest, and YAML support.

The currently validated repository test matrix covers Python 3.10 through 3.13. Python 3.14 and later should be treated as experimental until the full local test and Aer execution surface has been confirmed there.

## Environment Setup

From the repository root, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

The quoted extras specifier is important in `zsh`, where an unquoted `.[dev]` is treated as a glob pattern rather than as a package extras declaration.

A small [Makefile](../../Makefile) is also provided as a convenience interface for routine repository commands. It does not replace the governing documents, experiment scripts, or package metadata.

## Installation Verification

After installation, verify that the repository imports and tests correctly:

```bash
python -m pytest
```

If `pytest` is not available for any reason, run the baseline test suite with:

```bash
python -m unittest discover -s tests -v
```

These checks validate package imports, benchmark helpers, observable construction, backend wrappers, reporting utilities, repository structure, and guarded local Qiskit integrations when the relevant dependencies are installed.

## Repository Layout

The principal working locations are:

- `src/qclab/`: reusable shared scientific infrastructure,
- `experiments/`: official experiment directories and planned experiment lines,
- `tests/`: automated validation of infrastructure and experiment logic,
- `docs/`: architecture, methods, operations, and references,
- `data/raw/`: raw execution artifacts when direct outputs require preservation,
- `data/processed/`: normalized experiment outputs and comparison records,
- `results/reports/`: human-readable summaries and interpretations,
- `results/figures/`: analysis figures,
- `results/tables/`: tabular outputs when present.

Notebook work may be useful for exploration, but official workflows are expected to remain reproducible from package code and experiment scripts rather than from notebooks alone.

## Current Official Workflows

At present, the repository contains three official workflows.

The first is the reduced FRW minisuperspace line in `experiments/minisuperspace_frw/`. Its purpose is to provide a benchmarked and interpretable first official experiment for the lab, not to claim a full Wheeler-DeWitt solver or a full quantum-gravity simulation.

The standard execution sequence from the repository root is:

```bash
python experiments/minisuperspace_frw/benchmark.py
python experiments/minisuperspace_frw/run_local.py
python experiments/minisuperspace_frw/run_aer.py
python experiments/minisuperspace_frw/analyze.py
```

These scripts perform the following roles:

- `benchmark.py`: computes the exact reduced-model benchmark,
- `run_local.py`: evaluates the exact local quantum reference workflow,
- `run_aer.py`: evaluates the noisy local simulation workflow,
- `analyze.py`: compares outputs against benchmark values and produces reports and figures.

The corresponding IBM Runtime path is:

```bash
python experiments/minisuperspace_frw/run_ibm.py --backend-name <backend>
```

This command should be used only after the exact-local and noisy-local validation artifacts have been completed and reviewed.

The second is the reduced FLRW particle-creation line in `experiments/particle_creation_flrw/`. Its purpose is to provide a benchmarked and interpretable QFT-in-curved-spacetime workflow for a retained two-mode pair-creation system, not to claim a full continuum inflationary simulation.

The standard execution sequence from the repository root is:

```bash
python experiments/particle_creation_flrw/benchmark.py
python experiments/particle_creation_flrw/run_local.py
python experiments/particle_creation_flrw/run_aer.py
python experiments/particle_creation_flrw/analyze.py
```

The corresponding IBM Runtime path is:

```bash
python experiments/particle_creation_flrw/run_ibm.py --backend-name <backend>
```

This command should likewise be used only after the exact-local and noisy-local validation artifacts have been completed and reviewed.

The third is the reduced toy-gauge line in `experiments/gut_toy_gauge/`. Its purpose is to provide a benchmarked and interpretable Track C gauge toy model for a minimal two-link `Z2` system, not to claim a realistic grand unified gauge simulation.

The standard execution sequence from the repository root is:

```bash
python experiments/gut_toy_gauge/benchmark.py
python experiments/gut_toy_gauge/run_local.py
python experiments/gut_toy_gauge/run_aer.py
python experiments/gut_toy_gauge/analyze.py
```

The corresponding IBM Runtime path is:

```bash
python experiments/gut_toy_gauge/run_ibm.py --backend-name <backend>
```

This command should likewise be used only after the exact-local and noisy-local validation artifacts have been completed and reviewed.

## Local Environment Note for Aer

In the local repository validation performed on macOS arm64 with Python 3.14.2, direct Aer execution from a restrictive sandbox produced an OpenMP shared-memory initialization failure of the form `OMP: Error #178: Function Can't open SHM2 failed`.

In that environment, the noisy-local Aer workflow still succeeded when run outside the restrictive sandbox. This should be treated as an environment or runtime constraint rather than as a scientific failure of the experiment logic itself.

For the most conservative local validation path, prefer:

- Python 3.10 through 3.13 for routine Aer validation,
- a writable matplotlib configuration directory such as `MPLCONFIGDIR=/tmp/mpl` when generating figures in constrained environments,
- non-restrictive local execution for Aer workflows when the host OpenMP runtime requires shared-memory setup.

## Generated Outputs

The `minisuperspace_frw` workflow writes structured outputs to the repository so the scientific record is inspectable:

- benchmark and normalized execution JSON under `data/processed/minisuperspace_frw/`,
- human-readable summaries under `results/reports/minisuperspace_frw/`,
- tabular summaries under `results/tables/minisuperspace_frw/`,
- figures under `results/figures/minisuperspace_frw/`.

The `particle_creation_flrw` workflow writes the analogous structured outputs under:

- `data/processed/particle_creation_flrw/`,
- `results/reports/particle_creation_flrw/`,
- `results/tables/particle_creation_flrw/`,
- `results/figures/particle_creation_flrw/`.

The `gut_toy_gauge` workflow writes the analogous structured outputs under:

- `data/processed/gut_toy_gauge/`,
- `results/reports/gut_toy_gauge/`,
- `results/tables/gut_toy_gauge/`,
- `results/figures/gut_toy_gauge/`.

Users should treat these generated files as supporting evidence for the implemented workflow, not as substitutes for the written model statement in `model.md` or the interpretive discussion in `results.md`.

## IBM Runtime Use

IBM Runtime execution is supported by the repository but intentionally constrained by the lab's benchmark-before-hardware rule and by the requirement that both the exact-local and noisy-local validation artifacts already exist.

Before using the IBM workflow:

1. confirm that the benchmark is reproducible,
2. confirm that exact local execution reproduces the benchmark within the expected numerical tolerance,
3. confirm that noisy local execution remains scientifically interpretable,
4. review [ibm-runtime-setup.md](ibm-runtime-setup.md).

For infrastructure validation when credentials or hardware access are unavailable, the Phase 4 wrapper also supports IBM Runtime local testing mode through fake backends:

```bash
python experiments/minisuperspace_frw/run_ibm.py --local-testing-backend FakeManilaV2
python experiments/particle_creation_flrw/run_ibm.py --local-testing-backend FakeManilaV2
python experiments/gut_toy_gauge/run_ibm.py --local-testing-backend FakeManilaV2
```

These commands validate the repository hardware wrapper, transpilation path, provenance capture, and report generation. They are not real hardware results.

Credentials must never be committed to tracked source files. Use environment variables or approved local credential mechanisms only.

For credential-safe local account setup and validation, the repository also provides:

```bash
python scripts/ibm_runtime/save_account_from_env.py
python scripts/ibm_runtime/check_account.py
```

These helpers are documented in [scripts/ibm_runtime/README.md](../../scripts/ibm_runtime/README.md) and [ibm-runtime-setup.md](ibm-runtime-setup.md).

For completed live IBM hardware runs, the shared writer now preserves both the configured canonical output files and immutable timestamped archive copies. It also appends a run-manifest entry under `data/raw/<experiment>/ibm_runtime_runs.jsonl`. Local-testing-mode runs are not archived automatically by default and now write to separate `_local_testing` IBM artifact files so they do not replace the latest live-hardware record.

## IBM Hardware Validation and Execution Procedure

The following procedure is the recommended repository-standard path for a live IBM hardware submission. It expresses the repository's methodological order directly in terminal form and should be preferred over ad hoc command selection.

From the repository root with the virtual environment active:

```bash
python scripts/ibm_runtime/check_account.py
python experiments/<experiment>/benchmark.py
python experiments/<experiment>/run_local.py
python experiments/<experiment>/run_ibm.py --backend-name <backend>
```

For example, a conservative live submission for the reduced toy-gauge line is:

```bash
python scripts/ibm_runtime/check_account.py
python experiments/gut_toy_gauge/benchmark.py
python experiments/gut_toy_gauge/run_local.py
python experiments/gut_toy_gauge/run_ibm.py --backend-name ibm_fez
```

This procedure has the following interpretation:

1. `check_account.py` confirms that the saved IBM Runtime account is still valid before submission.
2. `benchmark.py` regenerates the benchmark reference used to interpret later tiers.
3. `run_local.py` regenerates the exact-local reference artifacts for the same experiment.
4. `run_ibm.py` submits the live IBM Runtime job only after the account and prior interpretive tiers are in place.

Noisy-local validation remains part of the repository's scientific standard even when it is not rerun immediately before every hardware submission on every host. When a platform-specific Aer environment is stable and convenient, rerunning `run_aer.py` before hardware is still methodologically appropriate.

Successful live IBM runs now preserve both canonical latest-result files and immutable archive copies automatically, and append a manifest entry under `data/raw/<experiment>/ibm_runtime_runs.jsonl`. Local-testing-mode runs remain separate operational artifacts and write to `_local_testing` output paths.

## Provenance and Results Policy

Execution outputs and comparison records should preserve enough metadata to support later review, including backend context, execution tier, seeds, shots or precision, timestamps, observable values, mitigation policy, backend-selection policy, calibration summaries, and runtime job metadata.

Repository-level guidance for that policy is documented in [results-and-provenance.md](results-and-provenance.md).

Phase 6 dissemination and governance materials are documented in:

- [internal-review-checklist.md](internal-review-checklist.md),
- [replication-checklist.md](replication-checklist.md),
- [archival-release-workflow.md](archival-release-workflow.md),
- [figure-and-table-style-guide.md](../methods/figure-and-table-style-guide.md),
- [citation-and-bibliography-policy.md](../references/citation-and-bibliography-policy.md).

## Interpreting Results Carefully

Users of this repository should keep the following limitations explicit:

- a circuit label is not a physical derivation,
- raw computational-basis distributions are not self-interpreting cosmological evidence,
- noise-induced distortions are not early-universe structure,
- reduced toy models remain reduced toy models unless a stronger claim is mathematically justified.

In Version 1 of the repository, scientific credibility depends on modest claims, explicit observables, benchmark agreement, and clear written limits of interpretation.

## Extending the Repository

New official work should not begin by inventing a circuit theme. It should begin with a model, a truncation or discretization, and a declared observable. Before a new experiment is treated as official, it should satisfy the experiment standard in [experiment-standard.md](../methods/experiment-standard.md).

With the three official scientific lines implemented and the baseline Phase 6 governance layer now added, repository-level dissemination work should proceed through the documented citation, review, replication, and archival-release policies rather than through ad hoc summary files.

## Related Documents

For repository use, the most relevant accompanying documents are:

- [README.md](../../README.md)
- [AGENTS.md](../../AGENTS.md)
- [PLANS.md](../../PLANS.md)
- [overview.md](../architecture/overview.md)
- [experiment-standard.md](../methods/experiment-standard.md)
- [ibm-runtime-setup.md](ibm-runtime-setup.md)
- [results-and-provenance.md](results-and-provenance.md)
