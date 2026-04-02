"""Generic circuit metadata used by shared lab infrastructure."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CircuitArtifact:
    """Structured description of a circuit construction result."""

    name: str
    qubit_count: int
    parameter_values: dict[str, float]
    construction_summary: str
    payload: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
