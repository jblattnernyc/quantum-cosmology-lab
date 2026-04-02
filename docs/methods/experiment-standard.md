# Official Experiment Standard

## Purpose

This document defines the minimum standard required for an experiment to count as an official Quantum Cosmology Lab experiment rather than an exploratory scaffold or development artifact.

## Required Scientific Elements

An official experiment must include all of the following:

1. A named scientific question.
2. A written model statement.
3. A clearly stated truncation or discretization.
4. A qubit encoding or operator mapping.
5. A declared observable or set of observables.
6. An exact or trusted classical benchmark.
7. A local exact quantum reference workflow.
8. A noisy local simulation workflow.
9. An IBM hardware workflow, when scientifically justified, with explicit backend-selection policy, explicit mitigation policy, metadata capture, and a hardware report.
10. A written interpretation of what the results do and do not establish.

If any element is absent, the work may still be useful, but it must be labeled as exploratory, developmental, or archival rather than official.

## Mandatory Interpretive Rules

The following rules apply to all official experiments:

- A circuit name is not a physical derivation.
- Raw computational-basis histograms are not self-interpreting cosmological evidence.
- Noise-induced nonuniformity is not cosmological structure.
- Claims about early-universe physics must be tied to explicit models, operators, and benchmarks.
- Toy gauge or symmetry-breaking studies must remain clearly labeled as toy models unless a stronger claim is rigorously justified.

## Required Directory Structure

Each experiment directory must contain:

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

## Roles of the Standard Files

- `README.md`: scope, status, and directory-specific orientation.
- `model.md`: mathematical statement, assumptions, and references.
- `config.yaml`: parameters, truncations, backend settings, and execution metadata.
- `benchmark.py`: exact or trusted reference calculation.
- `circuit.py`: circuit construction logic.
- `observables.py`: physically interpretable observable definitions.
- `run_local.py`: exact local execution path.
- `run_aer.py`: noisy local simulation path.
- `run_ibm.py`: IBM Runtime execution path with explicit hardware policy and provenance capture.
- `analyze.py`: comparison analysis and report generation.
- `results.md`: interpretation and limitations.

## Review Checklist

Before an experiment is treated as official, confirm the following:

- the model is mathematically explicit,
- the truncation is justified,
- the observable has stated physical meaning,
- the benchmark exists and is reproducible,
- local exact and noisy workflows agree to an interpretable degree,
- hardware, if used, is presented as a validated comparison tier rather than primary evidence,
- any IBM tier records backend-selection policy, mitigation policy, metadata capture, and a hardware report,
- written interpretation distinguishes result from speculation.
