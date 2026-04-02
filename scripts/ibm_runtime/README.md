# IBM Runtime Helper Scripts

This directory contains credential-safe operational helpers for IBM Runtime setup and validation.

These scripts are intended to support repository use without placing API tokens, instance identifiers, or other account secrets into tracked source files.

## Scripts

- `save_account_from_env.py`: save an IBM Runtime account from shell environment variables.
- `check_account.py`: validate IBM Runtime connectivity using either the saved local account or environment-provided credentials.

## Expected Environment Variables

The helpers follow the same environment-variable conventions documented in [ibm-runtime-setup.md](../../docs/operations/ibm-runtime-setup.md):

- `QISKIT_IBM_TOKEN`
- `QISKIT_IBM_CHANNEL`
- `QISKIT_IBM_INSTANCE`
- `QISKIT_IBM_URL`

`QISKIT_IBM_TOKEN` is required when saving an account or when explicitly validating from the shell environment.

## Example Usage

```bash
export QISKIT_IBM_TOKEN='<token>'
export QISKIT_IBM_CHANNEL='ibm_quantum_platform'
export QISKIT_IBM_INSTANCE='<instance-crn>'

python scripts/ibm_runtime/save_account_from_env.py
python scripts/ibm_runtime/check_account.py
python scripts/ibm_runtime/check_account.py --use-env-account
```

These scripts print only non-secret summaries. They do not print the token value.
