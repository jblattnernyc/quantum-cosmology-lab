# IBM Runtime Hardware Report

## Purpose

This report records the operational context of an IBM Runtime execution tier. It does not establish scientific meaning in isolation from the benchmark, exact-local, and noisy-local tiers.

## Experiment Context

- Experiment: `minisuperspace_frw`
- Scientific question: In a two-state positive-scale-factor truncation of an FRW minisuperspace toy Hamiltonian, what are the benchmark ground-state expectation values of the scale-factor and volume operators, and how accurately do exact local and noisy local quantum workflows reproduce them?
- Execution tier: `ibm_hardware`
- Primitive: `qiskit_ibm_runtime.EstimatorV2`
- Report timestamp (UTC): `2026-04-01T23:39:55.166284+00:00`

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
- Requested precision: `0.03`
- Requested shots: `None`
- Optimization level: `1`

## Backend and Calibration Summary

- Backend class: `IBMBackend`
- Backend qubits: `156`
- Calibration id: `None`
- Properties last update: `2026-04-01T18:55:42-04:00`
- Pending jobs at capture: `20`
- Backend operational: `True`

## Runtime Job Summary

- Job id: `d76qp1ohnndc7385l6dg`
- Job status: `DONE`
- Job creation date: `2026-04-01T19:38:47.751878-04:00`
- Session id: `None`
- Usage estimation: `{'quantum_seconds': 12.531153164}`

## Observable Comparison

| Observable | Benchmark | Hardware | Abs. error | Rel. error | Uncertainty |
|---|---:|---:|---:|---:|---:|
| scale_factor_expectation_value | 1.240000 | 1.248784 | 0.008784 | 0.007084 | 0.010243 |
| volume_expectation_value | 2.238400 | 2.266158 | 0.027758 | 0.012401 | 0.032368 |
| effective_hamiltonian_expectation | -0.300000 | -0.304850 | 0.004850 | 0.016166 | 0.005855 |

## Interpretation Constraint

Hardware output must be read only as a benchmarked execution tier for the declared observables. It does not by itself justify cosmological or field-theoretic interpretation.

## Metadata Artifact

- Raw hardware metadata JSON: `data/raw/minisuperspace_frw/ibm_runtime_metadata.json`
