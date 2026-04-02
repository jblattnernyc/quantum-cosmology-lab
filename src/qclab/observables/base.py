"""Observable definitions for scientifically interpretable measurements."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PauliTerm:
    """Single Pauli-string term in an observable decomposition."""

    label: str
    coefficient: complex = 1.0

    def __post_init__(self) -> None:
        normalized_label = self.label.strip().upper()
        if not normalized_label:
            raise ValueError("PauliTerm.label must be non-empty.")
        if any(symbol not in {"I", "X", "Y", "Z"} for symbol in normalized_label):
            raise ValueError(
                "PauliTerm.label must contain only I, X, Y, and Z characters."
            )
        object.__setattr__(self, "label", normalized_label)


@dataclass(frozen=True)
class ObservableDefinition:
    """A declared observable together with its physical interpretation."""

    name: str
    operator_label: str
    physical_meaning: str
    measurement_basis: str
    units: str = "dimensionless"
    pauli_terms: tuple[PauliTerm, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("ObservableDefinition.name must be non-empty.")
        if not self.operator_label.strip():
            raise ValueError("ObservableDefinition.operator_label must be non-empty.")
        if not self.measurement_basis.strip():
            raise ValueError("ObservableDefinition.measurement_basis must be non-empty.")
        if self.pauli_terms:
            qubit_counts = {len(term.label) for term in self.pauli_terms}
            if len(qubit_counts) != 1:
                raise ValueError(
                    "All Pauli terms in an observable must act on the same number of qubits."
                )


@dataclass(frozen=True)
class ObservableEvaluation:
    """Numeric record for a single observable estimate."""

    observable: ObservableDefinition
    value: float
    uncertainty: float = 0.0
    shots: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.uncertainty < 0:
            raise ValueError("ObservableEvaluation.uncertainty must be non-negative.")
