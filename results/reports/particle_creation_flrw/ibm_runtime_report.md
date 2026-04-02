# IBM Runtime Hardware Report

## Purpose

This report records the operational context of an IBM Runtime execution tier. It does not establish scientific meaning in isolation from the benchmark, exact-local, and noisy-local tiers.

## Experiment Context

- Experiment: `particle_creation_flrw`
- Scientific question: In a two-mode, single-pair truncation of a scalar field on a prescribed expanding FLRW-like background, what particle-number and pair-correlation observables are produced by an explicit stepwise time-dependent evolution, and how accurately do exact local and noisy local estimator workflows reproduce the benchmark?
- Execution tier: `ibm_hardware`
- Primitive: `qiskit_ibm_runtime.EstimatorV2`
- Report timestamp (UTC): `2026-04-02T00:34:15.918194+00:00`

## Validation Gate

- Benchmark available: `True`
- Exact local validation available: `True`
- Noisy local validation available: `True`

## Backend Selection

- Strategy: `explicit`
- Requested backend: `ibm_fez`
- Selected backend: `ibm_fez`
- Service channel: `ibm_quantum_platform`
- Service instance: `None`
- Local testing mode: `False`

## Mitigation Policy

- Resilience level: `1`
- Measurement mitigation: `True`
- Gate twirling: `None`
- Measurement twirling: `True`
- Dynamical decoupling: `None`
- Requested precision: `0.04`
- Requested shots: `None`
- Optimization level: `1`

## Backend and Calibration Summary

- Backend class: `IBMBackend`
- Backend qubits: `156`
- Calibration id: `None`
- Properties last update: `2026-04-01T20:13:44-04:00`
- Pending jobs at capture: `0`
- Backend operational: `True`

## Runtime Job Summary

- Job id: `d76risohnndc7385m6j0`
- Job status: `DONE`
- Job creation date: `2026-04-01T20:33:55.620932-04:00`
- Session id: `None`
- Usage estimation: `{'quantum_seconds': 10.959236911}`

## Observable Comparison

| Observable | Benchmark | Hardware | Abs. error | Rel. error | Uncertainty |
|---|---:|---:|---:|---:|---:|
| single_mode_particle_number_expectation | 0.034229 | 0.303708 | 0.269480 | 7.872933 | 0.015401 |
| total_particle_number_expectation | 0.068457 | 0.591349 | 0.522892 | 7.638225 | 0.025845 |
| pairing_correlator_expectation | -0.346545 | -0.206725 | 0.139820 | 0.403469 | 0.033241 |

## Interpretation Constraint

Hardware output must be read only as a benchmarked execution tier for the declared observables. It does not by itself justify cosmological or field-theoretic interpretation.

## Metadata Artifact

- Raw hardware metadata JSON: `data/raw/particle_creation_flrw/ibm_runtime_metadata.json`
