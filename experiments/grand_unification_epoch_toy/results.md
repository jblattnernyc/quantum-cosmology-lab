# Results

## Benchmark Interpretation

For the default parameter set in [config.yaml](config.yaml), the exact two-site
benchmark gives:

- ground-state energy: `-0.8204719227933479`
- order-parameter expectation: `0.8941919634759182`
- domain-wall density: `0.029822206193642085`
- transverse-coherence expectation: `0.28339891995741684`
- effective-Hamiltonian expectation: `-0.8204719227933478`

Within this truncation, the benchmark ground state is strongly biased toward
one ordered orientation while retaining a small anti-aligned component and a
nonzero transverse-coherence signal. The scientifically justified statement is
therefore modest: for the declared two-site `Z2` toy Hamiltonian and parameter
choice, the ground state has a large reduced order parameter and low
domain-wall proxy value.

## What the Outputs Mean

The experiment computes expectation values of explicitly declared operators in
a finite two-site `Z2` symmetry-breaking toy model:

- `order_parameter_expectation` measures the average retained `Z2` orientation,
- `domain_wall_density` measures support in the anti-aligned two-site sector,
- `transverse_coherence_expectation` measures mixing under the transverse term,
- `effective_hamiltonian_expectation` verifies consistency against the
  projected Hamiltonian benchmark.

For the default repository workflow:

- the exact local workflow reproduced the benchmark to numerical precision,
- the noisy local workflow returned
  - `order_parameter_expectation = 0.8673662045716406`,
  - `domain_wall_density = 0.057609713807597995`,
  - `transverse_coherence_expectation = 0.27489695235869493`,
  - `effective_hamiltonian_expectation = -0.7767027217898765`.

Relative to the benchmark, the noisy local absolute errors were:

- `0.02682575890427763` for the order-parameter expectation,
- `0.02778750761395591` for the domain-wall density,
- `0.008501967598721905` for the transverse-coherence expectation,
- `0.04376920100347126` for the effective-Hamiltonian expectation.

On this host, the noisy local artifact was generated through the repository's
host-safe analytic readout-error fallback because live Aer execution is guarded
on macOS arm64 with Python 3.13+. The fallback applies the declared symmetric
readout-error model to the exact Pauli-term expectations and records that
provenance explicitly in the noisy-local JSON artifact.

## What the Outputs Do Not Establish

The experiment does not establish:

- a literal simulation of the Grand Unification Epoch,
- a realistic grand unified gauge theory,
- a realistic `SU(5)`, `SO(10)`, Pati-Salam, or supersymmetric unification
  model,
- thermal symmetry-breaking dynamics,
- monopole production or dilution,
- baryogenesis,
- running gauge couplings,
- continuum lattice-gauge behavior,
- or any physical claim beyond the retained two-site `Z2` toy Hamiltonian.

The present result is a benchmarked reduced toy model only. The epoch label
provides context, not proof of literal physical simulation.

## IBM Runtime Hardware Execution

IBM Runtime execution has been run once for this experiment after benchmark,
exact-local, and noisy-local validation. The run used the `ibm_fez` backend and
completed with job id `d7fgo7q1u7fs739lvlb0`.

The hardware-tier estimates were:

- `order_parameter_expectation = 0.8708746845426667 ± 0.016889790569189725`,
- `domain_wall_density = 0.05090681263602187 ± 0.012942024461402234`,
- `transverse_coherence_expectation = 0.2755256075831184 ± 0.022112692929680492`,
- `effective_hamiltonian_expectation = -0.7865686314995806 ± 0.019498423021069702`.

Relative to the benchmark, the IBM hardware absolute errors were:

- `0.02331727893325153` for the order-parameter expectation,
- `0.021084606442379784` for the domain-wall density,
- `0.007873312374298447` for the transverse-coherence expectation,
- `0.033903291293767235` for the effective-Hamiltonian expectation.

This hardware result is an execution-tier comparison against the benchmarked
reduced model. It is not primary physical evidence for Grand-Unification-Epoch
dynamics and does not change the reduced toy-model status of the experiment.

## Expected Review Standard

This experiment should be reviewed by checking:

- whether the benchmark values are reproduced exactly in the local exact tier,
- whether the noisy local tier remains interpretable under the declared
  readout-error model,
- whether any later IBM Runtime output is compared against the benchmarked
  exact-local and noisy-local tiers rather than treated in isolation,
- whether any IBM Runtime run is accompanied by metadata JSON, comparison JSON,
  and a hardware report.

The detailed generated outputs are written to the configured JSON and report
paths under `data/processed/grand_unification_epoch_toy/` and
`results/reports/grand_unification_epoch_toy/`.

The generated analysis summary is available at
[analysis_report.md](../../results/reports/grand_unification_epoch_toy/analysis_report.md).
