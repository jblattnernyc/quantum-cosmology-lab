# Minisuperspace FRW

## Status

This directory now contains the first official Quantum Cosmology Lab experiment line: a reduced FRW minisuperspace toy model implemented in a two-state truncation and benchmarked against exact direct diagonalization.

The implementation is intentionally modest. It is not a full Wheeler-DeWitt solver, not a full quantum-gravity simulation, and not a claim about Planck-scale cosmological dynamics. It is a benchmarked reduced model designed to establish a disciplined first official experiment line for the lab.

## Scientific Question

In a two-state truncation of the positive-scale-factor sector of an FRW minisuperspace toy Hamiltonian, what are the benchmark ground-state expectation values of the scale-factor and volume operators, and how accurately can exact local and noisy local quantum workflows reproduce them?

## Model Summary

The experiment retains two representative scale-factor bins:

- `|0>`: lower positive-scale-factor bin centered at `a = 0.6`
- `|1>`: higher positive-scale-factor bin centered at `a = 1.4`

The reduced effective Hamiltonian is

```text
H_eff = diagonal_bias * Z - tunneling_strength * X
```

with

- `diagonal_bias = 0.18`
- `tunneling_strength = 0.24`

This produces a direct benchmark ground-state energy of `-0.3` and a ground-state vector proportional to

```text
(1 / sqrt(5)) |0> + (2 / sqrt(5)) |1>
```

for the chosen default parameter set.

## Core Observables

- `scale_factor_expectation_value`
- `volume_expectation_value`
- `effective_hamiltonian_expectation`

The scale factor is the primary cosmological observable in this experiment. The volume proxy and effective-Hamiltonian expectation are included to support benchmarked interpretation and diagnostic consistency.

## Directory Guide

- [model.md](model.md): mathematical statement and limits of interpretation
- [config.yaml](config.yaml): parameter choices, truncation, execution settings, and artifact paths
- [benchmark.py](benchmark.py): direct two-state diagonalization benchmark
- [circuit.py](circuit.py): one-qubit ground-state preparation circuit
- [observables.py](observables.py): Pauli-decomposed observable definitions
- [run_local.py](run_local.py): exact local primitives workflow
- [run_aer.py](run_aer.py): noisy local Aer workflow
- [run_ibm.py](run_ibm.py): IBM Runtime workflow, gated behind prior exact-local and noisy-local validation
- [analyze.py](analyze.py): comparison analysis and figure generation
- [results.md](results.md): written interpretation and limitations

## Exploratory Small-Scale-Factor Materials

This experiment line also preserves a conservative exploratory refinement for
small positive-scale-factor questions. These materials do not constitute a new
official experiment line and do not imply a literal Planck-Epoch simulation:

- [model_small_scale_factor.md](model_small_scale_factor.md): exploratory four-bin reduced-model statement
- [config_small_scale_factor.yaml](config_small_scale_factor.yaml): exploratory configuration and separate artifact paths
- [results_small_scale_factor.md](results_small_scale_factor.md): exploratory interpretation note
- [planck_epoch_exploratory_design.md](planck_epoch_exploratory_design.md): governance classification and conservative design analysis for Planck-context work

## Reproducible Workflow

From the repository root with the virtual environment active:

```bash
python experiments/minisuperspace_frw/benchmark.py
python experiments/minisuperspace_frw/run_local.py
python experiments/minisuperspace_frw/run_aer.py
python experiments/minisuperspace_frw/analyze.py
```

For the current Apple Silicon Aer runtime note, including the macOS arm64 Python 3.13+ guard status, see the repository [user guide](../../docs/operations/user-guide.md).

The IBM Runtime path is intentionally separate and should be used only after the exact-local and noisy-local validation outputs have been reviewed:

```bash
python experiments/minisuperspace_frw/run_ibm.py --backend-name <backend>
```

The Phase 4 hardware workflow now also writes:

- processed IBM execution JSON under `data/processed/minisuperspace_frw/`,
- raw IBM metadata capture under `data/raw/minisuperspace_frw/`,
- a hardware report under `results/reports/minisuperspace_frw/`.

For credential-free infrastructure validation of the IBM wrapper itself, use local testing mode:

```bash
python experiments/minisuperspace_frw/run_ibm.py --local-testing-backend FakeManilaV2
```

This validates the shared Runtime wrapper and provenance path, but it is not a real hardware result.
