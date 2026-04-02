# Figure and Table Style Guide

## Purpose

This document defines the repository-standard presentation rules for figures and tables used in official experiment analysis, milestone reporting, and archival release materials.

The governing principle is that figures and tables are analytical supports. They must not substitute for the explicit model statement, benchmark definition, or written interpretive limits.

## Shared Principles

Every figure or table should make the following items unambiguous:

- which experiment or repository document it belongs to,
- which observable or quantity is being shown,
- which execution tier each value or series represents,
- whether the quantity has units or is dimensionless,
- what the reader may and may not infer physically from the display.

When a quantity is dimensionless, state that fact explicitly rather than leaving units blank without explanation.

## Figure Requirements

Figures should:

- use a descriptive title tied to the declared experiment and observable set,
- label axes with observable names and units or dimensionless status,
- distinguish benchmark, exact local, noisy local, and IBM hardware data clearly in legends and captions,
- preserve conservative visual scaling rather than exaggerating small differences,
- avoid decorative styling that obscures numerical comparison,
- state backend and date context in the caption or accompanying text when IBM hardware data are shown.

Repository-standard comparison figures should preserve the benchmark as the reference visual baseline. Candidate execution tiers should be presented as comparisons against that baseline rather than as stand-alone visual claims.

## Table Requirements

Tables should identify:

- observable name,
- benchmark value,
- execution-tier value,
- absolute error,
- relative error when defined,
- uncertainty when available,
- backend context when IBM hardware data are included.

For IBM hardware tables, include or accompany the table with:

- backend name,
- UTC execution timestamp or archived run label,
- job identifier when appropriate for provenance review,
- mitigation setting summary when relevant to the comparison.

## Captions and Surrounding Text

Captions and surrounding prose should:

- state what was computed,
- state the reduced or toy status of the model when applicable,
- distinguish operational comparison from physical interpretation,
- avoid phrases that imply full early-universe simulation unless the model statement supports such language explicitly.

## File Naming and Storage

Figures and tables should continue to follow the established repository layout:

- figures under `results/figures/<experiment>/`,
- tables under `results/tables/<experiment>/`,
- report-level references under `results/reports/<experiment>/`.

Repository-level milestone reports may additionally reference:

- milestone reports under `results/reports/milestones/`,
- archival manifests under `data/processed/releases/`.

## Prohibited Presentation Practices

The following practices are not acceptable for official materials:

- unlabeled axes or legend entries,
- tables that omit benchmark values while presenting hardware values alone,
- captions that treat noisy deviations as self-interpreting physical structure,
- visually dramatic scaling choices that overstate agreement or disagreement,
- screenshots used as the sole preserved evidence for an analytical claim.
