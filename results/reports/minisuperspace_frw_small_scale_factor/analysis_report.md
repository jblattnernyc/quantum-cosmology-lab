# minisuperspace_frw_small_scale_factor Analysis Report

## Benchmark

- Ground-state energy: -0.134279
- Scale-factor expectation value: 0.340958
- Volume expectation value: 0.058452
- smallest_scale_factor_probability: 0.114212
- Largest retained scale-factor probability: 0.128097

## Execution Comparison

- Exact local scale-factor value: 0.340958
- Noisy local scale-factor value: 0.341232
- Exact local absolute scale-factor error: 1.110223e-16
- Noisy local absolute scale-factor error: 2.740691e-04

## Interpretation

The exact local workflow reproduces the direct diagonalization benchmark for the reduced minisuperspace model defined by the selected configuration.
The noisy local workflow preserves the ordering and approximate magnitude of the benchmark observables under the explicit Aer noise model, but it is not interpreted as evidence for full quantum-cosmological dynamics beyond the declared truncation.
The IBM Runtime tier, when present, remains subordinate to the benchmark, exact-local, and noisy-local tiers and must be read through the associated hardware report and metadata capture.

IBM execution JSON: `data/processed/minisuperspace_frw_small_scale_factor/ibm_runtime.json`
IBM metadata JSON: `data/raw/minisuperspace_frw_small_scale_factor/ibm_runtime_metadata.json`
IBM hardware report: `results/reports/minisuperspace_frw_small_scale_factor/ibm_runtime_report.md`

Table: `results/tables/minisuperspace_frw_small_scale_factor/observable_summary.md`

Figure: `results/figures/minisuperspace_frw_small_scale_factor/observable_comparison.png`
