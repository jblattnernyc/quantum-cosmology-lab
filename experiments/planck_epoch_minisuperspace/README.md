# Planck-Epoch-Motivated Minisuperspace

## Status

This directory contains a new official Quantum Cosmology Lab experiment line:
a Planck-Epoch-motivated reduced minisuperspace toy model implemented in a
four-bin positive-scale-factor truncation and benchmarked against exact direct
diagonalization.

The implementation is intentionally modest. It is not a literal simulation of
the Planck Epoch, not a full Wheeler-DeWitt solver, and not a claim about full
Planck-scale quantum gravity. The Planck-Epoch label is contextual motivation
only for why the smallest retained positive-scale-factor sector is resolved
more explicitly in this experiment.

## Scientific Question

In a four-bin positive-scale-factor truncation of an FRW/Wheeler-DeWitt-inspired
minisuperspace operator with a phenomenological small-scale-factor barrier,
what are the benchmark ground-state values of the retained scale factor, volume
proxy, projected Hamiltonian, and smallest-bin occupation probability, and how
accurately do exact local and noisy local quantum workflows reproduce them?

## Model Summary

The experiment keeps four retained positive-scale-factor bins:

- `|a_0>` centered at `a = 0.15`
- `|a_1>` centered at `a = 0.25`
- `|a_2>` centered at `a = 0.4`
- `|a_3>` centered at `a = 0.6`

The reduced effective operator is

```text
H_eff =
  -kappa * sum_j ( |a_j><a_{j+1}| + |a_{j+1}><a_j| )
  + sum_j U(a_j) |a_j><a_j|
```

with

```text
U(a) = mu * a^2 + nu / a^2
```

and default values

- `kappa = 0.1`
- `mu = 0.1`
- `nu = 0.001`

The inverse-square term is a phenomenological small-scale-factor barrier within
the reduced model. It is not a derivation of full Planck-scale quantum
gravitational dynamics.

## Core Observables

- `scale_factor_expectation_value`
- `volume_expectation_value`
- `effective_hamiltonian_expectation`
- `smallest_scale_factor_probability`

The smallest-bin probability is the primary additional diagnostic relative to
the baseline two-bin minisuperspace line. It measures support on the smallest
retained positive-scale-factor bin only.

## Directory Guide

- [model.md](model.md): mathematical statement and limits of interpretation
- [config.yaml](config.yaml): parameter choices, truncation, execution settings, and artifact paths
- [benchmark.py](benchmark.py): exact benchmark wrapper for the declared reduced model
- [circuit.py](circuit.py): state-preparation circuit interface for the benchmark ground state
- [observables.py](observables.py): Pauli-decomposed observable definitions
- [run_local.py](run_local.py): exact local primitives workflow
- [run_aer.py](run_aer.py): noisy local Aer workflow
- [run_ibm.py](run_ibm.py): IBM Runtime workflow, gated behind prior exact-local and noisy-local validation
- [analyze.py](analyze.py): comparison analysis and figure generation
- [results.md](results.md): written interpretation and limitations

## Reproducible Workflow

From the repository root with the virtual environment active:

```bash
python experiments/planck_epoch_minisuperspace/benchmark.py
python experiments/planck_epoch_minisuperspace/run_local.py
python experiments/planck_epoch_minisuperspace/run_aer.py
python experiments/planck_epoch_minisuperspace/analyze.py
```

For the current Apple Silicon Aer runtime note, including the macOS arm64
Python 3.13+ guard status, see the repository
[user guide](../../docs/operations/user-guide.md).

The IBM Runtime path is intentionally separate and should be used only after
the exact-local and noisy-local validation outputs have been reviewed:

```bash
python experiments/planck_epoch_minisuperspace/run_ibm.py --backend-name <backend>
```

The shared hardware workflow also supports credential-free IBM Runtime local
testing mode:

```bash
python experiments/planck_epoch_minisuperspace/run_ibm.py --local-testing-backend FakeManilaV2
```

This validates the shared Runtime wrapper and provenance path, but it is not a
real hardware result.
