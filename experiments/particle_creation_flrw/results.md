# Results

## Benchmark Interpretation

For the default parameter set in [config.yaml](config.yaml), the exact discrete benchmark gives:

- single-mode particle number expectation: `0.03422860544437149`
- total particle number expectation: `0.06845721088874299`
- pairing correlator expectation: `-0.3465452307022458`
- pair-occupation probability: `0.03422860544437149`
- even-parity probability: `1.0`

Within this truncation, the benchmark indicates a small but nonzero retained pair-creation signal. Most amplitude remains in the vacuum component, while the `|11>` sector acquires a controlled nonzero occupation. The scientifically justified statement is therefore modest: the declared discrete two-mode model produces a measurable pair-occupation signal under the prescribed expanding-background schedule.

## What the Outputs Mean

The experiment computes expectation values of explicitly declared operators in a two-mode single-pair truncation:

- `single_mode_particle_number_expectation` measures retained occupation in one mode,
- `total_particle_number_expectation` measures the total retained particle number of the mode pair,
- `pairing_correlator_expectation` measures the anomalous pair coherence `a_k^dagger a_-k^dagger + a_k a_-k`.

For the default repository workflow, the exact local estimator path should reproduce the benchmark to numerical precision. The noisy local Aer path should be interpreted only as a test of robustness for these reduced observables under an explicit local noise model.

For the default generated outputs in this repository:

- the exact local workflow reproduced the benchmark to numerical precision,
- the noisy local Aer workflow returned
  - `single_mode_particle_number_expectation = 0.06384892086330934`,
  - `total_particle_number_expectation = 0.12230215827338126`,
  - `pairing_correlator_expectation = -0.302158273381295`.

Relative to the benchmark, the noisy local absolute errors were:

- `0.029620315418937865` for the single-mode particle number,
- `0.0538449473846383` for the total particle number,
- `0.044386957320950715` for the pairing correlator.

Within this explicit noise model, the noisy tier preserves the sign of the anomalous pair correlator and retains a particle-number signal of the same order of magnitude as the benchmark.

## What the Outputs Do Not Establish

The experiment does not establish:

- a full continuum calculation of particle creation in FLRW spacetime,
- a full inflationary perturbation spectrum,
- reheating dynamics,
- mode summation over a field-theory vacuum,
- any claim that the repository has literally simulated inflation.

The present result is a benchmarked reduced QFT-in-curved-spacetime toy model only.

## Expected Review Standard

This experiment should be reviewed by checking:

- whether the benchmark values are reproduced exactly in the local exact tier,
- whether the noisy local tier preserves an interpretable particle-number signal,
- whether any later IBM Runtime output is compared against both prior tiers rather than treated in isolation,
- whether any IBM Runtime run is accompanied by its metadata JSON and hardware report.

The detailed generated outputs are written to the configured JSON and report paths under `data/processed/particle_creation_flrw/` and `results/reports/particle_creation_flrw/`.

The default generated analysis summary is available at [analysis_report.md](../../results/reports/particle_creation_flrw/analysis_report.md).
