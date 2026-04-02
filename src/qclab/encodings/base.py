"""Definitions for qubit encodings and operator mappings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EncodingSpecification:
    """Documented mapping from reduced degrees of freedom to qubits."""

    name: str
    degrees_of_freedom: tuple[str, ...]
    qubit_count: int
    mapping_summary: str
    basis_convention: str
    metadata: dict[str, Any] = field(default_factory=dict)
