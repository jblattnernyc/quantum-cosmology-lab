# AGENTS.md

## Quantum Cosmology Lab

This file defines the working rules for agents operating in the **Quantum Cosmology Lab** repository. It applies to all code, documentation, analysis, experiment design, and interpretation work performed in this repository.

This repository is a professional research lab for **reduced, benchmarked, and reproducible** quantum-computational studies of early-universe models using Qiskit and related scientific Python tooling. It already contains the foundational repository layers, shared scientific infrastructure, and official reduced experiment lines across quantum cosmology, curved-spacetime particle creation, and toy-gauge studies, and it is expected to continue expanding in a phased and methodologically disciplined manner.

## 1. Authority and Priority

Agents must treat the following documents as governing sources, in this order:

1. `AGENTS.md`
2. `PLANS.md`
3. repository source code and experiment documentation

If a conflict appears between implementation convenience and scientific rigor, scientific rigor takes priority.

## 2. Repository Identity

This repository is **not** a general quantum-computing sandbox. It is a research repository focused on:

- quantum cosmology proper in reduced models,
- quantum field theory in curved spacetime,
- early-universe field-theory toy models,
- reproducible numerical and hardware validation workflows.

Agents must preserve this identity. Work that does not support that mission should not be introduced without a clear justification.

## 3. Non-Negotiable Scientific Rules

### 3.1 Model First

Do not begin from a circuit concept, visual pattern, or thematic label. Begin from a mathematical model, reduction, Hamiltonian, constraint, evolution equation, or literature-grounded toy system.

### 3.2 Observable First

Do not interpret a result cosmologically unless the measured quantity is an explicitly defined observable with a stated physical meaning.

### 3.3 Benchmark Before Hardware

No IBM hardware result may be treated as scientifically meaningful until the same experiment has been validated against:

- an exact or trusted classical benchmark,
- an exact local quantum reference,
- a noisy simulation workflow, when relevant.

### 3.4 No Analogy Inflation

Do not describe a circuit as simulating the Planck epoch, Grand Unification epoch, inflation, or other cosmological regimes unless that claim is supported by an explicit model and observable mapping. Cosmology-themed toy circuits must be labeled as toy models or exploratory analogies.

### 3.5 No Noise Romanticism

Do not interpret noisy histograms, hardware distortions, or nonuniform shot distributions as evidence of cosmological structure unless a benchmarked analysis demonstrates that the effect is model-derived rather than noise-derived.

## 4. Scope Boundaries

### In Scope

- minisuperspace and reduced quantum-cosmology models,
- FRW or related reduced cosmological backgrounds,
- Wheeler-DeWitt-inspired toy models,
- particle creation and field dynamics in curved spacetime,
- small lattice or symmetry-breaking toy models relevant to early-universe physics,
- reproducible benchmark, Aer, and IBM Runtime workflows,
- analysis, plotting, and documentation infrastructure for those tasks.

### Out of Scope for Routine Work

- unqualified claims of full quantum-gravity simulation,
- unqualified claims of full GUT or QCD epoch simulation,
- repository clutter unrelated to the lab mission,
- ad hoc screenshots as primary scientific evidence,
- hard-coded credentials, tokens, or platform secrets.

## 5. Required Working Method

Agents must follow this workflow for substantial scientific or code changes.

1. Read the relevant parts of `PLANS.md` and any experiment-local documentation before changing code.
2. Identify the scientific question and the mathematical object being implemented.
3. State or encode the truncation, discretization, and assumptions explicitly.
4. Implement or update the benchmark first, or at minimum in parallel with the circuit logic.
5. Implement observables explicitly rather than inferring meaning from raw bitstrings.
6. Validate locally before proposing or running hardware execution.
7. Document limits of interpretation in the experiment’s results or method files.

If the task is exploratory, the work must still document that status clearly.

## 6. Official Experiment Standard

An experiment is not an official lab experiment unless it includes all of the following.

1. A named scientific question.
2. A written model statement.
3. A defined truncation or discretization.
4. A qubit encoding or operator mapping.
5. A declared observable or set of observables.
6. A benchmark implementation.
7. A local exact execution path.
8. A noisy simulation path, when relevant.
9. A documented IBM hardware path, if hardware use is justified.
10. A written interpretation that distinguishes result from speculation.

Agents must not silently elevate exploratory material to official status.

## 7. Experiment Directory Rules

When creating or extending an experiment under `experiments/`, agents should preserve the following structure unless there is a documented reason not to do so:

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

If a file is omitted, the reason must be explicit in the experiment `README.md`.

## 8. Coding Standards

### 8.1 General

- Prefer clear, maintainable Python over compact cleverness.
- Keep scientific logic explicit and inspectable.
- Use descriptive names for physical parameters, operators, and observables.
- Avoid hidden state and undocumented conventions.
- Add concise comments where mathematical intent would otherwise be unclear.

### 8.2 Reproducibility

- Keep parameters in structured configuration when practical.
- Avoid magic numbers without explanation.
- Record backend choices, shot counts, seeds, truncation levels, and mitigation settings.
- Do not make notebooks the sole source of truth for official workflows.

### 8.3 Numerical Discipline

- Be explicit about basis conventions.
- Be explicit about units or dimensionless rescalings.
- Distinguish exact values from approximations.
- Include tolerances in tests for floating-point comparisons.

## 9. Qiskit Policy

### 9.1 Use the Current Supported Workflow

For temporally unstable API details, agents must verify current Qiskit and IBM Runtime guidance from official documentation before making architectural claims or implementing version-sensitive patterns.

### 9.2 Preferred Execution Layers

Agents should structure work in three layers:

- exact local reference,
- noisy local simulation,
- IBM hardware execution.

Where expectation values are the true scientific quantity, prefer estimator-style workflows over raw sampling workflows.

### 9.3 Hardware Restraint

Do not rush to hardware. If an experiment is not scientifically interpretable under exact and noisy local validation, it is not ready for IBM Quantum execution.

## 10. Documentation Standards

Agents must write documentation in a professional academic style.

Documentation should:

- define the scientific question clearly,
- identify the model and approximation scheme,
- explain what the code computes,
- identify what the outputs mean physically,
- identify what the outputs do not establish physically,
- cite relevant primary literature when appropriate.

Avoid promotional language, inflated claims, and vague phrases such as “simulates the early universe” unless that statement is precisely justified.

## 11. Testing Standards

Agents must add or update tests when changing scientific code, encodings, observables, or benchmark logic.

At minimum, tests should cover:

- import integrity,
- benchmark correctness on small cases,
- observable construction,
- circuit-generation sanity for expected dimensions or parameters,
- regression checks for known values or conserved quantities when applicable.

If a test cannot reasonably be added, the reason must be stated in the final work summary.

## 12. Data and Results Policy

### 12.1 Raw and Processed Data

- Store raw outputs separately from processed outputs.
- Preserve provenance for generated tables and figures.
- Do not overwrite significant results without reason.

### 12.2 Figures and Tables

- Figures should support analysis, not substitute for it.
- Tables should identify parameters, backend context, and uncertainty where appropriate.

### 12.3 Historical Material

If earlier exploratory archive material is imported later, it must be labeled clearly as historical or exploratory. It must not be confused with official lab experiments.

## 13. Security and Credentials

Agents must never commit:

- API keys,
- tokens,
- CRNs,
- account credentials,
- environment-specific secrets.

Use environment variables or approved local credential mechanisms. If credentials are found in tracked files, agents should treat that as a security issue and avoid reproducing the secret value in outputs.

## 14. Communication Standards

When describing work, agents must:

- use formal, precise language,
- distinguish implementation from interpretation,
- distinguish benchmark results from hardware results,
- identify assumptions and unresolved uncertainties,
- avoid overstating what a result proves.

When uncertainty exists, state it directly.

## 15. Prohibited Practices

Agents must not:

- add cosmological labels to circuits without a model basis,
- treat raw bitstring histograms as self-interpreting physical evidence,
- prioritize visual novelty over scientific validity,
- bury essential assumptions in code without documentation,
- introduce unnecessary dependencies,
- commit secrets,
- present exploratory work as validated research.

## 16. Preferred Initial Priorities

Until the repository fully matures, agents should prioritize work in this order:

1. repository foundations,
2. shared scientific infrastructure,
3. minisuperspace quantum-cosmology experiment,
4. curved-spacetime particle-creation experiment,
5. hardware and mitigation framework,
6. early-universe toy gauge experiment,
7. secondary data-analysis workflows.

At the current repository state, the first six priorities have already been implemented at a baseline official level, and the baseline Phase 6 dissemination and governance layer is also now present. Agents working after that milestone should ordinarily treat maintenance, rigorous refinement of the implemented experiment lines and shared hardware framework, and carefully documented dissemination updates as the active priorities.

## 17. Definition of Good Agent Work in This Repository

Good work in this repository has the following characteristics:

- mathematically explicit,
- scientifically modest in its claims,
- reproducible from code,
- benchmarked before interpretation,
- clearly documented,
- modular enough to support later extension,
- careful about the distinction between toy model and physical claim.

## 18. Final Rule

The Quantum Cosmology Lab must be built as a disciplined scientific instrument. Agents should therefore optimize for rigor, reproducibility, and interpretive precision rather than speed, novelty, or rhetorical ambition.
