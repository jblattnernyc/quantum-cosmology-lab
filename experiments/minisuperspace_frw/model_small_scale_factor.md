# Exploratory Small-Scale-Factor Refinement

## Status

This document describes an exploratory refinement configuration for the existing
`minisuperspace_frw` experiment line. It is not a new official experiment line,
not a new roadmap phase, and not a literal Planck-Epoch simulation.

The Planck-Epoch label serves only as cosmological context for why one might
wish to inspect a more explicitly resolved small-scale-factor sector.

## Scientific Purpose

The purpose of this refinement is to extend the retained positive-scale-factor
sector from the official two-bin baseline to a four-bin truncation that keeps
the smallest retained bins explicit while preserving exact benchmark
diagonalization and a two-qubit encoding.

## Model Statement

Let the retained basis be the four positive-scale-factor bins

```text
|a_0>, |a_1>, |a_2>, |a_3>
```

with default bin centers

```text
a = (0.15, 0.25, 0.4, 0.6).
```

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

and default parameters

```text
kappa = 0.1
mu    = 0.1
nu    = 0.001.
```

The inverse-square term is a phenomenological small-scale-factor barrier within
the reduced model. It is not a derivation of full quantum-gravitational
Planck-scale physics.

## Truncation and Encoding

The truncation keeps four positive-scale-factor bins only. The model excludes:

- negative-scale-factor sectors,
- any larger superspace discretization,
- matter degrees of freedom,
- continuum-limit claims,
- full Wheeler-DeWitt dynamics outside the retained basis.

The qubit encoding is the two-qubit binary mapping

```text
|00> -> |a_0>
|01> -> |a_1>
|10> -> |a_2>
|11> -> |a_3>.
```

## Observables

The exploratory configuration declares the following observables:

- `scale_factor_expectation_value`,
- `volume_expectation_value`,
- `effective_hamiltonian_expectation`,
- `smallest_scale_factor_probability`.

The smallest-bin probability is the primary additional diagnostic relative to
the official two-bin baseline. It measures support in the most extreme retained
positive-scale-factor bin only.

## Interpretive Limits

This refinement does not establish:

- a literal simulation of the Planck Epoch,
- a full Wheeler-DeWitt solution,
- a full theory of singularity resolution,
- full Planck-scale quantum gravity,
- inflationary, reheating, or complete early-universe dynamics.

It supports statements only about this finite-dimensional reduced
minisuperspace model and its declared observables.
