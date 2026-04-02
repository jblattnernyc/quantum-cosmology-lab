# Minisuperspace FRW Analysis Report

## Benchmark

- Ground-state energy: -0.300000
- Scale-factor expectation value: 1.240000
- Volume expectation value: 2.238400

## Execution Comparison

- Exact local scale-factor value: 1.240000
- Noisy local scale-factor value: 1.227840
- Exact local absolute scale-factor error: 2.220446e-16
- Noisy local absolute scale-factor error: 1.216000e-02

## Interpretation

The exact local workflow reproduces the direct diagonalization benchmark for the reduced two-state model.
The noisy local workflow preserves the ordering and approximate magnitude of the benchmark observables under the explicit Aer noise model, but it is not interpreted as evidence for full quantum-cosmological dynamics beyond this truncation.
The IBM Runtime tier, when present, remains subordinate to the benchmark, exact-local, and noisy-local tiers and must be read through the associated hardware report and metadata capture.

IBM execution JSON: `data/processed/minisuperspace_frw/ibm_runtime.json`
IBM metadata JSON: `data/raw/minisuperspace_frw/ibm_runtime_metadata.json`
IBM hardware report: `results/reports/minisuperspace_frw/ibm_runtime_report.md`

Table: `results/tables/minisuperspace_frw/observable_summary.md`

Figure: `results/figures/minisuperspace_frw/observable_comparison.png`
