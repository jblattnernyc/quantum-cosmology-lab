# Model Statement

## Purpose

This experiment implements a Grand-Unification-Epoch-context reduced `Z2`
symmetry-breaking toy model in a two-site truncation. Its purpose is to study a
small, exactly benchmarkable order-parameter system relevant to the repository's
Track C early-universe toy-model scope while preserving explicit observables,
benchmark-before-hardware discipline, and conservative interpretation.

## Interpretive Scope

The Grand-Unification-Epoch label is contextual only. The experiment does not
simulate the literal Grand Unification Epoch, does not implement a realistic
grand unified gauge theory, and does not model a specific high-energy
unification group such as `SU(5)` or `SO(10)`. It also excludes thermal
field-theory dynamics, running couplings, monopole production, baryogenesis,
and cosmological expansion.

The implementation supports statements about this finite two-site `Z2` toy
Hamiltonian only.

## Truncation

The retained system has two binary order-parameter sites. The computational
basis is:

```text
|00>, |01>, |10>, |11>.
```

The local `Z2` values are dimensionless internal variables. The aligned states
`|00>` and `|11>` are ordered configurations, while `|01>` and `|10>` are
anti-aligned configurations. In this toy model, anti-alignment is used as a
finite two-site domain-wall proxy.

The model excludes:

- realistic grand unified gauge groups,
- non-Abelian gauge dynamics,
- Higgs representation theory,
- matter multiplets,
- finite-temperature effective potentials,
- continuum or thermodynamic limits,
- cosmological expansion and backreaction.

## Effective Hamiltonian

The reduced Hamiltonian is:

```text
H = -J ZZ - h (IX + XI) / 2 - b (IZ + ZI) / 2.
```

The default configuration uses:

```text
J = 0.7
h = 0.32
b = 0.08
```

The terms have the following model-specific meanings:

- `-J ZZ` favors aligned order-parameter configurations,
- `-h (IX + XI) / 2` mixes the retained `Z2` configurations,
- `-b (IZ + ZI) / 2` introduces a small explicit bias so that the finite
  two-site ground state has a definite order-parameter orientation.

For the default configuration, the benchmark ground-state energy is:

```text
E_0 = -0.8204719227933479.
```

The default benchmark ground-state vector in the retained basis is:

```text
|psi_0> =
  0.9654972183497672 |00>
  + 0.12211102774451228 |01>
  + 0.12211102774451224 |10>
  + 0.1949177138312983 |11>.
```

## Qubit Encoding

The experiment uses two qubits:

```text
q0 -> first retained Z2 order-parameter site
q1 -> second retained Z2 order-parameter site.
```

The circuit prepares the exact benchmark ground state through Qiskit's
finite-dimensional state-preparation machinery. Observable evaluation is then
performed through explicit Pauli-decomposed estimator observables.

## Observables

### Order-Parameter Expectation

```text
O_order = (IZ + ZI) / 2.
```

This is the primary reduced symmetry diagnostic. It measures the average
retained `Z2` orientation in the two-site truncation.

### Domain-Wall Density

```text
O_wall = (II - ZZ) / 2.
```

This observable projects onto the anti-aligned sector. It is a two-site
domain-wall proxy, not a continuum defect density.

### Transverse-Coherence Expectation

```text
O_coh = (IX + XI) / 2.
```

This observable measures coherence under the transverse mixing operator in the
declared finite model.

### Effective-Hamiltonian Expectation

```text
O_H = H.
```

The Hamiltonian expectation is included as a benchmark consistency diagnostic.

## Benchmark Values

For the default benchmark ground state, the exact values are:

- `order_parameter_expectation = 0.8941919634759182`
- `domain_wall_density = 0.029822206193642085`
- `transverse_coherence_expectation = 0.28339891995741684`
- `effective_hamiltonian_expectation = -0.8204719227933478`

## Why This Counts as a Track C Toy Experiment

The experiment qualifies as a reduced early-universe field-theory toy model
because:

- it begins from an explicit finite Hamiltonian rather than from an epoch label,
- it declares a finite truncation and direct qubit mapping,
- it defines an order parameter, domain-wall proxy, coherence diagnostic, and
  Hamiltonian expectation as explicit observables,
- it benchmarks all reported quantities by exact direct diagonalization,
- and it keeps the Grand-Unification-Epoch label as context rather than as a
  literal simulation claim.

It does not justify claims about realistic grand-unified symmetry breaking,
realistic non-Abelian gauge dynamics, monopole physics, baryogenesis, or a
direct simulation of the Grand Unification Epoch.

## Foundational References

- L. D. Landau, “On the Theory of Phase Transitions. I,” *Physikalische
  Zeitschrift der Sowjetunion* 11 (1937): 26-35.
- S. R. Coleman and E. Weinberg, “Radiative Corrections as the Origin of
  Spontaneous Symmetry Breaking,” *Physical Review D* 7 (1973): 1888-1910.
- J. B. Kogut, “An Introduction to Lattice Gauge Theory and Spin Systems,”
  *Reviews of Modern Physics* 51 (1979): 659-713.

These references motivate the broader symmetry-breaking and lattice-model
context. The present implementation is a reduced benchmark toy model for the
repository's official experiment program rather than a reproduction of a
specific published grand-unified theory.

