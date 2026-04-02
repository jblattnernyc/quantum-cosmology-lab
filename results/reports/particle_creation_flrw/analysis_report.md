# Particle-Creation FLRW Analysis Report

## Benchmark

- Single-mode particle number expectation: 0.034229
- Total particle number expectation: 0.068457
- Pairing correlator expectation: -0.346545

## Execution Comparison

- Exact local total particle number: 0.068457
- Noisy local total particle number: 0.122302
- Exact local absolute total-particle error: 0.000000e+00
- Noisy local absolute total-particle error: 5.384495e-02

## Interpretation

The exact local workflow reproduces the exact discrete benchmark of the retained two-mode FLRW particle-creation toy model.
The noisy local workflow preserves a nonzero particle-number signal and the sign of the pairing correlator under the explicit Aer noise model, but it is not interpreted as evidence for a full continuum curved-spacetime field theory.
The IBM Runtime tier, when present, remains subordinate to the benchmark, exact-local, and noisy-local tiers and must be read through the associated hardware report and metadata capture.

IBM execution JSON: `data/processed/particle_creation_flrw/ibm_runtime.json`
IBM metadata JSON: `data/raw/particle_creation_flrw/ibm_runtime_metadata.json`
IBM hardware report: `results/reports/particle_creation_flrw/ibm_runtime_report.md`

Table: `results/tables/particle_creation_flrw/observable_summary.md`

Figure: `results/figures/particle_creation_flrw/observable_comparison.png`
