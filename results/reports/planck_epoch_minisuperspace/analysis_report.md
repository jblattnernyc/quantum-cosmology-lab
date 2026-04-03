# planck_epoch_minisuperspace Analysis Report

## Benchmark

- Ground-state energy: -0.134279
- Scale-factor expectation value: 0.340958
- Volume expectation value: 0.058452
- smallest_scale_factor_probability: 0.114212
- Largest retained scale-factor probability: 0.128097

## Execution Comparison

- Exact local scale-factor value: 0.340958
- Noisy local scale-factor value: 0.341814
- Exact local absolute scale-factor error: 1.110223e-16
- Noisy local absolute scale-factor error: 8.564487e-04

## IBM Runtime Summary

- IBM backend: `ibm_kingston`
- IBM job id: `d782gp9q1efs73d18kng`
- scale_factor_expectation_value: 0.340249 (abs. error: 7.088017e-04, uncertainty: 5.739918e-03)
- volume_expectation_value: 0.058641 (abs. error: 1.895078e-04, uncertainty: 2.902245e-03)
- effective_hamiltonian_expectation: -0.133992 (abs. error: 2.868415e-04, uncertainty: 3.346624e-03)
- smallest_scale_factor_probability: 0.113559 (abs. error: 6.530722e-04, uncertainty: 1.539648e-02)

## Interpretation

The exact local workflow reproduces the direct diagonalization benchmark for the reduced minisuperspace model defined by the selected configuration.
The noisy local workflow uses a host-safe analytic readout-error fallback because live Aer execution is guarded on this host. In this experiment the configured Aer gate-noise component is inactive for the generated state-preparation circuit, so the fallback remains faithful to the declared noisy-local model for the reported observables.
The IBM Runtime tier, when present, remains subordinate to the benchmark, exact-local, and noisy-local tiers and must be read through the associated hardware report and metadata capture.

IBM execution JSON: `data/processed/planck_epoch_minisuperspace/ibm_runtime.json`
IBM metadata JSON: `data/raw/planck_epoch_minisuperspace/ibm_runtime_metadata.json`
IBM hardware report: `results/reports/planck_epoch_minisuperspace/ibm_runtime_report.md`

Table: `results/tables/planck_epoch_minisuperspace/observable_summary.md`

Figure: `results/figures/planck_epoch_minisuperspace/observable_comparison.png`
