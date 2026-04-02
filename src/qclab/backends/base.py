"""Backend execution policy for exact, noisy, and hardware tiers."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExecutionTier(str, Enum):
    """Required execution tiers for official lab experiments."""

    EXACT_LOCAL = "exact_local"
    NOISY_LOCAL = "noisy_local"
    IBM_HARDWARE = "ibm_hardware"


@dataclass(frozen=True)
class BackendRequest:
    """Requested execution settings for a backend run."""

    tier: ExecutionTier
    backend_name: str
    shots: int | None = None
    seed: int | None = None
    mitigation_enabled: bool = False
    precision: float | None = None
    optimization_level: int | None = None
    options: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.backend_name.strip():
            raise ValueError("BackendRequest.backend_name must be non-empty.")
        if self.shots is not None and self.shots <= 0:
            raise ValueError("BackendRequest.shots must be positive when set.")
        if self.precision is not None and self.precision < 0:
            raise ValueError("BackendRequest.precision must be non-negative when set.")
        if self.optimization_level is not None and self.optimization_level < 0:
            raise ValueError(
                "BackendRequest.optimization_level must be non-negative when set."
            )


@dataclass(frozen=True)
class BackendAvailability:
    """Detected local availability for an execution tier."""

    tier: ExecutionTier
    available: bool
    detail: str


def _has_module(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def detect_backend_availability() -> tuple[BackendAvailability, ...]:
    """Inspect whether the declared backend dependencies appear importable."""

    return (
        BackendAvailability(
            tier=ExecutionTier.EXACT_LOCAL,
            available=_has_module("qiskit"),
            detail="Requires qiskit for exact local primitives or statevector workflows.",
        ),
        BackendAvailability(
            tier=ExecutionTier.NOISY_LOCAL,
            available=_has_module("qiskit_aer"),
            detail="Requires qiskit-aer for noisy local simulation workflows.",
        ),
        BackendAvailability(
            tier=ExecutionTier.IBM_HARDWARE,
            available=_has_module("qiskit_ibm_runtime"),
            detail="Requires qiskit-ibm-runtime for IBM Runtime execution.",
        ),
    )


def validate_execution_progression(
    requested_tier: ExecutionTier,
    *,
    benchmark_complete: bool,
    exact_local_complete: bool = False,
    noisy_local_complete: bool = False,
) -> None:
    """Enforce the lab's benchmark-before-hardware execution policy."""

    if requested_tier is ExecutionTier.EXACT_LOCAL and not benchmark_complete:
        raise ValueError(
            "Exact local execution should follow an explicit benchmark or "
            "trusted reference definition."
        )
    if requested_tier is ExecutionTier.NOISY_LOCAL and not benchmark_complete:
        raise ValueError(
            "Noisy local execution is not permitted before the benchmark tier "
            "has been defined."
        )
    if requested_tier is ExecutionTier.IBM_HARDWARE:
        if not benchmark_complete:
            raise ValueError("IBM hardware execution requires a completed benchmark tier.")
        if not exact_local_complete:
            raise ValueError(
                "IBM hardware execution requires completed exact local validation."
            )
        if not noisy_local_complete:
            raise ValueError(
                "IBM hardware execution requires completed noisy local validation."
            )
