# Model Statement

## Purpose

This experiment implements a reduced two-link `Z2` gauge toy model intended to establish the third official Quantum Cosmology Lab research line under Track C of `PLANS.md`. Its purpose is to provide a benchmarked and reproducible early-universe field-theory toy study that remains explicit about the difference between a reduced gauge toy model and a literal realistic GUT simulation.

## Interpretive Scope

The experiment does not implement a realistic grand unified gauge group, does not model full non-Abelian lattice dynamics, does not include a continuum limit, and does not claim to simulate a specific early-universe epoch in literal field-theory detail. Instead, it isolates the smallest two-link `Z2` gauge-like system that still supports:

- an explicit gauge-consistency diagnostic,
- a reduced order parameter,
- a Wilson-line-like correlator proxy,
- exact benchmark diagonalization,
- explicit exact-local, noisy-local, and optional IBM Runtime workflows.

The implementation therefore supports statements about this reduced two-link toy model only.

## Reduced Link System

The experiment retains two binary link variables encoded directly into two qubits:

```text
q0 -> first retained Z2 link
q1 -> second retained Z2 link
```

The computational basis is:

```text
|00>, |01>, |10>, |11>
```

The even-parity states `|00>` and `|11>` are treated as the retained gauge-invariant sector. The odd-parity states `|01>` and `|10>` are treated as gauge-violating configurations for the purpose of this reduced model.

## Truncation

This is an explicit and severe truncation. The model keeps:

- two links only,
- binary link variables only,
- no spatial lattice larger than the retained two-link cell,
- no dynamical matter fields,
- no continuum extrapolation,
- no realistic non-Abelian gauge structure.

The retained gauge-invariant sector is:

```text
|00>, |11>
```

This two-state sector is the smallest setting in which a gauge-consistency diagnostic and a nontrivial gauge-invariant mixing term can both be defined and benchmarked.

## Hamiltonian

The model Hamiltonian is

```text
H = epsilon * (IZ + ZI) / 2
    - kappa * XX
    + lambda * (II - ZZ) / 2
```

with default parameters

```text
epsilon = 0.18
kappa   = 0.24
lambda  = 1.2
```

The terms are interpreted as follows:

- `(IZ + ZI) / 2`: reduced electric-flux alignment term,
- `XX`: gauge-invariant two-link flip term used here as a Wilson-line-like mixing operator,
- `(II - ZZ) / 2`: projector onto the odd-parity sector, included as an explicit gauge-penalty term.

Within the retained gauge-invariant sector `|00>, |11>`, the Hamiltonian reduces to the two-state form

```text
H_phys = epsilon * Z - kappa * X
```

while the odd-parity sector is shifted upward by the gauge penalty `lambda`.

For the default parameter set, the exact spectrum is:

```text
(-0.3, 0.3, 0.96, 1.44)
```

so the benchmark ground state lies in the gauge-invariant sector.

## Qubit Encoding and Ground-State Circuit

Because the benchmark ground state has support only on `|00>` and `|11>`, it can be prepared exactly with:

1. a single `RY(theta)` rotation on qubit `0`,
2. a `CX(0, 1)` gate.

For the default parameter set,

```text
theta = 2 arctan(2) ≈ 2.214297435588181
```

which prepares the benchmark ground state

```text
|psi_0> = (1 / sqrt(5)) |00> + (2 / sqrt(5)) |11>
```

up to a global phase.

## Observables

### Gauge-Invariance Violation

```text
O_gauge = (II - ZZ) / 2
```

This observable is zero on the retained gauge-invariant sector and one on the odd-parity sector. It measures leakage away from the reduced physical subspace.

### Link-Alignment Order Parameter

```text
O_order = (IZ + ZI) / 2
```

This observable measures the average retained `Z2` link orientation. Within this reduced model it serves as a small order-parameter proxy rather than as a full continuum symmetry-breaking diagnostic.

### Wilson-Line Correlator Proxy

```text
O_W = XX
```

This observable flips both retained links simultaneously and measures coherence between `|00>` and `|11>`. In the present experiment it is used only as a Wilson-line-like correlator proxy for the reduced two-link system.

## Default Benchmark Values

For the default configuration, the exact benchmark yields:

- `gauge_invariance_violation_expectation = 0.0`
- `link_alignment_order_parameter = -0.6`
- `wilson_line_correlator_proxy = 0.8`
- `physical_sector_probability = 1.0`

These values are properties of the reduced two-link toy model and its chosen parameter set only.

## Why This Counts as a Track C Toy-Gauge Experiment

The experiment qualifies as an early-universe field-theory toy model because:

- it is an explicitly declared reduced lattice-gauge-style model,
- it includes a gauge-violation diagnostic rather than inferring meaning from raw bitstrings,
- it includes a reduced order parameter and a Wilson-line-like correlator proxy,
- it is benchmarked exactly before any noisy or hardware execution tier,
- it keeps its claims at the level of a reduced `Z2` gauge toy rather than a literal realistic GUT simulation.

It does not justify claims about realistic grand-unified symmetry breaking, realistic non-Abelian confinement, or a direct simulation of the GUT epoch.

## Foundational References

- J. B. Kogut, “An Introduction to Lattice Gauge Theory and Spin Systems,” *Reviews of Modern Physics* 51 (1979): 659-713.
- E. Zohar, J. I. Cirac, and B. Reznik, “Quantum Simulations of Lattice Gauge Theories Using Ultracold Atoms in Optical Lattices,” *Reports on Progress in Physics* 79 (2016): 014401.

These references motivate the broader lattice-gauge context. The present implementation is a new reduced two-link toy model for repository benchmarking and workflow development rather than a direct reproduction of a specific published Hamiltonian.
