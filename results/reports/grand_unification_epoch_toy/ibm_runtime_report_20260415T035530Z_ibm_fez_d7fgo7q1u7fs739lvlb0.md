# IBM Runtime Hardware Report

## Purpose

This report records the operational context of an IBM Runtime execution tier. It does not establish scientific meaning in isolation from the benchmark, exact-local, and noisy-local tiers.

## Experiment Context

- Experiment: `grand_unification_epoch_toy`
- Scientific question: In a two-site Z2 symmetry-breaking toy Hamiltonian used as a reduced Grand-Unification-Epoch-context model, what are the benchmark ground-state values of the order-parameter expectation, domain-wall density, transverse-coherence expectation, and effective-Hamiltonian expectation, and how accurately do exact local and noisy local estimator workflows reproduce them?
- Execution tier: `ibm_hardware`
- Primitive: `qiskit_ibm_runtime.EstimatorV2`
- Report timestamp (UTC): `2026-04-15T03:55:30.621086+00:00`

## Validation Gate

- Benchmark available: `True`
- Exact local validation available: `True`
- Noisy local validation available: `True`

## Backend Selection

- Strategy: `explicit`
- Requested backend: `ibm_fez`
- Selected backend: `ibm_fez`
- Service channel: `ibm_quantum_platform`
- Service instance configured: `True`
- Service instance source: `active_account`
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
- Properties last update: `2026-04-14T23:30:15-04:00`
- Pending jobs at capture: `0`
- Backend operational: `True`

## Runtime Job Summary

- Job id: `d7fgo7q1u7fs739lvlb0`
- Job status: `DONE`
- Job creation date: `2026-04-14T23:55:11.277434-04:00`
- Session id: `None`
- Usage estimation: `{'quantum_seconds': 11.415488242}`

## Observable Comparison

| Observable | Benchmark | Hardware | Abs. error | Rel. error | Uncertainty |
|---|---:|---:|---:|---:|---:|
| order_parameter_expectation | 0.894192 | 0.870875 | 0.023317 | 0.026076 | 0.016890 |
| domain_wall_density | 0.029822 | 0.050907 | 0.021085 | 0.707010 | 0.012942 |
| transverse_coherence_expectation | 0.283399 | 0.275526 | 0.007873 | 0.027782 | 0.022113 |
| effective_hamiltonian_expectation | -0.820472 | -0.786569 | 0.033903 | 0.041322 | 0.019498 |

## Interpretation Constraint

Hardware output must be read only as a benchmarked execution tier for the declared observables. It does not by itself justify cosmological or field-theoretic interpretation.

## Metadata Artifact

- Raw hardware metadata JSON: `data/raw/grand_unification_epoch_toy/ibm_runtime_metadata_20260415T035530Z_ibm_fez_d7fgo7q1u7fs739lvlb0.json`
