# Model Statement

## Purpose

This experiment implements a scientifically modest reduced FRW minisuperspace toy model in a two-state truncation. Its purpose is to establish the first official Quantum Cosmology Lab experiment in a form that is benchmarked, reproducible, and explicit about its interpretive limits.

## Interpretive Scope

This is not a full quantization of the FRW universe and not a direct numerical solution of the Wheeler-DeWitt equation across a large discretized superspace. Instead, it is a projected two-state model intended to represent a minimal positive-scale-factor sector with explicit operator mapping and exact benchmark values.

The experiment therefore supports statements about this reduced projected model only.

## Truncation

The positive-scale-factor sector is truncated to two representative bins:

```text
|0>  -> lower scale-factor bin centered at a = 0.6
|1>  -> higher scale-factor bin centered at a = 1.4
```

The basis is dimensionless. The values `0.6` and `1.4` should be interpreted as internal scale-factor units chosen for this toy model, not as directly measured cosmological values.

## Effective Hamiltonian

After projection to the two-state basis, the model uses the effective Hamiltonian

```text
H_eff = epsilon * Z - Delta * X
```

with default parameters

```text
epsilon = 0.18
Delta   = 0.24
```

In matrix form,

```text
H_eff = [[ 0.18, -0.24],
         [-0.24, -0.18]]
```

The direct benchmark eigenvalues are

```text
E_0 = -0.3
E_1 =  0.3
```

and the benchmark ground state is

```text
|psi_0> = (1 / sqrt(5)) |0> + (2 / sqrt(5)) |1>
```

up to a global phase.

## Qubit Encoding

The experiment uses one qubit:

- computational basis state `|0>` encodes the lower scale-factor bin,
- computational basis state `|1>` encodes the higher scale-factor bin.

Because the benchmark ground state is real and two-dimensional, it can be prepared exactly with a single `RY` rotation.

## Observables

### Scale-Factor Operator

The truncated scale-factor operator is

```text
a_hat = diag(0.6, 1.4) = 1.0 * I - 0.4 * Z
```

This is the primary cosmological observable in the experiment.

### Volume Proxy

The volume proxy is taken to be `a^3` in the same truncation:

```text
V_hat = diag(0.6^3, 1.4^3) = 1.48 * I - 1.264 * Z
```

This is a derived geometric proxy, not a full quantization of the FRW volume operator in a richer basis.

### Effective Hamiltonian Expectation

The projected effective Hamiltonian itself is also measured:

```text
H_eff = 0.18 * Z - 0.24 * X
```

This observable is used as a diagnostic benchmark consistency check.

## Benchmark Values

For the benchmark ground state, the exact values are:

- `scale_factor_expectation_value = 1.24`
- `volume_expectation_value = 2.2384`
- `effective_hamiltonian_expectation = -0.3`
- `large_scale_factor_probability = 0.8`

## Why This Counts as a Reduced FRW Minisuperspace Experiment

The experiment qualifies as a minisuperspace toy study because:

- it reduces the cosmological degree of freedom to a scale-factor sector,
- it encodes that reduced sector explicitly into a qubit basis,
- it defines physically motivated observables in that truncated basis,
- it benchmarks all reported values against exact numerics.

It does not justify any claim that the repository has simulated the full early universe, the full Wheeler-DeWitt equation, or Planck-scale quantum gravity.

## Foundational References

- B. S. DeWitt, “Quantum Theory of Gravity. I. The Canonical Theory,” *Physical Review* 160 (1967): 1113-1148.
- J. B. Hartle and S. W. Hawking, “Wave Function of the Universe,” *Physical Review D* 28 (1983): 2960-2975.

These references motivate the broader minisuperspace and quantum-cosmology setting. The present implementation is a new reduced toy projection for repository development and benchmarking purposes rather than a direct reproduction of a single published model.
