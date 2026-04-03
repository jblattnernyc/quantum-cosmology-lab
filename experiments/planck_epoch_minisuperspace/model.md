# Model Statement

## Purpose

This experiment implements a Planck-Epoch-motivated reduced minisuperspace toy
model in a four-bin positive-scale-factor truncation. Its purpose is to study a
more explicitly resolved small-scale-factor sector within the repository's
existing Track A quantum-cosmology program while preserving exact benchmarking,
explicit observables, and conservative interpretation.

## Interpretive Scope

The Planck-Epoch label is contextual only. The experiment does not simulate the
literal Planck Epoch, does not solve full Wheeler-DeWitt dynamics on a large
superspace lattice, and does not claim a full quantum-gravity description of
the early universe. Instead, it isolates a finite-dimensional reduced operator
that is small enough to benchmark exactly and to encode directly on two qubits.

The implementation therefore supports statements about this reduced four-bin
minisuperspace model only.

## Truncation

The retained positive-scale-factor sector is truncated to four representative
bins:

```text
|a_0> -> a = 0.15
|a_1> -> a = 0.25
|a_2> -> a = 0.4
|a_3> -> a = 0.6
```

All values are dimensionless internal scale-factor units. They are chosen to
resolve a smaller retained positive-scale-factor region than the baseline
two-bin minisuperspace experiment while remaining finite and exactly
diagonalizable.

The model excludes:

- negative-scale-factor sectors,
- matter degrees of freedom,
- larger superspace discretizations,
- continuum-limit claims,
- and any direct physical claim about Planck-scale quantum gravity in nature.

## Effective Hamiltonian

The reduced operator is

```text
H_eff =
  -kappa * sum_j ( |a_j><a_{j+1}| + |a_{j+1}><a_j| )
  + sum_j U(a_j) |a_j><a_j|
```

with

```text
U(a) = mu * a^2 + nu / a^2
```

and default parameters

```text
kappa = 0.1
mu    = 0.1
nu    = 0.001
```

The nearest-neighbor term provides explicit mixing among retained bins. The
quadratic term provides a smooth large-scale growth in the retained diagonal
potential. The inverse-square term is used here as a phenomenological
small-scale-factor barrier. It is not derived as a complete Planck-scale
quantum-gravitational effective theory.

For the default configuration, the benchmark ground-state energy is

```text
E_0 = -0.13427869803736275.
```

## Qubit Encoding

The experiment uses a two-qubit binary encoding:

```text
|00> -> |a_0>
|01> -> |a_1>
|10> -> |a_2>
|11> -> |a_3>
```

Because the benchmark ground state is real in the retained basis, the circuit
prepares it directly through Qiskit's finite-dimensional state-preparation
machinery and then evaluates explicit Pauli-decomposed observables with
estimator primitives.

## Observables

### Scale-Factor Operator

The truncated scale-factor operator is

```text
a_hat = diag(0.15, 0.25, 0.4, 0.6).
```

This is the primary cosmological observable in the experiment.

### Volume Proxy

The truncated volume proxy is

```text
V_hat = diag(0.15^3, 0.25^3, 0.4^3, 0.6^3).
```

This is a retained `a^3` proxy in the declared truncation, not a full
minisuperspace volume operator in a richer basis.

### Effective Hamiltonian Expectation

The experiment also measures the expectation value of the projected
Hamiltonian itself as a benchmark-consistency diagnostic.

### Smallest-Bin Projector

The additional small-scale-factor diagnostic is

```text
P_small = |a_0><a_0|.
```

This observable reports support on the smallest retained positive-scale-factor
bin only. It is a finite-dimensional support diagnostic, not a direct
singularity-resolution criterion.

## Benchmark Values

For the default benchmark ground state, the exact values are:

- `scale_factor_expectation_value = 0.3409579452907098`
- `volume_expectation_value = 0.058451698470842514`
- `effective_hamiltonian_expectation = -0.13427869803736275`
- `smallest_scale_factor_probability = 0.11421160961397295`
- `largest_scale_factor_probability = 0.12809746928767865`

## Why This Counts as a Reduced Minisuperspace Experiment

The experiment qualifies as an official Track A reduced quantum-cosmology line
because:

- it begins from an explicit reduced operator rather than from thematic labeling,
- it declares a finite retained basis and a direct qubit mapping,
- it measures explicit operators with stated physical meaning,
- it benchmarks all reported values against exact direct diagonalization,
- and it preserves exact-local, noisy-local, and optional IBM Runtime tiers
  under the repository's benchmark-before-hardware discipline.

It does not justify claims about the literal Planck Epoch, complete
quantum-cosmology wave functions, or full Planck-scale quantum gravity.

## Foundational References

- B. S. DeWitt, “Quantum Theory of Gravity. I. The Canonical Theory,”
  *Physical Review* 160 (1967): 1113-1148.
- J. B. Hartle and S. W. Hawking, “Wave Function of the Universe,”
  *Physical Review D* 28 (1983): 2960-2975.

These references motivate the broader minisuperspace setting. The present
implementation is a new reduced toy projection for the repository's official
experiment program rather than a direct numerical reproduction of a single
published Wheeler-DeWitt model.
