# Citation and Bibliography Policy

## Purpose

This document defines the repository-standard citation and bibliography policy for Quantum Cosmology Lab reports, model notes, preserved Phase 6 milestone reports, and archival release materials used under the current governance baseline.

The objective is not to force a journal-specific style on every future publication. The objective is to ensure that the lab's internal and archival documents preserve enough bibliographic structure to identify scientific sources, computational methods, repository artifacts, and historical materials clearly and reproducibly.

## Scope

This policy applies to:

- repository-level governance and milestone documents,
- experiment `model.md` and `results.md` files when they are updated,
- internal review memoranda,
- replication notes,
- archival release manifests and release-adjacent documentation.

## Citation Categories

Documents in this repository should distinguish among the following citation classes:

- primary scientific literature for the mathematical model or physical interpretation,
- methodological and computational references for Qiskit, numerical procedures, and estimator workflows,
- repository-governance documents such as `AGENTS.md`, `PLANS.md`, and repository policy files,
- experiment-level repository artifacts such as benchmark JSON, analysis reports, and IBM hardware reports,
- historical or contextual materials that are not themselves part of the validated scientific record.

These categories should not be merged rhetorically. A benchmark JSON file is not a substitute for a primary literature citation, and a historical source is not a substitute for a methodological reference.

## Internal Default Style

For repository-internal documents, the default bibliographic style is author-date with full titles and stable identifiers when available.

At minimum, bibliography entries should preserve:

- author or responsible organization,
- year,
- full title,
- venue or publisher when applicable,
- version number when applicable,
- DOI or other stable identifier when available,
- stable URL for online documentation when no DOI exists,
- access date for web documentation that may change over time.

Venue-specific publication submissions may later convert this metadata into a numeric or journal-mandated style, but the internal source record should remain complete enough to support that conversion.

## Repository Artifact Citation

When citing repository outputs, identify the artifact class explicitly rather than citing the repository root alone.

Use the most specific stable artifact that supports the claim:

- `model.md` for the declared model statement,
- `results.md` for experiment-level interpretation,
- benchmark JSON for exact reference values,
- analysis reports and summary tables for derived comparisons,
- IBM hardware reports, metadata JSON, and `ibm_runtime_runs.jsonl` manifest entries for hardware provenance.

Repository artifact citations should preserve:

- experiment name,
- artifact type,
- path or release-manifest reference,
- milestone or release identifier when one exists,
- timestamp for IBM hardware records when the claim depends on a specific preserved run.

## IBM Hardware Provenance Citation

IBM hardware discussion must cite both the interpreted report layer and the preserved provenance layer.

When a live IBM result is discussed in an internal report or milestone document, cite:

- the canonical hardware report,
- the timestamped archived hardware report or archived JSON artifact,
- the corresponding `data/raw/<experiment>/ibm_runtime_runs.jsonl` manifest entry.

This three-part citation structure preserves:

- the human-readable report,
- the immutable archived run record,
- the append-only manifest context showing how the archived and canonical files relate.

Local-testing-mode artifacts may be cited for operational debugging or wrapper validation, but they must be labeled explicitly as local-testing artifacts and not as live QPU records.

## Bibliography Construction Rules

Each document should keep one consistent bibliography style throughout.

Bibliographies should:

- separate primary scientific references from repository artifacts when that distinction matters,
- prefer DOI-bearing sources for published scientific literature,
- cite official Qiskit or IBM Runtime documentation when version-sensitive implementation claims are made,
- avoid unsupported paraphrases of platform behavior when an official documentation citation is available,
- include enough metadata to recover the source without relying on search-engine context.

## Historical and Contextual Sources

Historical or contextual materials may be included when they clarify the background of a model, method, or repository decision. They must be labeled as contextual or historical sources and must not be presented as direct validation of the experiment implementation.

## Minimal Citation Set for Historical Phase 6 Milestone Materials

At minimum, a historical Phase 6 milestone report or archival release packet should cite:

- `AGENTS.md`,
- `PLANS.md`,
- the relevant experiment `model.md` and `results.md` files,
- the repository-level figure and table style guide,
- the relevant IBM hardware report and manifest entry when live IBM results are mentioned.
