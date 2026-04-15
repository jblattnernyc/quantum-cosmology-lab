# Grand-Unification-Epoch-Context Toy Model

## Status

This directory contains an official Quantum Cosmology Lab experiment line: a
Grand-Unification-Epoch-context reduced `Z2` symmetry-breaking toy model
implemented as a two-site finite Hamiltonian and benchmarked against exact
direct diagonalization.

The implementation is intentionally modest. It is not a literal simulation of
the Grand Unification Epoch, not a realistic grand unified gauge theory, not a
thermal field-theory phase transition, and not a model of `SU(5)`, `SO(10)`,
or any other specific unification group. The epoch label is contextual only.
The experiment studies a small benchmarkable order-parameter toy model that is
appropriate for Track C only because it remains reduced, explicit, and
scientifically limited.

## Scientific Question

In a two-site `Z2` symmetry-breaking toy Hamiltonian used as a reduced
Grand-Unification-Epoch-context model, what are the benchmark ground-state
values of the order-parameter expectation, domain-wall density,
transverse-coherence expectation, and effective-Hamiltonian expectation, and
how accurately do exact local and noisy local estimator workflows reproduce
them?

## Model Summary

The experiment keeps two retained binary order-parameter sites:

- qubit `0`: first retained `Z2` order-parameter site,
- qubit `1`: second retained `Z2` order-parameter site.

The reduced Hamiltonian is

```text
H = -J ZZ - h (IX + XI) / 2 - b (IZ + ZI) / 2
```

with default values:

- `J = 0.7`
- `h = 0.32`
- `b = 0.08`

The alignment term favors ordered configurations, the transverse term mixes
the retained order-parameter states, and the small bias chooses one orientation
so that the finite model has a nonzero order-parameter expectation. These are
toy-model terms, not a derivation of realistic GUT symmetry breaking.

## Core Observables

- `order_parameter_expectation`
- `domain_wall_density`
- `transverse_coherence_expectation`
- `effective_hamiltonian_expectation`

The order parameter is the primary reduced symmetry diagnostic. The domain-wall
density is a two-site anti-alignment proxy. The transverse-coherence observable
diagnoses mixing among retained configurations. The Hamiltonian expectation is
included as a benchmark consistency check.

## Directory Guide

- [model.md](model.md): mathematical statement, truncation, and interpretive limits
- [config.yaml](config.yaml): parameters, execution settings, and artifact paths
- [common.py](common.py): typed configuration, operator, and benchmark helpers
- [benchmark.py](benchmark.py): exact direct diagonalization benchmark
- [circuit.py](circuit.py): two-qubit exact ground-state preparation circuit
- [observables.py](observables.py): Pauli-decomposed observable definitions
- [run_local.py](run_local.py): exact local estimator workflow
- [run_aer.py](run_aer.py): noisy local workflow with Aer or guarded analytic readout fallback
- [run_ibm.py](run_ibm.py): optional IBM Runtime workflow
- [analyze.py](analyze.py): comparison analysis and figure generation
- [results.md](results.md): written interpretation and limitations

## Reproducible Workflow

From the repository root with the virtual environment active:

```bash
python experiments/grand_unification_epoch_toy/benchmark.py
python experiments/grand_unification_epoch_toy/run_local.py
python experiments/grand_unification_epoch_toy/run_aer.py
python experiments/grand_unification_epoch_toy/analyze.py
```

The IBM Runtime path is intentionally separate and should be used only after
the exact-local and noisy-local validation outputs have been reviewed:

```bash
python experiments/grand_unification_epoch_toy/run_ibm.py --backend-name <backend>
```

Credential-free IBM Runtime local testing mode is also available:

```bash
python experiments/grand_unification_epoch_toy/run_ibm.py --local-testing-backend FakeManilaV2
```

This validates the shared Runtime wrapper and provenance path, but it is not a
real hardware result.

