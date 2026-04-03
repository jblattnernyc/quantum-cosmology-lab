# IBM Runtime Hardware Report

## Purpose

This report records the operational context of an IBM Runtime execution tier. It does not establish scientific meaning in isolation from the benchmark, exact-local, and noisy-local tiers.

## Experiment Context

- Experiment: `planck_epoch_minisuperspace`
- Scientific question: In a four-bin positive-scale-factor truncation of an FRW/Wheeler-DeWitt-inspired minisuperspace operator with a phenomenological small-scale-factor barrier, what are the benchmark ground-state values of the retained scale factor, volume proxy, projected Hamiltonian, and smallest-bin occupation probability, and how accurately do exact local and noisy local quantum workflows reproduce them?
- Execution tier: `ibm_hardware`
- Primitive: `qiskit_ibm_runtime.EstimatorV2`
- Report timestamp (UTC): `2026-04-03T20:52:08.811948+00:00`

## Validation Gate

- Benchmark available: `True`
- Exact local validation available: `True`
- Noisy local validation available: `True`

## Backend Selection

- Strategy: `explicit`
- Requested backend: `ibm_kingston`
- Selected backend: `ibm_kingston`
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
- Properties last update: `2026-04-03T16:15:32-04:00`
- Pending jobs at capture: `0`
- Backend operational: `True`

## Runtime Job Summary

- Job id: `d782gp9q1efs73d18kng`
- Job status: `DONE`
- Job creation date: `2026-04-03T16:51:49.814317-04:00`
- Session id: `None`
- Usage estimation: `{'quantum_seconds': 11.424942786}`

## Observable Comparison

| Observable | Benchmark | Hardware | Abs. error | Rel. error | Uncertainty |
|---|---:|---:|---:|---:|---:|
| scale_factor_expectation_value | 0.340958 | 0.340249 | 0.000709 | 0.002079 | 0.005740 |
| volume_expectation_value | 0.058452 | 0.058641 | 0.000190 | 0.003242 | 0.002902 |
| effective_hamiltonian_expectation | -0.134279 | -0.133992 | 0.000287 | 0.002136 | 0.003347 |
| smallest_scale_factor_probability | 0.114212 | 0.113559 | 0.000653 | 0.005718 | 0.015396 |

## Interpretation Constraint

Hardware output must be read only as a benchmarked execution tier for the declared observables. It does not by itself justify cosmological or field-theoretic interpretation.

## Metadata Artifact

- Raw hardware metadata JSON: `data/raw/planck_epoch_minisuperspace/ibm_runtime_metadata.json`
