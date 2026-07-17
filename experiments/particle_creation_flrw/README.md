# Particle Creation in FLRW

## Status

This directory now contains the second official Quantum Cosmology Lab experiment line: a reduced quantum-field-theory-in-curved-spacetime toy model for pair creation on a prescribed expanding FLRW-like background.

The implementation is intentionally modest. It is not a full field-theory simulation in an expanding universe, not a continuum calculation of cosmological perturbations, and not a literal inflation simulation. It is a benchmarked discrete two-mode truncation designed to capture a small, explicit particle-creation signal with clearly declared limits of interpretation.

## Scientific Question

For a single retained pair of scalar-field modes on a prescribed expanding FLRW-like background, truncated to occupations `0` and `1` in each mode, what particle-number and pair-correlation observables are produced by a stepwise time-dependent evolution, and how accurately do exact local and noisy local estimator workflows reproduce the benchmark?

## Model Summary

The experiment keeps one momentum pair of a scalar field:

- qubit `0`: retained occupation of mode `k`
- qubit `1`: retained occupation of mode `-k`

Each mode is truncated to the occupation set `{0, 1}`. Because the evolution starts from the vacuum and uses only pair-creation and pair-annihilation terms, the dynamics remain in the even-parity sector spanned by:

- `|00>`: no retained pair
- `|11>`: one retained pair

The background is prescribed rather than dynamically solved:

```text
a(eta_j) = a_initial + (a_final - a_initial) * j / N
```

with default values:

- `a_initial = 1.0`
- `a_final = 2.4`
- `N = 6`
- `time_extent = 1.5`

The retained mode frequency is

```text
omega_j = sqrt(k^2 + m^2 a(eta_j)^2)
```

with

- `k = 0.5`
- `m = 0.6`

For each time slice, the circuit uses the configured `symmetric_strang`
factor ordering:

1. one half of the diagonal midpoint-frequency phase,
2. a two-mode pairing rotation whose angle is

```text
theta_j = (1 / 2) log(omega_{j+1} / omega_j)
```

3. the remaining half of the diagonal phase.

This symmetric phase-half/pairing/phase-half composition is a
Bogoliubov-inspired discrete toy model. Its observed second-order convergence
is relative to the separately declared linear-interpolation ODE diagnostic and
does not mean that the repository has solved a full continuum FLRW
particle-production problem.

## Core Observables

- `single_mode_particle_number_expectation`
- `total_particle_number_expectation`
- `pairing_correlator_expectation`

The primary observable is the particle number in the retained mode pair. The pairing correlator is included as a squeezing-related diagnostic for the same reduced system.

## Directory Guide

- [model.md](model.md): mathematical statement, truncation, and interpretive limits
- [config.yaml](config.yaml): parameter choices, execution settings, and artifact paths
- [common.py](common.py): typed experiment configuration and time-slice construction helpers
- [benchmark.py](benchmark.py): exact benchmark for the declared discrete model
- [independent_benchmark.py](independent_benchmark.py): independent 4 x 4 matrix reproduction and time-slice convergence study
- [hardware_feasibility.py](hardware_feasibility.py): exploratory fake-backend transpilation study with no execution or submission
- [circuit.py](circuit.py): two-qubit stepwise evolution circuit
- [observables.py](observables.py): Pauli-decomposed particle-number and pairing observables
- [run_local.py](run_local.py): exact local estimator workflow
- [run_aer.py](run_aer.py): noisy local Aer estimator workflow
- [run_ibm.py](run_ibm.py): optional IBM Runtime workflow
- [analyze.py](analyze.py): comparison analysis and figure generation
- [results.md](results.md): written interpretation and limitations

## Reproducible Workflow

From the repository root with the virtual environment active:

```bash
python experiments/particle_creation_flrw/benchmark.py
python experiments/particle_creation_flrw/independent_benchmark.py
python experiments/particle_creation_flrw/run_local.py
python experiments/particle_creation_flrw/run_aer.py
python experiments/particle_creation_flrw/analyze.py
```

An exploratory hardware-cost study can be run separately:

```bash
python experiments/particle_creation_flrw/hardware_feasibility.py
# or: make particle-hardware-feasibility
```

This command transpiles `N = 6, 12, 24` circuits against the configured fake
backend over deterministic seeds. It records depth, one- and two-qubit gate
counts, layouts, surviving SWAP instructions, calibration-based error proxies,
and the independent continuum-refinement errors. It first requires current,
passing independent-validation evidence and records the exact source-artifact
digest. It does not execute a circuit, create an IBM Runtime service, or submit
a job. The error proxy assumes
independent calibrated instruction errors and omits readout, idling, crosstalk,
coherent error, observable synthesis, and mitigation; it is not circuit
fidelity.

For the current Apple Silicon Aer runtime note, including the macOS arm64 Python 3.13+ guard status, see the repository [user guide](../../docs/operations/user-guide.md).

The independent validator reconstructs the generators, slice propagators, and
observables directly with NumPy and `scipy.linalg.expm`; it does not call the
experiment's evolution, circuit, or observable helpers. It also evaluates the
declared `N = 6, 12, 24, 48, 96` refinement sequence against an ODE obtained by
linearly interpolating the prescribed scale factor. That ODE is an additional
discretization diagnostic, not a continuum-exact FLRW field calculation. The
configured acceptance policy requires monotone refinement, a final observed
order of at least `1.8`, a maximum `N = 96` observable error of `5.0e-5`, and a
maximum state infidelity of `1.0e-8`. It also requires the symmetric product to
reduce the official `N = 6` maximum observable error by at least a factor of
`3.0` relative to the superseded first-order phase-then-pairing product under
the same diagnostic.

The IBM Runtime path is intentionally separate and should be used only after
the independent, exact-local, and noisy-local validation outputs have been
reviewed:

```bash
python experiments/particle_creation_flrw/run_ibm.py --backend-name <backend>
```

The hardware entry point now enforces that ordering as a content-based gate.
The benchmark, exact-local result, noisy-local result, and independent
validation evidence carry the current validation lineage. Before a hardware
request can be submitted, `run_ibm.py` freshly recomputes the independent
matrix assessment, verifies that the stored independent content matches,
verifies that all prerequisite artifacts have the current lineage, and
recomputes both local-tier assessments from their persisted observable values.
All three assessments must pass the policies declared under `validation` in
[config.yaml](config.yaml). File existence alone is not sufficient. A change
to a model parameter, truncation, operator, execution setting, noise model,
benchmark, or acceptance policy therefore requires the independent benchmark,
benchmark, exact-local, and noisy-local artifacts to be regenerated.

For each observable, the principal numerical test is

```text
absolute_error <= absolute_tolerance + relative_tolerance * |benchmark_value|
```

The configured physical bounds and sign constraints are also required. IBM
results additionally require a standardized residual no greater than `3.0` for
each observable. These thresholds establish operational acceptance criteria
for this reduced experiment; they do not establish fidelity to a continuum
field theory. In particular, the noisy-tier tolerances are regression
guardrails for the declared local noise model, and the hardware standardized
residual is the absolute benchmark deviation divided by the reported estimator
uncertainty; it is not, by itself, a complete goodness-of-fit test for hardware
systematics. The hashes detect ordinary configuration and artifact drift but
are not digital signatures or a tamper-proof provenance system.

Hardware readiness can be checked without credentials, backend resolution, or
job submission:

```bash
python experiments/particle_creation_flrw/run_ibm.py --preflight-only
# or: make particle-preflight
```

This command reports the current lineage and the independent-benchmark,
exact-local, and noisy-local PASS results. It exits with an error if required
evidence is missing, stale, tampered, or outside policy.

The Phase 4 hardware workflow now also writes:

- processed IBM execution JSON under `data/processed/particle_creation_flrw/`,
- raw IBM metadata capture under `data/raw/particle_creation_flrw/`,
- a hardware report under `results/reports/particle_creation_flrw/`.

For credential-free infrastructure validation of the IBM wrapper itself, use local testing mode:

```bash
python experiments/particle_creation_flrw/run_ibm.py --local-testing-backend FakeManilaV2
```

Local testing mode is subject to the same local-evidence gate. It validates the
shared Runtime wrapper and provenance path, but it is not a real hardware
result.
