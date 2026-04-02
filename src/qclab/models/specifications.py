"""Model-level scientific specifications used across the lab."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TruncationSpecification:
    """Explicit truncation data for reduced Hilbert-space constructions."""

    basis_name: str
    cutoff: int
    rationale: str
    assumptions: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ModelSpecification:
    """Named scientific model with explicit approximation metadata."""

    name: str
    scientific_question: str
    model_statement: str
    approximation_scheme: str
    parameters: dict[str, Any]
    truncation: TruncationSpecification
    references: tuple[str, ...] = ()
    exploratory: bool = True
