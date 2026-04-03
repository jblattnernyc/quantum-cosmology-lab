# Exploratory Design Note: Planck-Epoch Context

## Status

This note records the repository's current design judgment for work motivated by
the cosmological context of the Planck Epoch.

Under the active Version 1.1 governance posture, this request is classified as
**exploratory design**, not as a new official experiment, not as a new roadmap
phase, and not as evidence that a literal Planck-Epoch simulation claim is
scientifically justified.

Direct official implementation as a new experiment line is therefore **not
authorized by the epoch label alone**. The label is contextual motivation only.

## Governance Classification

The present repository already contains:

- an official Track A minisuperspace experiment in `minisuperspace_frw/`,
- an official Track B particle-creation experiment in
  `particle_creation_flrw/`,
- an official Track C toy-gauge experiment in `gut_toy_gauge/`,
- shared exact-local, noisy-local, and IBM Runtime infrastructure under
  `src/qclab/`.

Within that implemented landscape, a broad "Planck Epoch" request does not by
itself fix:

- a unique Hamiltonian or constraint operator,
- a unique truncation,
- a unique observable set,
- or a unique physical interpretation policy.

The request is therefore treated conservatively as exploratory model design
within the existing minisuperspace program rather than as a new official
experiment admission.

## Repository-Fit Analysis

The strongest mission-fit path is a Track A reduced minisuperspace refinement.
This remains within the repository's established scope because it stays inside
reduced quantum cosmology proper, reuses the current benchmark-first workflow,
and does not require a new research track, a new execution tier, or a new
governance structure.

At the same time, the request is too underdetermined for immediate official
admission. The phrase "Planck Epoch" is much broader than any single
benchmarkable reduced model now warranted by repository policy. A direct
official implementation would risk analogy inflation unless the model,
observables, and interpretive limits were fixed much more narrowly.

## Preferred Reduced-Model Candidate

The preferred exploratory candidate is the existing four-bin
small-scale-factor refinement already documented in:

- `model_small_scale_factor.md`
- `config_small_scale_factor.yaml`
- `results_small_scale_factor.md`

Its reduced operator is

```text
H_eff =
  -kappa * sum_j ( |a_j><a_{j+1}| + |a_{j+1}><a_j| )
  + sum_j U(a_j) |a_j><a_j|
```

with

```text
U(a) = mu * a^2 + nu / a^2
```

on the retained positive-scale-factor bins

```text
a = (0.15, 0.25, 0.4, 0.6).
```

The two-qubit encoding is

```text
|00> -> |a_0>
|01> -> |a_1>
|10> -> |a_2>
|11> -> |a_3>.
```

This candidate is the most appropriate current reduced proxy for
Planck-Epoch-motivated questions because it:

- remains inside the existing minisuperspace family,
- makes the small positive-scale-factor sector more explicit,
- stays exactly diagonalizable,
- stays directly encodable on two qubits,
- reuses the current shared estimator and analysis infrastructure,
- and already declares its status as exploratory rather than official.

## Candidate Model Options

1. **Preferred current option: four-bin small-scale-factor barrier
   refinement.**
   This is the least disruptive and most benchmarkable path. It is the correct
   immediate vehicle for Planck-context exploratory work in the current
   repository.

2. **Possible later refinement: larger finite-difference Wheeler-DeWitt-style
   truncation.**
   A four-bin or eight-bin discretized constraint-style operator could remain
   mission-fit if its benchmark, encoding, and circuit synthesis stay explicit
   and tractable. This would still need a sharply defined observable set and
   interpretive guardrails before official admission.

3. **Possible later expansion in complexity: two-variable minisuperspace with a
   homogeneous scalar clock.**
   This is scientifically interesting, but it is not the conservative first
   choice for a Planck-context request. Depending on how broadly it is framed,
   it may rise to the level of a materially new experiment family and therefore
   require additional governance review before official adoption.

## Candidate Observables

For the preferred exploratory candidate, the observables should remain:

- `scale_factor_expectation_value`
- `volume_expectation_value`
- `effective_hamiltonian_expectation`
- `smallest_scale_factor_probability`

These quantities are appropriate because they are explicit observables of the
declared finite-dimensional model. The smallest-bin probability is especially
useful as a conservative proxy for support near the smallest retained positive
scale-factor region. It is not, by itself, a singularity-resolution claim.

## Benchmark and Validation Strategy

The benchmark and validation strategy should remain exactly aligned with
repository policy:

1. Direct diagonalization of the retained Hamiltonian as the exact benchmark.
2. Exact local estimator evaluation of the declared observables using an exact
   state-preparation circuit.
3. Noisy local Aer evaluation with an explicit noise model and preserved
   provenance.
4. IBM Runtime only if the first three layers remain scientifically
   interpretable and if hardware execution answers a concrete operational
   question rather than serving as primary physical evidence.

No hardware-first workflow is justified for this context.

## Relation to Existing Official Lines

This exploratory path is a refinement candidate within the existing
`minisuperspace_frw` line. It does not alter the scientific role of:

- `particle_creation_flrw`, which remains a Track B curved-spacetime
  particle-creation line,
- `gut_toy_gauge`, which remains a Track C toy-gauge line,
- or the current official experiment registry, which still contains three
  official lines only.

## Relation to IBM Provenance and Archival Policy

If this exploratory configuration is ever executed through IBM Runtime, its
artifacts should remain separate from the canonical official minisuperspace
artifacts. The already-declared exploratory artifact paths under
`minisuperspace_frw_small_scale_factor/` are consistent with that policy.

Any IBM output from such exploratory work would still be subordinate to the
benchmark, exact-local, and noisy-local tiers, and it would need to preserve
the same metadata-capture, reporting, and archival discipline used elsewhere in
the repository.

## Implementation Risks

- The inverse-square barrier is phenomenological within the reduced model and
  should not be mistaken for a derivation from full quantum gravity.
- Results are sensitive to the chosen retained bins and cutoff.
- Multi-qubit state preparation for larger truncations can increase circuit
  depth rapidly and may reduce the value of the hardware tier.
- Small-scale-factor probability can be rhetorically overread if it is not kept
  tied to the finite-dimensional truncation.

## Interpretive Limits

Even if the preferred exploratory candidate is executed successfully, it does
not establish:

- a literal simulation of the Planck Epoch,
- a full Wheeler-DeWitt solution,
- a full theory of singularity resolution,
- realistic Planck-scale quantum gravity,
- inflationary or reheating dynamics,
- or a claim about nature beyond the retained reduced model.

The work must remain labeled as a **toy model**, **reduced model**, or
**exploratory refinement** unless a much stronger derivation and validation
program is supplied.

## PLANS.md Amendment Trigger

No `PLANS.md` amendment is required for this exploratory design note itself.
No new roadmap phase is created or implied.

A future `PLANS.md` amendment would become necessary only if proposed follow-on
work were to:

- create a new primary research track,
- widen the repository's scope beyond the existing Track A to Track C program,
- add a new repository-wide execution or validation tier,
- or materially change IBM provenance, archival, or governance policy.

If such a major expansion were ever proposed, the amendment should include:

1. a precise objective,
2. candidate reduced models and observables,
3. benchmark and validation strategy,
4. scope boundaries,
5. relation to the existing official experiments,
6. relation to IBM hardware provenance and archival policy,
7. implementation risks,
8. and explicit interpretive limits.
