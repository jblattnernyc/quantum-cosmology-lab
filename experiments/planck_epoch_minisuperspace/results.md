# Results

## Benchmark Interpretation

For the default parameter set in [config.yaml](config.yaml), the direct
four-bin benchmark gives:

- ground-state energy: `-0.13427869803736275`
- scale-factor expectation value: `0.3409579452907098`
- volume expectation value: `0.058451698470842514`
- smallest retained scale-factor probability: `0.11421160961397295`
- largest retained scale-factor probability: `0.12809746928767865`

Within this truncation, the benchmark ground state distributes support across
all four retained positive-scale-factor bins. The primary model-specific
statement supported by the benchmark is therefore modest: for the chosen
effective couplings, the projected stationary state retains nonzero weight in
the smallest resolved bin while remaining a property of the declared
finite-dimensional operator only.

## What the Outputs Mean

The experiment computes expectation values of explicitly declared operators in a
four-bin reduced model:

- `scale_factor_expectation_value` measures the mean scale factor within the
  retained truncation,
- `volume_expectation_value` measures the corresponding retained `a^3` proxy,
- `effective_hamiltonian_expectation` verifies consistency against the
  projected Hamiltonian benchmark,
- `smallest_scale_factor_probability` measures support on the smallest retained
  positive-scale-factor bin.

The exact local workflow should reproduce the benchmark to numerical precision.
For the tracked repository run captured by the generated artifacts:

- the exact local workflow reproduced the benchmark to numerical precision,
- the noisy local workflow returned
  - `scale_factor_expectation_value = 0.3418143940325237`,
  - `volume_expectation_value = 0.05979506679044425`,
  - `effective_hamiltonian_expectation = -0.12449581029536433`,
  - `smallest_scale_factor_probability = 0.12459081541442275`.

Relative to the benchmark, the noisy local absolute errors were:

- `0.0008564487418138422` for the scale-factor expectation,
- `0.0013433683196017385` for the volume proxy,
- `0.009782887741998425` for the effective Hamiltonian expectation,
- `0.010379200956088075` for the smallest-bin probability.

On this host, the noisy local artifact was generated through a host-safe
analytic readout-error fallback because live Aer execution is guarded on macOS
arm64 with Python 3.13+. In this experiment the configured Aer gate-noise model
is attached only to `ry` instructions, and the decomposed state-preparation
circuit contains no `ry` gates, so the fallback remains faithful to the
declared noisy-local model for the reported observables.

## IBM Runtime Hardware Execution

The live IBM Runtime workflow was then executed on `ibm_kingston` and completed
successfully on April 3, 2026, with job id `d782gp9q1efs73d18kng`. The hardware
report for this archived run is available at
[ibm_runtime_report.md](../../results/reports/planck_epoch_minisuperspace/ibm_runtime_report.md).

For the canonical tracked live-hardware artifact, the returned observables were:

- `scale_factor_expectation_value = 0.3402491436254437 +- 0.005739917561251769`
- `volume_expectation_value = 0.05864120622492208 +- 0.0029022643219695276`
- `effective_hamiltonian_expectation = -0.13399185652173115 +- 0.003347497490286022`
- `smallest_scale_factor_probability = 0.11355854226799772 +- 0.015395956326286616`

Relative to the benchmark, the hardware absolute errors were:

- `0.0007088016652662121` for the scale-factor expectation,
- `0.0001895077540795681` for the volume proxy,
- `0.00028684151563160287` for the effective Hamiltonian expectation,
- `0.0006530721903369591` for the smallest-bin probability.

These values remain close to the benchmark within the declared reduced model and
its reported estimator uncertainties. The hardware tier therefore supports a
conservative execution claim: the declared two-qubit reduced minisuperspace
observables were reproduced on a real IBM quantum backend with small benchmark
deviations for this archived run.

## What the Outputs Do Not Establish

The experiment does not establish:

- a literal simulation of the Planck Epoch,
- a full Wheeler-DeWitt wave function,
- a full theory of singularity resolution,
- realistic Planck-scale quantum gravity,
- or any cosmological claim beyond the retained reduced operator and its
  declared observables.

The present result is a benchmarked reduced toy model only.

## Expected Review Standard

This experiment should be reviewed by checking:

- whether the benchmark values are reproduced exactly in the local exact tier,
- whether the noisy local tier remains numerically interpretable under the
  explicit Aer noise model,
- whether the IBM Runtime output is compared to these tiers rather than treated
  in isolation,
- whether the IBM Runtime run is accompanied by its metadata JSON and hardware
  report.

The detailed generated outputs are written to the configured JSON and report
paths under `data/processed/planck_epoch_minisuperspace/` and
`results/reports/planck_epoch_minisuperspace/`.

The default generated analysis summary is available at
[analysis_report.md](../../results/reports/planck_epoch_minisuperspace/analysis_report.md).
