# Particle-Creation FLRW Analysis Report

## Benchmark

- Single-mode particle number expectation: 0.038921
- Total particle number expectation: 0.077841
- Pairing correlator expectation: -0.325517

## Execution Comparison

- Exact local total particle number: 0.077841
- Noisy local total particle number: 0.135791
- Exact local absolute total-particle error: 2.498002e-16
- Noisy local absolute total-particle error: 5.795008e-02

## Validation Status

- Current lineage: `55f8373cc4fe4f6e808305bf3c42a356794a98c8df70ec8e95358f551d9ea7c8`

| Tier | Lineage | Assessment mode | Stored assessment matches | Result |
|---|---|---|---|---|
| Independent benchmark | current | fresh_matrix_recomputation | True | PASS |
| Exact local | current | recomputed_current_policy | True | PASS |
| Noisy local | current | recomputed_current_policy | True | PASS |
| IBM Runtime | legacy_unbound | retrospective_current_policy | None | FAIL |

## Interpretation

The exact local workflow reproduces the exact discrete benchmark of the retained two-mode FLRW particle-creation toy model.
The independent matrix benchmark separately reconstructs the four-dimensional evolution and quantifies time-slice refinement under an explicitly added continuum interpolation.
The noisy local workflow preserves a nonzero particle-number signal and the sign of the pairing correlator under the explicit Aer noise model, but it is not interpreted as evidence for a full continuum curved-spacetime field theory.
The IBM Runtime tier, when present, remains subordinate to the benchmark, exact-local, and noisy-local tiers and must be read through the associated hardware report and metadata capture.
Its validation status above is a current-policy assessment. A legacy-unbound result is retrospective evidence and is not eligible as prerequisite evidence for a new hardware run.

IBM execution JSON: `data/processed/particle_creation_flrw/ibm_runtime.json`
IBM metadata JSON: `data/raw/particle_creation_flrw/ibm_runtime_metadata.json`
IBM hardware report: `results/reports/particle_creation_flrw/ibm_runtime_report.md`

Table: `results/tables/particle_creation_flrw/observable_summary.md`

Figure: `results/figures/particle_creation_flrw/observable_comparison.png`

Independent validation report: `results/reports/particle_creation_flrw/independent_validation_report.md`
Convergence table: `results/tables/particle_creation_flrw/convergence_summary.md`

Exploratory hardware-feasibility report: `results/reports/particle_creation_flrw/hardware_feasibility_report.md`
Hardware-feasibility table: `results/tables/particle_creation_flrw/hardware_feasibility_summary.md`
