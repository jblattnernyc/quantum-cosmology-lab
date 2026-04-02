# Results

## Benchmark Interpretation

For the default parameter set in `config.yaml`, the direct two-link benchmark gives:

- ground-state energy: `-0.3`
- gauge-invariance violation expectation: `0.0`
- link-alignment order parameter: `-0.6`
- Wilson-line correlator proxy: `0.8`
- physical-sector probability: `1.0`

Within this truncation, the benchmark ground state lies entirely in the retained gauge-invariant sector and is biased toward the `|11>` link-alignment state while remaining coherently mixed with `|00>`.

## What the Outputs Mean

The experiment computes expectation values of explicitly declared operators in a reduced two-link `Z2` toy model:

- `gauge_invariance_violation_expectation` measures leakage into the odd-parity, gauge-violating sector,
- `link_alignment_order_parameter` measures the average retained link orientation,
- `wilson_line_correlator_proxy` measures coherence under a reduced two-link flip operator.

For the default repository run captured by the generated artifacts:

- the exact local workflow reproduced the benchmark to numerical precision,
- the noisy local Aer workflow returned
  - `gauge_invariance_violation_expectation = 0.03956834532374098`,
  - `link_alignment_order_parameter = -0.5863309352517986`,
  - `wilson_line_correlator_proxy = 0.7248201438848921`.

Relative to the benchmark, the noisy local absolute errors were:

- `0.03956834532374098` for gauge-invariance violation,
- `0.013669064748201398` for the link-alignment order parameter,
- `0.0751798561151078` for the Wilson-line correlator proxy.

Within this explicit noise model, the gauge-invariant sector remains dominant, but the reduced order parameter and Wilson proxy both degrade measurably. The noisy local workflow should therefore be interpreted as a degradation study for these declared observables, not as primary physical evidence.

## What the Outputs Do Not Establish

The experiment does not establish:

- a realistic grand unified gauge simulation,
- realistic non-Abelian lattice dynamics,
- literal GUT-era symmetry breaking,
- continuum confinement physics,
- direct early-universe field-theory realism beyond the declared two-link toy truncation.

The present result is a benchmarked reduced toy-gauge model only.

## Expected Review Standard

This experiment should be reviewed by checking:

- whether the benchmark values are reproduced exactly in the local exact tier,
- whether the noisy local tier preserves low gauge-violation leakage and interpretable reduced observables,
- whether any later IBM Runtime output is compared against the benchmarked exact-local and noisy-local tiers rather than treated in isolation,
- whether any IBM Runtime run is accompanied by its metadata JSON and hardware report.
