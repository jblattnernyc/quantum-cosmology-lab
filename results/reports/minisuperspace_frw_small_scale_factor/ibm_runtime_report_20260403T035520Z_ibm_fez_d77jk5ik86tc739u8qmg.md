# IBM Runtime Hardware Report

## Purpose

This report records the operational context of an IBM Runtime execution tier. It does not establish scientific meaning in isolation from the benchmark, exact-local, and noisy-local tiers.

## Experiment Context

- Experiment: `minisuperspace_frw_small_scale_factor`
- Scientific question: In a four-bin positive-scale-factor truncation of an FRW/Wheeler-DeWitt-inspired minisuperspace operator with a small-scale-factor inverse-square barrier term, what are the benchmark ground-state values of the retained scale-factor expectation, a volume proxy, and the smallest-bin occupation probability, and how accurately do exact local and noisy local quantum workflows reproduce them?
- Execution tier: `ibm_hardware`
- Primitive: `qiskit_ibm_runtime.EstimatorV2`
- Report timestamp (UTC): `2026-04-03T03:55:20.475818+00:00`

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
- Properties last update: `2026-04-02T23:35:14-04:00`
- Pending jobs at capture: `0`
- Backend operational: `True`

## Runtime Job Summary

- Job id: `d77jk5ik86tc739u8qmg`
- Job status: `DONE`
- Job creation date: `2026-04-02T23:55:02.073829-04:00`
- Session id: `None`
- Usage estimation: `{'quantum_seconds': 11.14206373}`

## Observable Comparison

| Observable | Benchmark | Hardware | Abs. error | Rel. error | Uncertainty |
|---|---:|---:|---:|---:|---:|
| scale_factor_expectation_value | 0.340958 | 0.350337 | 0.009379 | 0.027507 | 0.008732 |
| volume_expectation_value | 0.058452 | 0.064417 | 0.005965 | 0.102048 | 0.004128 |
| effective_hamiltonian_expectation | -0.134279 | -0.124945 | 0.009333 | 0.069508 | 0.004225 |
| smallest_scale_factor_probability | 0.114212 | 0.110735 | 0.003477 | 0.030444 | 0.019748 |

## Interpretation Constraint

Hardware output must be read only as a benchmarked execution tier for the declared observables. It does not by itself justify cosmological or field-theoretic interpretation.

## Metadata Artifact

- Raw hardware metadata JSON: `data/raw/minisuperspace_frw_small_scale_factor/ibm_runtime_metadata_20260403T035520Z_ibm_fez_d77jk5ik86tc739u8qmg.json`
