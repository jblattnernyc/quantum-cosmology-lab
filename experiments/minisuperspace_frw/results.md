# Results

## Benchmark Interpretation

For the default parameter set in [config.yaml](config.yaml), the direct two-state benchmark gives:

- ground-state energy: `-0.3`
- scale-factor expectation value: `1.24`
- volume expectation value: `2.2384`
- probability weight in the larger scale-factor bin: `0.8`

Within this truncation, the benchmark ground state places most of its support on the larger positive-scale-factor bin while retaining nonzero amplitude in the smaller bin. The primary cosmological statement supported by the model is therefore modest: for the chosen effective couplings, the projected stationary reference state is biased toward the larger of the two retained scale-factor bins.

## What the Outputs Mean

The experiment computes expectation values of explicitly declared operators in a two-state reduced model:

- `scale_factor_expectation_value` measures the mean scale factor within the retained truncation,
- `volume_expectation_value` measures the corresponding truncated `a^3` proxy,
- `effective_hamiltonian_expectation` verifies consistency against the projected Hamiltonian benchmark.

For the default repository run captured by the generated artifacts:

- the exact local workflow reproduced the benchmark to numerical precision,
- the noisy local Aer workflow returned
  - `scale_factor_expectation_value = 1.22784`,
  - `volume_expectation_value = 2.1999744`,
  - `effective_hamiltonian_expectation = -0.283776`.

Relative to the benchmark, the noisy local absolute errors were:

- `0.01216` for the scale-factor expectation,
- `0.0384256` for the volume proxy,
- `0.016224` for the effective Hamiltonian expectation.

Within this explicit noise model, the ordering and approximate magnitude of the benchmark observables are preserved.

## What the Outputs Do Not Establish

The experiment does not establish:

- a full solution of FRW quantum cosmology,
- a full Wheeler-DeWitt wave function,
- a full quantum-gravity description of the early universe,
- any claim about the Planck epoch or inflation as literal simulated regimes.

The present result is a benchmarked reduced toy model only.

## Expected Review Standard

This experiment should be reviewed by checking:

- whether the benchmark values are reproduced exactly in the local exact tier,
- whether the noisy local tier remains interpretable under the explicit Aer noise model,
- whether any later IBM Runtime output is compared to these tiers rather than treated in isolation,
- whether any IBM Runtime run is accompanied by its metadata JSON and hardware report.

The detailed generated outputs are written to the configured JSON and report paths under `data/processed/minisuperspace_frw/` and `results/reports/minisuperspace_frw/`.

The default generated analysis summary is available at [analysis_report.md](../../results/reports/minisuperspace_frw/analysis_report.md).
