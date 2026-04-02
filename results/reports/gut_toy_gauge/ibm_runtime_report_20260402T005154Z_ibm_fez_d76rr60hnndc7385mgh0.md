# IBM Runtime Hardware Report

## Purpose

This report records the operational context of an IBM Runtime execution tier. It does not establish scientific meaning in isolation from the benchmark, exact-local, and noisy-local tiers.

## Experiment Context

- Experiment: `gut_toy_gauge`
- Scientific question: In a reduced two-link Z2 gauge toy Hamiltonian with an explicit gauge-penalty term, what are the benchmark ground-state values of gauge-invariance violation, a link-alignment order parameter, and a Wilson-line correlator proxy, and how accurately do exact local and noisy local estimator workflows reproduce them?
- Execution tier: `ibm_hardware`
- Primitive: `qiskit_ibm_runtime.EstimatorV2`
- Report timestamp (UTC): `2026-04-02T00:51:54.949130+00:00`

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
- Requested precision: `0.05`
- Requested shots: `None`
- Optimization level: `1`

## Backend and Calibration Summary

- Backend class: `IBMBackend`
- Backend qubits: `156`
- Calibration id: `None`
- Properties last update: `2026-04-01T20:40:06-04:00`
- Pending jobs at capture: `0`
- Backend operational: `True`

## Runtime Job Summary

- Job id: `d76rr60hnndc7385mgh0`
- Job status: `DONE`
- Job creation date: `2026-04-01T20:51:36.619850-04:00`
- Session id: `None`
- Usage estimation: `{'quantum_seconds': 11.000829479}`

## Observable Comparison

| Observable | Benchmark | Hardware | Abs. error | Rel. error | Uncertainty |
|---|---:|---:|---:|---:|---:|
| gauge_invariance_violation_expectation | 0.000000 | 0.014667 | 0.014667 | n/a | 0.010141 |
| link_alignment_order_parameter | -0.600000 | -0.606074 | 0.006074 | 0.010123 | 0.021996 |
| wilson_line_correlator_proxy | 0.800000 | 0.753353 | 0.046647 | 0.058309 | 0.027127 |

## Interpretation Constraint

Hardware output must be read only as a benchmarked execution tier for the declared observables. It does not by itself justify cosmological or field-theoretic interpretation.

## Metadata Artifact

- Raw hardware metadata JSON: `data/raw/gut_toy_gauge/ibm_runtime_metadata_20260402T005154Z_ibm_fez_d76rr60hnndc7385mgh0.json`
