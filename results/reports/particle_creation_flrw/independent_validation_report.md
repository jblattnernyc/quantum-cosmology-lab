# Particle-Creation FLRW Independent Validation Report

Overall result: **PASS**

## Independent discrete reproduction

The declared two-qubit model was reconstructed with explicit 4 x 4 matrices and SciPy matrix exponentials. No experiment evolution, circuit-construction, or observable-construction helper was used.

- Official-state infidelity: 2.220446e-16
- Phase-aligned maximum amplitude error: 1.110231e-16
- Maximum observable absolute error: 5.551115e-17
- Odd-parity probability: 0.000000e+00

## Refinement study

The refinement study compares the symmetric discrete product with an ODE obtained by linearly interpolating the prescribed scale factor. This is an added discretization diagnostic; it is not a claim of a continuum-exact quantum field calculation.

- Final maximum observable error: 2.490678e-05
- Final state infidelity: 1.917668e-10
- Final observed convergence order: 2.000109

## Factor-ordering comparison

At the official `N = 6`, the symmetric product reduces the maximum observable error by a factor of `4.276668` relative to the superseded phase-then-pairing product under the same ODE diagnostic.

## Interpretation

Passing independent reproduction corroborates the implementation of the declared finite-dimensional discrete model. It does not validate the single-pair truncation as a complete curved-spacetime field theory.
The refinement sequence quantifies sensitivity to the number of time slices and should be considered separately from backend noise.

Experiment: `particle_creation_flrw`
JSON evidence: `data/processed/particle_creation_flrw/independent_validation.json`
Convergence table: `results/tables/particle_creation_flrw/convergence_summary.md`
