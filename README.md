# Quantum Cosmology Lab

The Quantum Cosmology Lab is a professional research repository for reduced, benchmarked, and reproducible quantum-computational studies of early-universe models using Qiskit and related scientific Python tooling.

## Repository Status

This repository is currently implemented through **Phase 6** of the laboratory roadmap in [PLANS.md](PLANS.md).

Completed milestones:

- Phase 0: repository foundation and project standards.
- Phase 1: reusable scientific infrastructure for later experiments.
- Phase 2: the first official `minisuperspace_frw` reduced toy experiment.
- Phase 3: the second official `particle_creation_flrw` reduced QFT-in-curved-spacetime experiment.
- Phase 4: the shared hardware-and-mitigation framework for IBM Runtime execution, provenance capture, and hardware reporting.
- Phase 5: the third official `gut_toy_gauge` reduced toy-gauge experiment.
- Phase 6: repository-level dissemination and governance, including citation policy, figure and table guidance, internal review and replication checklists, archival release workflow, and versioned milestone reporting.

The repository now contains three benchmarked official experiments, spanning reduced quantum cosmology, reduced quantum field theory in curved spacetime, and reduced toy-gauge studies, together with the shared infrastructure, documentation, tests, and hardware-execution policy required to extend the lab further.

No Phase 7 or later work is implemented in this repository state.
Any future major expansion must be defined explicitly in `PLANS.md` before implementation begins.

## Current Release Artifacts

The current repository-level Phase 6 archival baseline for the first public stable release is recorded in:

- [v1.0.0-phase6-20260402.md](results/reports/milestones/v1.0.0-phase6-20260402.md)
- [v1.0.0-phase6-20260402_manifest.json](data/processed/releases/v1.0.0-phase6-20260402_manifest.json)

These repository-level release artifacts summarize and package the preserved official experiment and IBM provenance record. They do not replace the experiment-level `model.md`, `results.md`, benchmark artifacts, or per-experiment IBM manifests.

The earlier `v0.1.0` and `v0.2.0` Phase 6 outputs are preserved as internal historical development baselines rather than as the first public release.

Phase 1 shared infrastructure now includes:

- validated experiment-configuration loading,
- explicit observable and Pauli-decomposition utilities,
- benchmark wrappers for scalar reference calculations,
- estimator-based backend wrappers for exact local, Aer, and IBM Runtime execution tiers,
- explicit IBM backend-selection and mitigation-policy helpers,
- calibration and runtime-metadata capture for IBM execution,
- repository-standard IBM hardware metadata JSON and report generation,
- provenance-aware comparison, serialization, and reporting helpers,
- conservative plotting utilities for scalar benchmark comparisons.

The repository now also includes:

- guarded live Qiskit integration tests for installed primitives,
- a baseline GitHub Actions CI workflow,
- operational documentation for IBM Runtime setup and results provenance,
- repository-level dissemination and governance documentation for citation, presentation, review, replication, and archival release curation,
- Phase 6 milestone-report and archival-manifest scripts aligned to the preserved IBM provenance structure,
- tighter Qiskit-stack dependency constraints aligned to the currently implemented API generation.

## Scientific Scope

Version 1 of the lab is intentionally limited to reduced and benchmarked models. The principal research lines are:

- quantum cosmology proper in reduced minisuperspace settings,
- quantum field theory in curved spacetime,
- carefully labeled early-universe field-theory toy models.

The repository is not intended to support unqualified claims of full Planck-scale quantum-gravity simulation or full realistic GUT, electroweak, or QCD epoch simulation. Cosmological interpretation is reserved for model-driven results with explicit observables and trusted reference calculations.

## Methodological Commitments

All official lab work is governed by the following constraints:

- model first,
- observable first,
- benchmark before hardware,
- explicit truncations and approximations,
- disciplined separation of validated results from exploratory work.

IBM Quantum hardware is treated as an optional third execution tier that follows benchmark construction, exact local reference validation, and noisy local simulation validation.

## Repository Layout

```text
src/qclab/               Reusable package code and shared infrastructure
docs/                    Architecture and methods documentation
experiments/             Official experiment directories and templates
tests/                   Import, structure, and infrastructure smoke tests
data/                    Raw, processed, and external data locations
results/                 Figures, tables, and report outputs
notebooks/               Secondary exploratory notebook work
scripts/                 Operational scripts and utilities
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

The quoted extras specifier is intentional and avoids `zsh` glob expansion errors.

The package declares the compact initial scientific software stack required by the lab, including Qiskit, Aer, IBM Runtime, NumPy, SciPy, SymPy, pandas, matplotlib, pytest, and YAML support for experiment configuration files.

The current dependency constraints target the Qiskit 2.2+ primitive generation used by the shared backend wrappers.

The repository's validated CI matrix currently covers Python 3.10 through 3.13. Python 3.14 and later should be treated as experimental until the full test and Aer execution surface has been validated there.

A small [Makefile](Makefile) is provided as a convenience interface for routine repository commands. It does not replace the experiment scripts, `pyproject.toml`, or the governing documents.

The `Makefile` now exposes convenience targets for all three implemented official lines, including `minisuperspace`, `particle-creation`, and `gut-toy-gauge`, together with tier-specific benchmark, local, Aer, analysis, and IBM wrapper targets.

## Testing

After installation, run:

```bash
python -m pytest
```

In environments where `pytest` is not yet installed, the baseline test suite can also be exercised with:

```bash
python -m unittest discover -s tests -v
```

Some integration tests are intentionally guarded. Exact-local primitive tests run when `qiskit` is installed, and noisy-local Aer tests run only when `qiskit-aer` is installed.

## Reproducing the Official Experiments

The first official experiment line is [experiments/minisuperspace_frw/README.md](experiments/minisuperspace_frw/README.md). From the repository root with the virtual environment active, run:

```bash
python experiments/minisuperspace_frw/benchmark.py
python experiments/minisuperspace_frw/run_local.py
python experiments/minisuperspace_frw/run_aer.py
python experiments/minisuperspace_frw/analyze.py
```

This workflow generates benchmark and execution artifacts under `data/processed/minisuperspace_frw/`, together with analysis outputs under `results/reports/minisuperspace_frw/`, `results/tables/minisuperspace_frw/`, and `results/figures/minisuperspace_frw/`.

The IBM Runtime path is implemented separately and should be used only after the exact-local and noisy-local validation artifacts are present:

```bash
python experiments/minisuperspace_frw/run_ibm.py --backend-name <backend>
```

For credential-free infrastructure validation of the IBM wrapper itself, the shared Phase 4 layer also supports IBM Runtime local testing mode through fake backends:

```bash
python experiments/minisuperspace_frw/run_ibm.py --local-testing-backend FakeManilaV2
```

The second official experiment line is [experiments/particle_creation_flrw/README.md](experiments/particle_creation_flrw/README.md). From the repository root with the virtual environment active, run:

```bash
python experiments/particle_creation_flrw/benchmark.py
python experiments/particle_creation_flrw/run_local.py
python experiments/particle_creation_flrw/run_aer.py
python experiments/particle_creation_flrw/analyze.py
```

This workflow generates benchmark and execution artifacts under `data/processed/particle_creation_flrw/`, together with analysis outputs under `results/reports/particle_creation_flrw/`, `results/tables/particle_creation_flrw/`, and `results/figures/particle_creation_flrw/`.

The IBM Runtime path is implemented separately and should be used only after the exact-local and noisy-local validation artifacts are present:

```bash
python experiments/particle_creation_flrw/run_ibm.py --backend-name <backend>
```

The same local-testing-mode validation path is available for the particle-creation line:

```bash
python experiments/particle_creation_flrw/run_ibm.py --local-testing-backend FakeManilaV2
```

The third official experiment line is [experiments/gut_toy_gauge/README.md](experiments/gut_toy_gauge/README.md). From the repository root with the virtual environment active, run:

```bash
python experiments/gut_toy_gauge/benchmark.py
python experiments/gut_toy_gauge/run_local.py
python experiments/gut_toy_gauge/run_aer.py
python experiments/gut_toy_gauge/analyze.py
```

This workflow generates benchmark and execution artifacts under `data/processed/gut_toy_gauge/`, together with analysis outputs under `results/reports/gut_toy_gauge/`, `results/tables/gut_toy_gauge/`, and `results/figures/gut_toy_gauge/`.

The IBM Runtime path is implemented separately and should be used only after the exact-local and noisy-local validation artifacts are present:

```bash
python experiments/gut_toy_gauge/run_ibm.py --backend-name <backend>
```

The same local-testing-mode validation path is available for the toy-gauge line:

```bash
python experiments/gut_toy_gauge/run_ibm.py --local-testing-backend FakeManilaV2
```

## Operations

Operational guidance is documented in:

- [docs/operations/user-guide.md](docs/operations/user-guide.md)
- [docs/operations/ibm-runtime-setup.md](docs/operations/ibm-runtime-setup.md)
- [docs/operations/results-and-provenance.md](docs/operations/results-and-provenance.md)
- [docs/operations/internal-review-checklist.md](docs/operations/internal-review-checklist.md)
- [docs/operations/replication-checklist.md](docs/operations/replication-checklist.md)
- [docs/operations/archival-release-workflow.md](docs/operations/archival-release-workflow.md)
- [docs/methods/figure-and-table-style-guide.md](docs/methods/figure-and-table-style-guide.md)
- [docs/references/citation-and-bibliography-policy.md](docs/references/citation-and-bibliography-policy.md)
- [scripts/ibm_runtime/README.md](scripts/ibm_runtime/README.md)
- [scripts/release/README.md](scripts/release/README.md)
- [CHANGELOG.md](CHANGELOG.md)

## Initial Official Experiment Lines

The first official experiment lines for this repository are:

1. `experiments/minisuperspace_frw/` implemented
2. `experiments/particle_creation_flrw/` implemented
3. `experiments/gut_toy_gauge/` implemented

All three experiment directories listed above are now implemented official lines. The `gut_toy_gauge` experiment is a reduced Track C toy-gauge model and must not be described as a realistic GUT simulation.

## Security and Credentials

Tracked source files must never contain IBM Quantum credentials, API keys, tokens, instance identifiers, or other secrets. Runtime access must be configured through environment variables or approved local credential mechanisms.
