# Early-Universe Toy Gauge Model

## Status

This directory now contains the third official Quantum Cosmology Lab experiment line: a reduced two-link `Z2` gauge toy model implemented as a benchmarked, explicitly gauge-labeled Track C study.

The implementation is intentionally modest. It is not a realistic grand-unified-theory simulation, not a full lattice gauge theory calculation, and not a literal model of a specific early-universe epoch. It is a benchmarked two-link toy model designed to study gauge-sector consistency, a reduced order parameter, and a Wilson-line-like correlator proxy in the smallest hardware-relevant setting.

## Scientific Question

For a reduced two-link `Z2` gauge toy Hamiltonian with an explicit gauge-penalty term, what are the benchmark ground-state values of gauge-invariance violation, a link-alignment order parameter, and a Wilson-line correlator proxy, and how accurately do exact local and noisy local estimator workflows reproduce them?

## Model Summary

The experiment keeps two retained link qubits:

- qubit `0`: first retained `Z2` link
- qubit `1`: second retained `Z2` link

The gauge-invariant subspace is the even-parity sector:

- `|00>`: aligned positive link orientation
- `|11>`: aligned negative link orientation

The odd-parity states `|01>` and `|10>` are treated as gauge-violating configurations and are penalized energetically.

The reduced Hamiltonian is

```text
H = electric_field_bias * (IZ + ZI) / 2
    - pair_flip_coupling * XX
    + gauge_penalty * (II - ZZ) / 2
```

with default values:

- `electric_field_bias = 0.18`
- `pair_flip_coupling = 0.24`
- `gauge_penalty = 1.2`

For the default parameter set, the direct benchmark gives:

- ground-state energy: `-0.3`
- gauge-invariance violation expectation: `0.0`
- link-alignment order parameter: `-0.6`
- Wilson-line correlator proxy: `0.8`

## Core Observables

- `gauge_invariance_violation_expectation`
- `link_alignment_order_parameter`
- `wilson_line_correlator_proxy`

The gauge-violation observable is the primary consistency diagnostic. The link-alignment observable serves as a reduced order parameter, and the Wilson-line proxy measures coherent mixing inside the retained gauge-invariant sector.

## Directory Guide

- `model.md`: mathematical statement, truncation, operator mapping, and interpretive limits
- `config.yaml`: parameter choices, execution settings, and artifact paths
- `common.py`: typed experiment configuration and reduced-operator helpers
- `benchmark.py`: exact direct diagonalization benchmark
- `circuit.py`: two-qubit gauge-invariant ground-state preparation circuit
- `observables.py`: Pauli-decomposed gauge, order-parameter, and Wilson-proxy observables
- `run_local.py`: exact local estimator workflow
- `run_aer.py`: noisy local Aer estimator workflow
- `run_ibm.py`: optional IBM Runtime workflow
- `analyze.py`: comparison analysis and figure generation
- `results.md`: written interpretation and limitations

## Reproducible Workflow

From the repository root with the virtual environment active:

```bash
python experiments/gut_toy_gauge/benchmark.py
python experiments/gut_toy_gauge/run_local.py
python experiments/gut_toy_gauge/run_aer.py
python experiments/gut_toy_gauge/analyze.py
```

For the current Apple Silicon Aer runtime note, including the macOS arm64 Python 3.13+ guard status, see the repository [user guide](../../docs/operations/user-guide.md).

The IBM Runtime path is intentionally separate and should be used only after the exact-local and noisy-local validation outputs have been reviewed:

```bash
python experiments/gut_toy_gauge/run_ibm.py --backend-name <backend>
```

The shared hardware workflow also supports credential-free IBM Runtime local testing mode:

```bash
python experiments/gut_toy_gauge/run_ibm.py --local-testing-backend FakeManilaV2
```

This validates the shared Runtime wrapper and provenance path, but it is not a real hardware result.
