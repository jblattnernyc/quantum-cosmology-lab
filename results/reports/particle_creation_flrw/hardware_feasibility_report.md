# Particle-Creation FLRW Hardware-Feasibility Report

## Status

**Exploratory transpilation only. Live hardware recommendation: DEFER.**

No circuit was executed, no Runtime service was created, and no job was submitted.

## Method

Circuits with `N = 6, 12, 24` were mapped to `FakeManilaV2` at optimization level `1` with the `translator` translation method across 5 deterministic seeds.
The aggregate error proxy multiplies independent calibrated gate success probabilities. It omits readout, idling, crosstalk, coherent effects, observable synthesis, and mitigation and is not fidelity.
The study required current, passing independent-validation evidence; the exact input path and SHA-256 digest are recorded in the JSON artifact.

## Result

`N = 6` has the lowest structural hardware cost among the compared candidates. Its median transpiled depth is `73.0`, its median two-qubit gate count is `24.0`, and its median two-qubit calibration-error proxy is `0.191687`.
At `N = 24`, the continuum-interpolation observable error decreases to `3.986591e-04`, but the two-qubit burden and calibration-error proxy increase.

## Decision

Retain `N = 6` only as the least costly declared discrete candidate. The study does not authorize a live run because the calibration is a fixed fake-backend snapshot and structural proxies do not establish observable accuracy.
A current real-backend transpilation assessment and an acceptable noisy or local-testing observable assessment remain required. If the noise-versus-discretization tradeoff remains unacceptable after the current symmetric splitting refinement, reassess the slice count and backend mapping before considering live execution.

## Artifacts

- JSON evidence: `data/processed/particle_creation_flrw/hardware_feasibility.json`
- Summary table: `results/tables/particle_creation_flrw/hardware_feasibility_summary.md`

## Method References

- [IBM Quantum transpilation guide](https://quantum.cloud.ibm.com/docs/en/guides/transpile)
- [IBM Quantum optimization-level guide](https://quantum.cloud.ibm.com/docs/en/guides/set-optimization)

This result concerns the reduced experiment `particle_creation_flrw` only.
