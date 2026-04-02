# Changelog

All notable changes to the Quantum Cosmology Lab repository shall be recorded in this file.

This changelog is intended to document repository-level changes that affect scientific scope, reproducibility, experiment status, interfaces, dependencies, documentation standards, or operational policy. It does not replace experiment-level scientific records such as `model.md`, `results.md`, benchmark artifacts, or analysis outputs.

Formal repository releases are now tracked by semantic-version tags, with `1.0.0` as the first public stable release of the completed Version 1 laboratory baseline.

## [Unreleased]

## [1.0.0] - 2026-04-02

### Added

- Added a repository-root `.gitattributes` file for conservative public-repository line-ending normalization and binary-file handling.
- Added a root `CITATION.cff` file aligned to the new Phase 6 citation policy.
- Added a Phase 6 citation and bibliography policy under `docs/references/`.
- Added a Phase 6 figure and table style guide under `docs/methods/`.
- Added Phase 6 internal-review, replication, and archival-release workflow documents under `docs/operations/`.
- Added shared Phase 6 milestone-report and archival-release helpers under `src/qclab/analysis/milestones.py`.
- Added Phase 6 release scripts under `scripts/release/` for versioned milestone-report and archival-manifest generation.
- Added an initial versioned Phase 6 milestone report and archival release manifest reflecting the preserved official experiment and IBM hardware record.
- Added the third official experiment line in `experiments/gut_toy_gauge/`, including a written model statement, configuration, benchmark workflow, circuit construction, observable definitions, exact local execution, noisy local Aer execution, IBM Runtime workflow, analysis pipeline, and written results interpretation.
- Added generated benchmark, exact-local, noisy-local, report, table, and figure artifacts for the default `gut_toy_gauge` workflow.
- Added automated tests for the implemented `gut_toy_gauge` experiment line, including configuration, benchmark, observable, circuit, exact-local, noisy-local, and analysis checks.
- Added package-style exports for `experiments/gut_toy_gauge/` through a local `__init__.py`.
- Added credential-safe IBM Runtime helper scripts under `scripts/ibm_runtime/` for environment-based account saving and connectivity checks without storing secrets in tracked files.
- Added automatic timestamped archival and JSON Lines manifest capture for completed live IBM Runtime runs through the shared Phase 4 hardware writer, while leaving local-testing-mode runs unarchived by default.
- Added separate `_local_testing` IBM artifact paths so fake-backend local-testing runs no longer overwrite the canonical live-hardware files.
- Added the Phase 4 shared hardware-and-mitigation framework under `src/qclab/backends/hardware.py`, including explicit backend-selection policy, mitigation-policy handling, IBM Runtime local-testing support, calibration capture, runtime-job metadata capture, raw hardware metadata JSON writing, and hardware report generation.
- Added a repository-level user guide in `docs/operations/user-guide.md`.
- Added a repository `Makefile` exposing validated convenience targets for installation, testing, the implemented minisuperspace workflow, and local cleanup.
- Added the second official experiment line in `experiments/particle_creation_flrw/`, including a written model statement, configuration, benchmark workflow, circuit construction, observable definitions, exact local execution, noisy local Aer execution, IBM Runtime workflow, analysis pipeline, and written results interpretation.
- Added generated benchmark, exact-local, noisy-local, report, table, and figure artifacts for the default `particle_creation_flrw` workflow.
- Added automated tests for the implemented `particle_creation_flrw` experiment line, including configuration, benchmark, observable, circuit, and analysis checks.
- Added package-style exports for `experiments/particle_creation_flrw/` through a local `__init__.py`.

### Changed

- Advanced the repository package version from `0.2.0` to `1.0.0` to mark the first public stable release of the completed Version 1 laboratory baseline.
- Advanced the repository package version from `0.1.0` to `0.2.0` to mark the formal Phase 6 archival baseline.
- Normalized repository documentation, generated analysis outputs, milestone reports, release manifests, IBM hardware reports, and IBM run manifests to use repository-relative paths suitable for public publication while preserving the underlying scientific and provenance record.
- Updated release documentation, tests, and CI smoke identifiers so the current public baseline is recorded as `v1.0.0`.
- Reclassified `PLANS.md` from an active build-and-execution plan into the completed Version 1 foundational roadmap, program record, and change-control document for any future major expansion.
- Updated the README to link directly to the current versioned Phase 6 milestone report and archival release manifest.
- Extended CI with Phase 6 smoke coverage for the milestone-report and archival-manifest scripts.
- Updated `AGENTS.md`, `PLANS.md`, `README.md`, architecture documentation, and operations documentation so repository status and workflow descriptions reflect implementation through Phase 6 and the new governance layer.
- Updated repository operations guidance so archival release preparation now references the versioned milestone-report and release-manifest workflow rather than ad hoc release curation.
- Extended the `Makefile`, repository-layout checks, and import-integrity coverage to include the Phase 6 release-reporting surface.
- Added the `data/raw/gut_toy_gauge/` placeholder path and extended CI with a dedicated `gut_toy_gauge` noisy-local Aer smoke so the third official line has closer operational parity with the earlier official experiments.
- Updated the root script index and IBM Runtime operations documentation to describe the repository-local account-helper workflow.
- Updated the IBM provenance documentation so canonical hardware outputs and immutable archive copies are both part of the default live-run policy.
- Updated the IBM operations documentation so local-testing outputs are documented as separate non-canonical artifacts.
- Added a formal `IBM Hardware Validation and Execution Procedure` section to the user guide so live IBM submission steps are documented as a single repository-standard workflow.
- Updated `.gitignore` so `_local_testing` IBM artifact files remain untracked by default while canonical and archived live-hardware records stay trackable.
- Updated `AGENTS.md`, `PLANS.md`, `README.md`, architecture documentation, and operations documentation so repository status and workflow descriptions reflect implementation through Phase 5.
- Extended the `Makefile`, import-integrity tests, and CI workflow with `gut_toy_gauge` targets and smoke coverage consistent with the other official experiment lines.
- Updated the shared IBM Runtime estimator wrapper so hardware execution records backend-selection policy, mitigation policy, backend summary, and runtime-job provenance while supporting backend-aware ISA transpilation with an optional transpiler seed.
- Tightened the benchmark-before-hardware gate so IBM execution now requires existing exact-local and noisy-local validation artifacts in addition to a benchmark definition.
- Extended the official Phase 2 and Phase 3 `run_ibm.py` workflows so they use the shared Phase 4 policy layer, write raw hardware metadata JSON, write a hardware report, and support IBM Runtime local testing mode for credential-free smoke validation.
- Extended official experiment configuration and artifact metadata to include IBM optimization level, mitigation-policy defaults, backend-selection policy defaults, raw hardware metadata paths, and hardware report paths.
- Extended the official analysis workflows so IBM execution JSON, metadata JSON, and hardware report paths are surfaced directly when IBM artifacts are present.
- Extended the `Makefile` and CI workflow with dedicated IBM Runtime local-testing smoke paths.
- Updated `AGENTS.md`, `PLANS.md`, `README.md`, experiment documentation, and operations documentation so repository status and IBM Runtime policy reflect implementation through Phase 4.
- Added direct `pytest` execution to the CI workflow in addition to the existing `unittest` run.
- Extended the `minisuperspace_frw` analysis workflow to generate a markdown observable summary table under `results/tables/minisuperspace_frw/`.
- Clarified in repository metadata and user-facing documentation that Python 3.10 through 3.13 are the currently validated versions and that Python 3.14 and later remain experimental pending broader Aer validation.
- Updated the `Makefile` so `make check` now mirrors the CI validation surface more closely by running both `pytest` and `unittest` before compile checks.
- Added a defensive guard that skips the live Aer integration test on macOS arm64 with Python 3.14 and later, where the current local environment exposed a `libomp` runtime abort during direct `pytest` execution.
- Updated `AGENTS.md` to reflect the current implemented repository state while preserving the governing scientific rules.
- Updated `PLANS.md` so project status, phase state markers, and later-phase ordering match the implemented Phase 3 repository state.
- Updated `README.md` to reflect current roadmap status, correct `zsh`-safe installation guidance, document the two implemented official experiment workflows, and clarify the role of the `Makefile`.
- Updated `.gitignore` to ignore local environment files, coverage outputs, editor metadata, and log files while keeping scientific outputs trackable.
- Updated the CI workflow to use the quoted editable-install extras form.
- Updated repository-layout tests to reflect the implemented baseline and to require the new operational files.
- Updated `AGENTS.md`, `PLANS.md`, `README.md`, and repository operations documentation so status markers and workflow descriptions reflect implementation through Phase 3.
- Updated the `Makefile` to expose convenience targets for the implemented `particle_creation_flrw` workflow.
- Updated CI to run Phase 3 benchmark and exact-local smoke paths in addition to the repository test suites.
- Documented the observed macOS arm64 Python 3.14 Aer/OpenMP shared-memory constraint in the user guide.

### Scientific Status

- The repository now contains one official benchmarked reduced quantum-cosmology experiment in `experiments/minisuperspace_frw/`.
- The repository now also contains one official benchmarked reduced QFT-in-curved-spacetime experiment in `experiments/particle_creation_flrw/`.
- The repository now also contains one official benchmarked reduced Track C toy-gauge experiment in `experiments/gut_toy_gauge/`.
- The repository now also contains the Phase 4 shared hardware-and-mitigation program needed to compare IBM Runtime runs systematically across experiments and dates.
- The `gut_toy_gauge` line remains a reduced toy model and must not be treated as a realistic GUT simulation.

## [2026-04-01] Initial Laboratory Build Through Phase 2

### Added

- Established the Phase 0 repository foundation with a professional `src`-layout Python package, licensing, installation metadata, baseline documentation, and test scaffolding.
- Added the shared Phase 1 scientific infrastructure under `src/qclab/`, including model-specification structures, configuration loading, observable-construction utilities, benchmark interfaces, execution-tier abstractions, analysis helpers, plotting helpers, and provenance-aware serialization utilities.
- Added architecture, methods, and operations documentation, including repository architecture guidance, the official experiment standard, IBM Runtime setup policy, and results-and-provenance conventions.
- Added guarded automated tests for imports, configuration validation, observable construction, benchmark helpers, backend execution wrappers, reporting utilities, repository layout, and live local Qiskit integration when dependencies are available.
- Added a baseline continuous-integration workflow for installation, import validation, tests, and compile checks.
- Added the first official experiment line in `experiments/minisuperspace_frw/`, including a written model statement, configuration, benchmark workflow, circuit construction, observable definitions, exact local execution, noisy local Aer execution, IBM Runtime workflow, analysis pipeline, and written results interpretation.
- Added generated benchmark, exact-local, noisy-local, report, and figure artifacts for the default `minisuperspace_frw` workflow.

### Changed

- Constrained the core Qiskit stack in `pyproject.toml` to the currently implemented primitive and Runtime API generation.
- Standardized repository guidance around the three-tier execution policy: exact local reference, noisy local simulation, and IBM hardware execution only after prior validation.
- Updated the top-level repository documentation to reflect completion of Phases 0 and 1 and implementation of the first official Phase 2 experiment.

### Scientific Status

- The repository now contains one official benchmarked reduced quantum-cosmology experiment in `experiments/minisuperspace_frw/`.
- The `experiments/particle_creation_flrw/` and `experiments/gut_toy_gauge/` directories remain scaffolds and must not be treated as validated official experiment results.
- Version 1 remains explicitly limited to reduced, benchmarked, and interpretable models. It does not claim full Planck-scale quantum-gravity simulation or full realistic GUT, electroweak, or QCD epoch simulation.
