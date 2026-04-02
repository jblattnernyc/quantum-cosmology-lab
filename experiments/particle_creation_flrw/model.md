# Model Statement

## Purpose

This experiment implements a reduced particle-creation toy model for a scalar-field mode pair on a prescribed expanding FLRW-like background. Its purpose is to establish the second official Quantum Cosmology Lab research line in a form that is benchmarked, reproducible, and explicit about the difference between a reduced curved-spacetime model and a literal cosmological-era simulation.

## Interpretive Scope

The experiment does not solve a full continuum quantum field in curved spacetime, does not evolve a field over many momentum modes, and does not claim to simulate inflation itself. Instead, it isolates one retained momentum pair and studies a discrete sequence of pair-production updates tied to a prescribed expanding background.

The implementation therefore supports statements about this reduced two-mode, single-pair-truncation model only.

## Background Prescription

The background is a prescribed spatially flat FLRW-like scale factor sampled on a discrete conformal-time grid:

```text
eta_j = j * Delta eta,   j = 0, ..., N

a(eta_j) = a_initial + (a_final - a_initial) * j / N
```

The default configuration uses:

```text
a_initial = 1.0
a_final   = 2.4
N         = 6
time_extent = 1.5
Delta eta = time_extent / N = 0.25
```

All quantities are dimensionless internal units chosen for a small benchmarkable toy model.

## Retained Mode and Frequency

One comoving scalar-field mode pair `(k, -k)` is retained. The effective frequency at the discrete grid edges is taken to be

```text
omega_j = sqrt(k^2 + m^2 a(eta_j)^2)
```

with default parameters

```text
k = 0.5
m = 0.6
```

This frequency choice corresponds to a deliberately simplified massive-mode prescription on a prescribed background. The experiment does not attempt to include the full range of curvature-coupling, renormalization, vacuum-choice, or continuum mode-summation issues present in the full theory.

## Truncation

Each of the two retained modes is truncated to occupation numbers `{0, 1}`:

```text
|0> -> zero retained occupation
|1> -> one retained occupation
```

The full two-qubit basis is therefore:

```text
|00>, |01>, |10>, |11>
```

The dynamics start from `|00>` and use only pair-creation and pair-annihilation operators, so the model remains in the even-parity subspace:

```text
|00>, |11>
```

This is a strong truncation. States with two or more pairs, additional momentum modes, and backreaction on the background are excluded by construction.

## Discrete Evolution Rule

For each time slice `j`, define:

```text
omega_mid,j = (omega_j + omega_{j+1}) / 2
theta_j     = (1 / 2) log(omega_{j+1} / omega_j)
phi_j       = omega_mid,j * Delta eta
```

The experiment uses the ordered slice unitary

```text
U_j = exp[-i phi_j (N_k + N_-k - I)]
      exp[-i theta_j (a_k^dagger a_-k^dagger + a_k a_-k)]
```

and the full discrete evolution is

```text
U = U_{N-1} ... U_1 U_0 .
```

This is the model actually benchmarked in code. The repository does not claim that this discrete ordered product is a continuum-exact FLRW solution. It is an explicit, finite-dimensional, Bogoliubov-inspired toy evolution chosen because it is small enough to benchmark exactly and evaluate with estimator primitives.

## Qubit Encoding

The qubit mapping used in the code is:

- qiskit qubit `0` encodes mode `k`,
- qiskit qubit `1` encodes mode `-k`.

In Pauli form:

```text
N_k   = (I - I Z) / 2
N_-k  = (I - Z I) / 2
N_tot = I I - (I Z + Z I) / 2
P_11  = (I I - I Z - Z I + Z Z) / 4

a_k^dagger a_-k^dagger + a_k a_-k = (X X - Y Y) / 2
```

The circuit implementation uses `RZ`, `RXX`, and `RYY` gates so that the benchmarked discrete model is represented directly at the gate level.

## Observables

### Single-Mode Particle Number

```text
n_k = <N_k>
```

This reports the occupation of one retained mode. In the present symmetric truncation, it also equals the retained pair-occupation probability.

### Total Particle Number

```text
n_tot = <N_k + N_-k>
```

This is the principal particle-creation observable for the reduced model.

### Pairing Correlator

```text
C_pair = <a_k^dagger a_-k^dagger + a_k a_-k>
       = <(X X - Y Y) / 2>
```

This is a squeezing-related anomalous correlator for the retained mode pair. Within this toy truncation it serves as a diagnostic of pair coherence, not as a full continuum squeezing parameter.

## Default Benchmark Values

For the default repository parameter set, the exact benchmark of the declared discrete model gives:

- `single_mode_particle_number_expectation = 0.03422860544437149`
- `total_particle_number_expectation = 0.06845721088874299`
- `pairing_correlator_expectation = -0.3465452307022458`
- `pair_occupation_probability = 0.03422860544437149`
- `even_parity_probability = 1.0`

The final benchmark state in the retained even-parity sector is:

```text
|psi_final> = c_00 |00> + c_11 |11>
```

with complex amplitudes fixed numerically by the benchmark code and serialized in the benchmark artifact.

## Why This Counts as a Curved-Spacetime Particle-Creation Experiment

The experiment qualifies as a reduced QFT-in-curved-spacetime study because:

- it begins from a prescribed expanding FLRW-like background rather than from an arbitrary circuit label,
- it models a retained field-mode pair rather than a minisuperspace scale factor,
- it encodes time-dependent mode evolution explicitly through slice-dependent frequencies and pairing angles,
- it measures particle-number and pair-correlation observables tied to the retained field operators,
- it benchmarks all reported values against an exact discrete-model calculation.

It does not justify claims about a full inflationary particle spectrum, continuum reheating dynamics, or complete quantum field theory on cosmological spacetimes.

## Foundational References

- [L. Parker, “Particle Creation in Expanding Universes,” *Physical Review Letters* 21 (1968): 562-564.](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.21.562)
- [L. Parker, “Quantized Fields and Particle Creation in Expanding Universes. I,” *Physical Review* 183 (1969): 1057-1068.](https://journals.aps.org/pr/abstract/10.1103/PhysRev.183.1057)
- N. D. Birrell and P. C. W. Davies, *Quantum Fields in Curved Space* (Cambridge University Press, 1982).

These references motivate the broader particle-creation setting. The present implementation is a deliberately reduced discrete toy model for repository benchmarking and workflow development rather than a direct reproduction of any one published continuum calculation.
