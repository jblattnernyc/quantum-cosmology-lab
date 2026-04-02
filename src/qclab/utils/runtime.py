"""Platform-sensitive runtime guards for local validation workflows."""

from __future__ import annotations

import platform
import sys


_AER_GUARDED_MINIMUM_VERSION = (3, 13)


def is_aer_execution_guard_required() -> bool:
    """Return whether local Aer-backed execution is guarded on this host."""

    return (
        platform.system() == "Darwin"
        and platform.machine() == "arm64"
        and sys.version_info >= _AER_GUARDED_MINIMUM_VERSION
    )


def aer_execution_guard_message(context: str) -> str:
    """Return the shared explanation for the local Aer runtime guard."""

    return (
        f"{context} is guarded on macOS arm64 with Python 3.13+ because the "
        "installed qiskit-aer runtime aborts during OpenMP shared-memory "
        "initialization (`OMP: Error #178: Function Can't open SHM2 failed`). "
        "This repository treats the condition as a local runtime constraint "
        "rather than as a scientific failure of the benchmarked workflow. Use "
        "Python 3.10-3.12 for local Aer-backed validation on Apple Silicon, or "
        "skip Aer-backed validation tiers on this host."
    )


def guard_aer_execution(context: str) -> None:
    """Raise a precise error before entering a guarded Aer-backed path."""

    if is_aer_execution_guard_required():
        raise RuntimeError(aer_execution_guard_message(context))
