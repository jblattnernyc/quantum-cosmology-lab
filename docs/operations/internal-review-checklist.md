# Internal Review Checklist

## Purpose

This checklist defines the minimum repository-level review items for internal reports, milestone materials, and release-candidate dissemination packages after Phase 6.

## Scientific Scope

- [ ] The document identifies the experiment line or repository scope explicitly.
- [ ] The work is labeled correctly as quantum cosmology, curved-spacetime field theory, toy gauge study, governance material, or repository operations.
- [ ] No language inflates a toy model into a literal Planck-era, inflationary, GUT, electroweak, or QCD-era simulation without explicit model support.

## Model and Observable Integrity

- [ ] The scientific question is stated explicitly.
- [ ] The relevant `model.md` is cited or referenced directly.
- [ ] Observables are named explicitly rather than inferred from raw bitstrings.
- [ ] Truncations, discretizations, and approximation limits remain visible in the document.

## Benchmark and Execution Tiers

- [ ] Benchmark artifacts are present and identifiable.
- [ ] Exact-local validation artifacts are present and identifiable.
- [ ] Noisy-local validation artifacts are present and identifiable when required by the official experiment standard.
- [ ] IBM hardware discussion, if present, is subordinate to the benchmarked tiers.

## IBM Provenance

- [ ] Live IBM results are cited through canonical artifacts, archived artifacts, and the `ibm_runtime_runs.jsonl` manifest.
- [ ] Local-testing-mode artifacts, if mentioned, are labeled as non-canonical operational outputs.
- [ ] Backend name, timestamp, and mitigation context are preserved where IBM data are discussed.

## Figures and Tables

- [ ] Figures and tables follow the repository figure and table style guide.
- [ ] Benchmark values are visible in the relevant figure or table context.
- [ ] Uncertainties and backend context are reported where appropriate.

## Interpretation

- [ ] The document distinguishes operational result, numerical comparison, and physical interpretation.
- [ ] The document states what the outputs do not establish physically.
- [ ] The document does not treat hardware noise patterns as cosmological evidence.

## Repository Governance

- [ ] The document cites the relevant repository policies when making governance or release claims.
- [ ] The milestone or release identifier is recorded when the document is part of Phase 6 dissemination or archival work.
