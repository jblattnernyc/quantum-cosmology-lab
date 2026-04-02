# IBM Runtime Setup

## Purpose

This document defines the operational policy for using IBM Runtime within the Quantum Cosmology Lab repository.

The repository permits IBM Runtime execution only as the third execution tier, after benchmark construction, exact-local validation, and noisy-local validation. Hardware access is therefore an optional operational capability, not the starting point of a scientific workflow.

## Prerequisites

Before using IBM Runtime from this repository:

1. Install the repository with the declared scientific dependencies.
2. Confirm that the target experiment already has:
   - an exact or trusted benchmark,
   - a completed exact-local validation artifact,
   - a completed noisy-local validation artifact.
3. Confirm that the experiment documentation identifies the observable to be measured and the limits of interpretation.

## Credential Policy

Credentials must never be committed into tracked source files.

Use one of the credential mechanisms supported by `QiskitRuntimeService`, such as:

- a local saved account managed by Qiskit Runtime,
- environment variables read by the installed client,
- explicit runtime-service arguments supplied outside tracked files.

For the currently installed `qiskit-ibm-runtime` client in this environment, the package source recognizes environment variables including:

- `QISKIT_IBM_CHANNEL`
- `QISKIT_IBM_TOKEN`
- `QISKIT_IBM_URL`
- `QISKIT_IBM_INSTANCE`

These values should be set in the shell environment or local credential store, not hard-coded in repository files.

For repository-local operational convenience, credential-safe helper scripts are also provided under [scripts/ibm_runtime/README.md](../../scripts/ibm_runtime/README.md). These helpers save and validate IBM Runtime accounts from environment variables without embedding tokens in tracked source.

## Repository Helper Workflow

The recommended repository-local account workflow is:

```bash
export QISKIT_IBM_TOKEN='<token>'
export QISKIT_IBM_CHANNEL='ibm_quantum_platform'
export QISKIT_IBM_INSTANCE='<instance-crn>'

python scripts/ibm_runtime/save_account_from_env.py
python scripts/ibm_runtime/check_account.py
```

If the saved local account state is suspected to be stale, the same validation can be run directly against the shell environment without relying on the saved account file:

```bash
python scripts/ibm_runtime/check_account.py --use-env-account
```

These helpers print only non-secret summaries such as channel, whether an instance is configured, and a short backend list.

The repository-standard live submission sequence itself is documented in the `IBM Hardware Validation and Execution Procedure` section of [user-guide.md](user-guide.md).

## Repository Usage Pattern

The repository backend wrapper in [execution.py](../../src/qclab/backends/execution.py) uses `qiskit_ibm_runtime.EstimatorV2` together with `QiskitRuntimeService`, the shared backend-selection and mitigation-policy helpers in [hardware.py](../../src/qclab/backends/hardware.py), and backend-aware local transpilation to ISA-compatible circuits and observables.

Operational expectations are:

1. Select the backend through a documented `BackendRequest`.
2. Keep mitigation settings explicit through the shared mitigation-policy configuration.
3. Preserve run provenance, including backend selection policy, mitigation policy, calibration summary, job identifier, timestamp, and runtime metadata.
4. Write serialized run records, metadata JSON, and a hardware report to disk using the shared helpers.
5. Preserve completed live IBM hardware runs automatically through timestamped archive copies and a JSON Lines run manifest, while leaving local-testing-mode runs unarchived by default and routed to separate `_local_testing` artifact paths.

## Backend Selection

Backend choice should be documented per experiment. The repository does not assume that any available backend is scientifically appropriate.

The Phase 4 shared framework supports two backend-selection strategies:

- `explicit`: require a named backend and treat that name as part of the run provenance.
- `least_busy`: use `QiskitRuntimeService.least_busy(...)` with explicit filter criteria such as minimum qubit count and simulator exclusion.

The repository configuration defaults to explicit selection for the implemented official lines. Least-busy selection is supported when a dated operational reason justifies it, but the filter criteria used for the selection must remain part of the recorded metadata.

In practice:

- prefer `explicit` selection for benchmarked comparison work, replication across dates, or any case where backend identity itself is part of the provenance record;
- consider `least_busy` selection only when queue conditions or temporary backend availability make a single fixed backend operationally impractical, and record the selection date together with the filters used;
- do not use `least_busy` as a substitute for documenting hardware choice. It is an operational fallback, not a scientific rationale.

When choosing a backend, document:

- backend name,
- date of execution,
- shot count or precision target,
- mitigation settings,
- any relevant instance or channel context,
- whether selection was explicit or least-busy,
- any minimum-qubit or operational filters used.

## Mitigation Policy

The Phase 4 shared framework keeps mitigation policy explicit and inspectable. The repository currently supports:

- resilience level `0`: no mitigation,
- resilience level `1`: minimal mitigation cost, suitable for measurement-mitigation-first workflows,
- resilience level `2`: higher-cost mitigation when explicitly justified.

The shared configuration layer can also record specific toggles such as measurement mitigation, measurement twirling, gate twirling, and dynamical decoupling. These settings are treated as operational controls rather than as claims about physical signal recovery.

Mitigation settings should therefore always be recorded together with:

- the requested resilience level,
- any explicit sub-options,
- the selected backend,
- the benchmark and prior-tier comparison context.

## Local Testing Mode

When credentials or hardware access are unavailable, the repository may validate the IBM Runtime wrapper through IBM Runtime local testing mode using fake backends from `qiskit_ibm_runtime.fake_provider`.

This local-testing path is appropriate for:

- validating the shared wrapper,
- validating backend-aware transpilation,
- validating report and metadata generation,
- smoke-testing the experiment `run_ibm.py` entry points.

It is not a substitute for a real hardware run and must not be presented as one.

## Logging and Reproducibility

If IBM Runtime logging is required, the installed client also exposes logging-related environment variables such as:

- `QISKIT_IBM_RUNTIME_LOG_LEVEL`
- `QISKIT_IBM_RUNTIME_LOG_FILE`

These may be useful for debugging operational failures, but they should not substitute for experiment-level provenance capture in repository outputs.

For local transpilation reproducibility, the shared wrapper also records the configured optimization level and can pass a transpiler seed when one is provided in the experiment execution request.

## Scientific Restraint

A successful IBM Runtime job is not, by itself, a scientific result. Repository interpretation remains subordinate to benchmark agreement, observable definition, and explicit written analysis.
