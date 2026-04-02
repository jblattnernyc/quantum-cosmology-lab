# Quantum Cosmology Lab

## PLANS.md

**Document Status:** Foundational roadmap completed through Phase 6; retained as the authoritative program record and change-control document for Version 1  
**Project Status:** Implemented through Phase 6  
**Repository Role:** Root roadmap, program-record, and future-expansion control guide for the official Quantum Cosmology Lab

## 1. Purpose

This document defines the scientific, technical, organizational, and methodological plan by which the official **Quantum Cosmology Lab** was established as a rigorous Qiskit-based research repository, and it remains the governing document for any later programmatic extension. The lab is intended to support reproducible research on reduced models relevant to the early universe, with particular emphasis on quantum cosmology, quantum field theory in curved spacetime, and carefully scoped lattice or symmetry-breaking toy models.

The central objective is to build and preserve a laboratory that is scientifically valid, computationally reproducible, and historically well documented. The lab must therefore be more than a collection of cosmology-themed circuits. It must operate as a research system in which every experiment is derived from a defined model, every observable has a stated physical meaning, and every claim is benchmarked against exact or trusted classical reference results.

## 2. Mission

The mission of the Quantum Cosmology Lab is to:

1. Develop reproducible Qiskit workflows for reduced early-universe models.
2. Establish a rigorous bridge between cosmological theory and quantum computation.
3. Validate model-specific observables across exact simulation, noisy simulation, and IBM Quantum hardware.
4. Produce research outputs that are methodologically transparent, benchmarked, and suitable for academic development.

## 3. Foundational Principles

All work in this repository shall be governed by the following principles.

### 3.1 Model First

No experiment shall begin from a visually interesting circuit. Every experiment must begin from a mathematical model, reduction, Hamiltonian, constraint, or evolution equation.

### 3.2 Observable First

No result shall be interpreted cosmologically unless the measured quantity is a defined observable with a documented physical meaning.

### 3.3 Benchmark Before Hardware

No IBM hardware run shall be treated as scientifically meaningful until the same experiment has been validated by an exact local reference and a noisy simulation workflow.

### 3.4 Reproducibility Over Impression

Screenshots, histograms, and visual outputs are supplementary artifacts. The primary scientific record shall consist of code, configuration, benchmark data, numerical outputs, and written interpretation.

### 3.5 Explicit Limits

The lab must distinguish sharply between:

- true quantum-cosmology models,
- quantum field theory in curved spacetime,
- lattice gauge or symmetry-breaking toy models,
- observational data-analysis applications.

No project shall blur these categories for rhetorical effect.

## 4. Scope

### 4.1 In Scope

- Minisuperspace quantum-cosmology models.
- FRW, de Sitter, or related reduced cosmological backgrounds.
- Wheeler-DeWitt or Hamiltonian-constraint toy formulations.
- Quantum field theory in curved spacetime.
- Cosmological particle creation in expanding backgrounds.
- Reduced early-universe lattice or gauge toy models.
- Error-mitigated expectation-value estimation on IBM hardware.
- Reproducible analysis, documentation, and publication pipelines.

### 4.2 Out of Scope for Version 1

- Claims to full Planck-scale quantum-gravity simulation.
- Claims to full GUT, electroweak, or QCD epoch simulation in realistic field-theory detail.
- Cosmological interpretation based solely on raw computational-basis histograms.
- Unbenchmarked variational results presented as physical conclusions.
- Storage of platform credentials or secrets inside tracked source files.

## 5. Scientific Program

The official lab shall be built around three primary research tracks and one secondary track.

### Track A. Quantum Cosmology Proper

Focus: reduced cosmological models in which the universe is represented by a small set of canonical degrees of freedom.

Examples:

- FRW minisuperspace with scalar field.
- Wheeler-DeWitt toy models.
- Tunneling or bounce scenarios in truncated bases.
- Constraint-satisfaction and expectation-value studies.

Primary observables:

- constraint residuals,
- expectation values of scale-factor operators,
- basis-state amplitudes or probabilities in truncated models,
- transition amplitudes,
- singularity-avoidance diagnostics.

### Track B. Quantum Field Theory in Curved Spacetime

Focus: quantum matter fields evolving on a classical expanding background.

Examples:

- particle creation in time-dependent scale factors,
- two-mode and few-mode scalar-field models,
- squeezing and entanglement generation in expansion,
- inflation-adjacent toy models.

Primary observables:

- particle number,
- mode occupation,
- squeezing parameters,
- entanglement measures,
- Bogoliubov-related expectation values.

### Track C. Early-Universe Field-Theory Toy Models

Focus: reduced models relevant to GUT, electroweak, quark, and hadron-era questions, without claiming full physical completeness.

Examples:

- small \( Z_2 \), \( U(1) \), or \( SU(2) \) lattice gauge systems,
- symmetry-breaking toy Hamiltonians,
- confinement and Gauss-law toy diagnostics,
- small matter-gauge couplings.

Primary observables:

- gauge-invariance violations,
- order parameters,
- Wilson-line or correlator proxies,
- simple confinement indicators,
- excitation spectra in reduced settings.

### Track D. Cosmological Data Analysis and Inference

Focus: quantum-enhanced analysis relevant to later cosmological epochs.

This track is secondary during Version 1 and shall not delay the core simulation program.

Examples:

- exploratory quantum methods for CMB or 21 cm data analysis,
- quantum topological data analysis,
- quantum-enhanced inference prototypes,
- radio astronomy or interferometric toy workflows.

## 6. Official Lab Standard

An experiment shall count as an official Quantum Cosmology Lab experiment only if all of the following are present.

1. A named scientific question.
2. A written model statement.
3. A clearly stated truncation or discretization.
4. A qubit encoding or operator mapping.
5. A declared observable or set of observables.
6. An exact or trusted classical benchmark.
7. A local exact quantum reference run.
8. A noisy simulation run.
9. An optional IBM hardware run, if justified.
10. A written interpretation of what the result does and does not mean physically.

If any of these components is missing, the work may be exploratory but shall not be classified as an official lab result.

## 7. Repository Architecture

The repository shall be structured as follows.

```text
QUANTUM COSMOLOGY LAB/
  PLANS.md
  README.md
  LICENSE
  NOTICE
  .gitignore
  pyproject.toml
  docs/
    architecture/
    methods/
    references/
  src/qclab/
    __init__.py
    models/
    encodings/
    observables/
    circuits/
    benchmarks/
    backends/
    analysis/
    plotting/
    utils/
  experiments/
    minisuperspace_frw/
    particle_creation_flrw/
    gut_toy_gauge/
  notebooks/
  tests/
  data/
    raw/
    processed/
    external/
  results/
    figures/
    tables/
    reports/
  scripts/
```

## 8. Experiment Package Template

Each experiment directory under `experiments/` shall contain, at minimum:

```text
experiment_name/
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

### Required Roles of These Files

- `model.md`: mathematical statement of the problem and references.
- `config.yaml`: parameter choices, truncation levels, backend settings, and run metadata.
- `benchmark.py`: exact or trusted classical reference calculation.
- `circuit.py`: circuit construction and parameter binding.
- `observables.py`: operator definitions and measurement logic.
- `run_local.py`: exact local primitives workflow.
- `run_aer.py`: noisy simulation with explicit simulator settings.
- `run_ibm.py`: real hardware execution with Runtime primitives.
- `analyze.py`: comparison plots, summary tables, and uncertainty analysis.
- `results.md`: narrative interpretation suitable for internal review.

## 9. Software and Infrastructure Standards

### 9.1 Core Stack

The initial software stack shall include:

- Python
- Qiskit
- qiskit-aer
- qiskit-ibm-runtime
- NumPy
- SciPy
- SymPy
- pandas
- matplotlib
- pytest

Optional supporting tools may be added later, but the initial stack should remain compact and fully justified.

### 9.2 Environment Management

The repository shall use a single declared environment in `pyproject.toml`. Dependency sprawl shall be avoided. Locking may be added after the first stable implementation milestone.

### 9.3 Testing

The repository shall include:

- unit tests for encodings and observables,
- regression tests for benchmark values,
- interface tests for experiment configuration loading,
- smoke tests for local simulation pipelines.

### 9.4 Continuous Integration

CI shall be introduced once the first runnable local experiment exists. At minimum, CI must run:

- linting,
- tests,
- benchmark smoke checks,
- import validation.

### 9.5 Security

IBM credentials, API keys, tokens, and instance identifiers shall never be hard-coded into committed source files. Secrets must be loaded from environment variables or approved local credential stores.

## 10. Qiskit Execution Policy

The lab shall use a three-tier execution policy for every official experiment.

### Tier 1. Exact Local Reference

Use exact local primitives or equivalent statevector-based workflows to establish the ideal reference behavior.

Purpose:

- verify circuit logic,
- validate observable definitions,
- detect interpretive errors before noise is introduced.

### Tier 2. Noisy Local Simulation

Use Aer with explicit simulator options and, when appropriate, backend-informed noise models.

Purpose:

- estimate realistic degradation,
- compare ideal and noisy behavior,
- determine whether hardware execution is scientifically worthwhile.

### Tier 3. IBM Hardware

Use IBM Runtime primitives only after Tier 1 and Tier 2 validation has been completed.

Purpose:

- assess hardware feasibility,
- test mitigation strategies,
- evaluate the stability of experimentally accessible observables.

## 11. Interpretation Policy

The following interpretive rules are mandatory.

1. A circuit name shall never substitute for a physical derivation.
2. Phase-only gate sequences measured directly in the computational basis shall not be assigned cosmological meaning unless the measurement basis is scientifically justified.
3. Noise-induced nonuniformity shall not be interpreted as evidence of early-universe structure.
4. All cosmological claims must be tied to explicit operators, models, and reference calculations.
5. Exploratory circuits may be preserved, but they must be labeled as exploratory.

## 12. Phased Roadmap

As of 2026-04-02, Phases 0, 1, 2, 3, 4, 5, and 6 have been implemented at a baseline official level in the repository. No work beyond Phase 6 is implemented in this planning state.

## Phase 0. Repository Foundation

**Current Status:** Complete

**Objective:** Establish the repository as a professional research environment.

### Deliverables

- `README.md`
- `LICENSE`
- `.gitignore`
- `pyproject.toml`
- initial `src/qclab/` package
- initial `tests/` package
- `docs/architecture/overview.md`
- `docs/methods/experiment-standard.md`

### Completion Standard

The repository can be installed locally, imported, and tested without experiment-specific code.

## Phase 1. Core Scientific Infrastructure

**Current Status:** Complete

**Objective:** Build the reusable machinery required for all later experiments.

### Deliverables

- parameterized model configuration loader,
- observable construction utilities,
- benchmark interface,
- backend abstraction for local, Aer, and IBM execution,
- common analysis and plotting helpers.

### Completion Standard

A minimal toy example can pass through benchmark, circuit generation, and local analysis using shared infrastructure.

## Phase 2. First Official Research Line

**Current Status:** Complete

**Target:** `minisuperspace_frw`

### Goals

- implement a reduced FRW or Wheeler-DeWitt-inspired toy model,
- define a tractable truncated Hilbert space,
- construct a Pauli decomposition,
- measure at least one meaningful cosmological observable,
- benchmark against exact numerics.

### Completion Standard

The repository contains one fully reproducible and internally reviewable quantum-cosmology experiment.

## Phase 3. Second Official Research Line

**Current Status:** Complete

**Target:** `particle_creation_flrw`

### Goals

- implement a curved-spacetime particle-creation model,
- encode time-dependent evolution,
- compare particle number or related observables across exact, noisy, and hardware runs,
- document where the model is inflation-adjacent rather than a literal inflation simulation.

### Completion Standard

The repository contains one fully reproducible QFT-in-curved-spacetime experiment.

## Phase 4. Hardware and Mitigation Program

**Current Status:** Complete

**Objective:** Standardize IBM Quantum execution once the first two scientific tracks are stable.

### Deliverables

- common Runtime execution wrapper,
- mitigation configuration policy,
- backend selection policy,
- hardware report template,
- calibration and run metadata capture.

### Completion Standard

Hardware runs can be compared systematically across experiments and dates.

## Phase 5. Third Official Research Line

**Current Status:** Complete

**Target:** `gut_toy_gauge`

### Goals

- implement a small lattice or symmetry-breaking toy model,
- enforce clear language distinguishing toy gauge studies from literal GUT simulation,
- add gauge- or order-parameter observables,
- benchmark interpretability before hardware execution.

### Completion Standard

The repository contains one fully reproducible early-universe field-theory toy experiment.

## Phase 6. Research Dissemination and Governance

**Current Status:** Complete

**Objective:** Prepare the lab for publication-grade outputs and durable maintenance.

### Deliverables

- citation and bibliography policy,
- figure and table style guide,
- internal review checklist,
- replication checklist,
- archival release workflow,
- versioned milestone reports.

### Completion Standard

The repository can support internal reports, formal writeups, and reproducible archival releases.

### 12.1 Roadmap Closure

Phases 0 through 6 constitute the completed founding roadmap for Version 1 of the Quantum Cosmology Lab.

This completed roadmap should be read as:

- the historical record of how the lab was intentionally built,
- the authoritative statement of the repository's founding scientific and organizational program,
- the baseline against which later maintenance, refinement, or expansion should be evaluated.

No Phase 7 is currently defined in this document. Routine maintenance, dissemination updates, release preparation, test upkeep, documentation refinement, or reproducibility refreshes do not by themselves create a new roadmap phase.

### 12.2 Post-Phase-6 Change Control

After completion of Phase 6, no new major programmatic expansion should be treated as an official next phase unless it is first added explicitly to `PLANS.md`.

Any future major phase definition must include, at minimum:

- a stated objective,
- named deliverables,
- a completion standard,
- scope boundaries,
- its relation to the existing official experiment lines,
- its relation to the preserved IBM hardware provenance and archival policy.

Until such a section is added, work after Phase 6 should be interpreted as maintenance, refinement, dissemination, or release management within the existing Version 1 program rather than as a new roadmap phase.

### 12.3 Maintenance Versus Expansion

Post-Phase-6 work should distinguish among three categories.

- **Maintenance:** dependency updates, test upkeep, documentation corrections, CI refinement, release packaging, and reproducibility repairs within the existing repository mission.
- **Refinement:** scientifically modest improvements to the existing official experiment lines, shared infrastructure, reporting, or governance documents that do not alter the repository's core scope.
- **Expansion:** new official research tracks, new major experiment families, new repository-wide methodological tiers, or other changes that materially extend the founding Version 1 program.

Only the third category should ordinarily require definition as a new roadmap phase. The first two categories should be tracked through repository governance documents, results records, and `CHANGELOG.md` rather than by inventing informal successor phases.

## 13. Priority Order

The work shall be executed in the following order.

1. Repository foundation and standards.
2. Reusable scientific infrastructure.
3. Minisuperspace experiment.
4. Particle-creation experiment.
5. Hardware and mitigation framework.
6. Gauge toy-model experiment.
7. Secondary data-analysis track.

The first six priorities have been completed at a baseline official level, and the baseline Phase 6 dissemination-and-governance layer has now been added to support internal reports, formal writeups, and archival release preparation. No Phase 7 work is defined in this planning document.

This ordering reflects the need to establish one mathematically disciplined core line before expanding into broader thematic coverage.

## 14. Definition of Done for Version 1

Version 1 of the Quantum Cosmology Lab shall be considered established when all of the following are true.

1. The repository has a complete project skeleton and declared environment.
2. At least two official experiments are fully reproducible from code alone.
3. At least one experiment belongs to quantum cosmology proper.
4. At least one experiment belongs to quantum field theory in curved spacetime.
5. Each official experiment includes benchmark, local exact, noisy simulation, and analysis workflows.
6. IBM hardware execution is available as an optional, documented tier.
7. Secrets are not stored in tracked files.
8. Tests pass consistently.
9. Documentation clearly distinguishes exploratory work from official results.

## 15. Risk Register

### Scientific Risks

- choosing models too ambitious for current hardware,
- conflating analogy with simulation,
- measuring observables with weak physical interpretability,
- overreading noisy outputs.

### Technical Risks

- dependency instability,
- excessive circuit depth,
- backend drift across time,
- insufficient analysis automation.

### Organizational Risks

- expanding scope before the first reproducible result,
- mixing archival material with official lab outputs,
- inadequate documentation of assumptions and truncations.

## 16. Mitigation Strategy

The lab shall mitigate these risks by:

1. preferring small, publishable reduced models over broad symbolic coverage,
2. requiring benchmark-first development,
3. documenting all approximations explicitly,
4. separating exploratory notebooks from official experiment modules,
5. preserving run metadata and analysis outputs in structured form.

## 17. Documentation Policy

The repository documentation shall distinguish among the following categories.

- **Foundational documents:** mission, plans, architecture, standards.
- **Scientific documents:** model notes, derivations, references.
- **Operational documents:** environment, setup, backend configuration.
- **Result documents:** analyzed outputs and interpretation.
- **Archival documents:** imported historical material from earlier exploratory work.

Historical archive material may be preserved later, but it shall be clearly labeled as pre-repository exploratory work and shall not be confused with official lab experiments.

## 18. Historical Immediate Build List

This section is preserved as a historical record of the repository's founding implementation order. It is no longer an active to-do list after completion of Phase 6.

The following files and directories should be created first.

1. `README.md`
2. `.gitignore`
3. `pyproject.toml`
4. `src/qclab/__init__.py`
5. `tests/test_imports.py`
6. `docs/architecture/overview.md`
7. `docs/methods/experiment-standard.md`
8. `experiments/minisuperspace_frw/README.md`
9. `experiments/particle_creation_flrw/README.md`
10. `experiments/gut_toy_gauge/README.md`

## 19. Final Planning Statement

The official Quantum Cosmology Lab shall be built as a disciplined research repository devoted to reduced, benchmarked, and interpretable early-universe simulations. Its credibility will depend not on the breadth of cosmological labels applied to circuits, but on the precision with which models, encodings, observables, and numerical comparisons are defined and preserved.
