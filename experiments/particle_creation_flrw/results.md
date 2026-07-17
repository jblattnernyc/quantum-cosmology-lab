# Results

## Benchmark Interpretation

For the default parameter set in [config.yaml](config.yaml), the exact discrete benchmark gives:

- single-mode particle number expectation: `0.03892064274087119`
- total particle number expectation: `0.07784128548174238`
- pairing correlator expectation: `-0.32551651813899957`
- pair-occupation probability: `0.03892064274087119`
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
  - `single_mode_particle_number_expectation = 0.06294964028776978`,
  - `total_particle_number_expectation = 0.13579136690647486`,
  - `pairing_correlator_expectation = -0.28057553956834536`.

Relative to the benchmark, the noisy local absolute errors were:

- `0.024028997546898592` for the single-mode particle number,
- `0.057950081424732486` for the total particle number,
- `0.04494097857065421` for the pairing correlator.

Within this explicit noise model, the noisy tier preserves the sign of the anomalous pair correlator and retains a particle-number signal of the same order of magnitude as the benchmark.

Under the acceptance policies declared in [config.yaml](config.yaml), the
current exact-local and noisy-local observable values pass. This is an
experiment-specific workflow result: it establishes consistency with the
declared finite-dimensional benchmark and robustness under the declared local
noise model, not validation of an untruncated continuum calculation.

## Independent Reproduction and Discretization Refinement

The independent validator reconstructs the declared evolution as explicit
four-dimensional phase and pairing generators and applies SciPy matrix
exponentials without using the experiment's benchmark-evolution, circuit, or
observable-construction helpers. Its first responsibility is to reproduce the
official `N = 6` discrete statevector and observables to the configured
floating-point tolerances while preserving normalization and even parity.
The official slice is the symmetric
phase-half/pairing/phase-half composition declared in [model.md](model.md), and
the independent implementation reconstructs all three factors separately.

Separately, it evaluates `N = 6, 12, 24, 48, 96` against an ODE reference built
from a linear interpolation of the prescribed scale factor. This refinement
study measures sensitivity to the time discretization. The interpolated ODE is
an additional assumption and is not treated as the official benchmark or as a
continuum-exact curved-spacetime field calculation. Agreement with the
discrete `N = 6` benchmark and convergence toward the interpolated ODE answer
different questions: implementation reproduction and discretization
sensitivity, respectively.

For the default configuration, the independent discrete result passes with a
maximum observable deviation of approximately `5.55e-17`, a phase-aligned
maximum amplitude error of approximately `1.11e-16`, and zero odd-parity
probability. At `N = 96`, the maximum observable deviation from the added ODE
reference is approximately `2.49e-5`, the state infidelity is approximately
`1.92e-10`, and the final observed convergence order is approximately `2.000`.
At the official `N = 6`, the maximum observable error is approximately
`6.42e-3`; the earlier first-order product gave approximately `2.74e-2` under
the same diagnostic. These values satisfy the strengthened acceptance policy
recorded in [config.yaml](config.yaml). The comparison supports the symmetric
factor ordering as a discretization refinement only; it does not relax the
two-mode truncation or the continuum-interpretation limits.

## Exploratory Hardware-Feasibility Study

The transpilation-only study compares `N = 6, 12, 24` against the fixed
`FakeManilaV2` calibration snapshot at optimization level `1` across five
deterministic transpiler seeds. It performs no estimator execution and makes no
IBM service connection. For the configured historical fake-backend snapshot,
the aggregate results are:

- `N = 6`: median depth `73`, median CX count `24`, median two-qubit
  calibration-error proxy approximately `0.191687`;
- `N = 12`: median depth `145`, median CX count `48`, median two-qubit
  calibration-error proxy approximately `0.346630`;
- `N = 24`: median depth `289`, median CX count `96`, median two-qubit
  calibration-error proxy approximately `0.573108`.

Every seed selected the adjacent physical pair `[0, 1]`, and no SWAP
instruction survived ISA translation. Routing is therefore not the dominant
structural burden in this study; decomposition of the repeated pairing
rotations is. The proxy is not fidelity and omits readout, idling, crosstalk,
coherent accumulation, observable synthesis, and mitigation. `N = 6` remains
the least costly hardware candidate among the compared discretizations, but
live hardware remains deferred because the snapshot is historical and the
structural proxies do not establish observable accuracy.

The generated feasibility report is available at
[hardware_feasibility_report.md](../../results/reports/particle_creation_flrw/hardware_feasibility_report.md).

## Preserved IBM Result and Current Acceptance Status

The repository contains a preserved IBM Runtime result generated before the
validation-lineage schema was introduced. Its reported central values are
approximately:

- single-mode particle number: `0.303708` with uncertainty `0.0154`,
- total particle number: `0.591349` with uncertainty `0.025845`,
- pairing correlator: `-0.206725` with uncertainty `0.03324`.

A retrospective assessment against the current benchmark and policy classifies
all three observables as failing. The single-mode and total particle numbers
exceed their combined absolute/relative error tolerances and have standardized
residuals of approximately `17.2` and `19.9`, respectively. The pairing
correlator satisfies its broad numerical tolerance and sign/bound checks, but
its standardized residual is approximately `3.6`, above the configured maximum
of `3.0`. The preserved artifact also lacks the current lineage record and is
therefore ineligible as prerequisite evidence for a new hardware submission.
This classification is a statement about agreement with the declared reduced
model, not a claim about cosmological structure in the hardware deviations.

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
- whether the independent matrix implementation reproduces the official
  discrete benchmark and passes its declared refinement criteria,
- whether the noisy local tier passes its declared observable policies,
- whether any later IBM Runtime output is compared against both prior tiers rather than treated in isolation,
- whether independent-benchmark, benchmark, exact-local, and noisy-local
  artifacts share the current validation lineage,
- whether any IBM Runtime run is accompanied by its metadata JSON and hardware report.

The detailed generated outputs are written to the configured JSON and report paths under `data/processed/particle_creation_flrw/` and `results/reports/particle_creation_flrw/`.

The default generated analysis summary is available at [analysis_report.md](../../results/reports/particle_creation_flrw/analysis_report.md).
