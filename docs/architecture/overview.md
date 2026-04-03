# Architecture Overview

## Purpose

The Quantum Cosmology Lab is designed as a research repository rather than a general quantum-computing sandbox. Its architecture therefore emphasizes explicit model specification, reproducible execution tiers, observable-centered analysis, and disciplined separation between reusable infrastructure and experiment-specific code.

## Architectural Layers

The repository is organized into four primary layers.

### 1. Foundational Governance

The governing documents at repository root define mission, standards, and execution order:

- `AGENTS.md`
- `PLANS.md`
- `README.md`

Within this set, `AGENTS.md` is the primary active governance document, `PLANS.md` preserves the completed Version 1 founding roadmap and major-expansion boundaries, and `README.md` provides the public repository overview.

The preserved Phase 6 Version 1 governance layer also adds repository-standard citation policy, figure and table presentation policy, review and replication checklists, and archival release workflow documentation under `docs/`.

### 2. Shared Package Infrastructure

The `src/qclab/` package contains reusable scientific infrastructure:

- `models/`: model and truncation specifications,
- `encodings/`: qubit-encoding metadata,
- `observables/`: observable declarations, Pauli decompositions, and Qiskit-compatible conversion helpers,
- `circuits/`: shared circuit metadata and infrastructure-only builders,
- `benchmarks/`: reference-result interfaces and callable scalar benchmark helpers,
- `backends/`: execution-tier policy, availability helpers, and estimator-based wrappers for exact local, Aer, and IBM Runtime workflows,
- `analysis/`: benchmark comparison, tolerance checks, and provenance-aware reporting helpers,
- `plotting/`: common figure style and scalar-comparison plotting helpers,
- `utils/`: configuration loading, optional-dependency helpers, and smoke examples.

This package is intended to host reusable logic. It should not contain inflated cosmological claims or experiment-specific interpretations detached from explicit models.

### 3. Experiment Directories

Each official experiment lives under `experiments/` and follows a standard structure:

```text
README.md
model.md
config.yaml
benchmark.py
circuit.py
observables.py
run_local.py
run_aer.py
run_ibm.py
analyze.py
results.md
```

This structure ensures that every official experiment contains a scientific question, a model statement, an explicit truncation, declared observables, benchmark logic, local and noisy execution paths, optional IBM Runtime execution, and a written interpretation.

### 4. Data, Results, and Secondary Workspaces

The repository includes dedicated locations for:

- `data/raw/`
- `data/processed/`
- `data/external/`
- `results/figures/`
- `results/tables/`
- `results/reports/`
- `notebooks/`
- `scripts/`

These locations support provenance, analysis organization, and exploratory work without allowing notebooks or figures to become the sole scientific record.

Within this structure, the preserved Phase 6 Version 1 dissemination outputs use:

- `results/reports/milestones/` for versioned milestone reports,
- `data/processed/releases/` for machine-readable archival release manifests.

The phase-neutral current official experiment layer uses:

- `results/reports/repository/` for current official experiment reports,
- `data/processed/repository/` for machine-readable current official experiment manifests.

## Execution Policy

Official experiments must be structured around three execution tiers:

1. exact local reference,
2. noisy local simulation,
3. IBM hardware execution.

The second and third tiers are subordinate to the benchmarked reference calculation. Hardware execution is an optional final tier, not the starting point of a scientific workflow.

## Current State

The active repository baseline now contains:

- three official experiment lines in `experiments/minisuperspace_frw/`, `experiments/particle_creation_flrw/`, and `experiments/gut_toy_gauge/`,
- shared scientific infrastructure for exact-local, noisy-local, and IBM Runtime execution tiers,
- preserved IBM provenance capture and reporting pathways,
- a repository-level governance and dissemination layer for citation policy, figure and table policy, internal review, replication, and archival release preparation.

The historical Phases 0 through 6 recorded in `PLANS.md` explain how this baseline was constructed, but they are no longer the ordinary gate for routine future official experiment admission. Mission-fit future experiments may be added when they satisfy the repository standards without implying a new roadmap phase.

These implemented lines are deliberately reduced and benchmarked. The `gut_toy_gauge` directory is an official Track C toy-gauge implementation, but it remains a reduced two-link `Z2` toy model and must not be read as a realistic GUT simulation.
