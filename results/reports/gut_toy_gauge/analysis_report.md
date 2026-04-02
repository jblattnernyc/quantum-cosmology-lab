# Gut Toy Gauge Analysis Report

## Benchmark

- Ground-state energy: -0.300000
- Gauge-invariance violation expectation: 0.000000
- Link-alignment order parameter: -0.600000
- Wilson-line correlator proxy: 0.800000

## Execution Comparison

- Exact local gauge-violation value: 0.000000
- Noisy local gauge-violation value: 0.039568
- Exact local link-alignment value: -0.600000
- Noisy local link-alignment value: -0.586331

## Interpretation

The exact local workflow reproduces the direct diagonalization benchmark for the reduced two-link Z2 gauge toy model.
The noisy local workflow preserves a low gauge-violation signal while degrading the order-parameter and Wilson-line proxy values under the explicit Aer noise model, so any IBM-tier interpretation must remain subordinate to these benchmarked tiers.
The IBM Runtime tier, when present, remains subordinate to the benchmark, exact-local, and noisy-local tiers and must be read through the associated hardware report and metadata capture.

IBM execution JSON: `data/processed/gut_toy_gauge/ibm_runtime.json`
IBM metadata JSON: `data/raw/gut_toy_gauge/ibm_runtime_metadata.json`
IBM hardware report: `results/reports/gut_toy_gauge/ibm_runtime_report.md`

Table: `results/tables/gut_toy_gauge/observable_summary.md`

Figure: `results/figures/gut_toy_gauge/observable_comparison.png`
