"""Pauli-based observable construction utilities."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from qclab.observables.base import ObservableDefinition, PauliTerm
from qclab.utils.optional import require_dependency


PauliTermInput = PauliTerm | str | tuple[str, complex]


def _coerce_pauli_term(term: PauliTermInput) -> PauliTerm:
    """Normalize Pauli-term inputs into a ``PauliTerm`` instance."""

    if isinstance(term, PauliTerm):
        return term
    if isinstance(term, str):
        return PauliTerm(label=term, coefficient=1.0)
    if isinstance(term, tuple) and len(term) == 2:
        label, coefficient = term
        return PauliTerm(label=str(label), coefficient=complex(coefficient))
    raise TypeError(
        "Pauli terms must be provided as PauliTerm, str, or (label, coefficient) tuples."
    )


def pauli_terms_from_mapping(term_mapping: Mapping[str, complex]) -> tuple[PauliTerm, ...]:
    """Create a canonical ordered tuple of Pauli terms from a mapping."""

    return tuple(
        PauliTerm(label=label, coefficient=complex(coefficient))
        for label, coefficient in term_mapping.items()
    )


def make_pauli_observable(
    *,
    name: str,
    terms: Mapping[str, complex] | Iterable[PauliTermInput],
    physical_meaning: str,
    measurement_basis: str = "pauli",
    units: str = "dimensionless",
    metadata: dict[str, Any] | None = None,
) -> ObservableDefinition:
    """Construct an observable from an explicit Pauli decomposition."""

    pauli_terms: tuple[PauliTerm, ...]
    if isinstance(terms, Mapping):
        pauli_terms = pauli_terms_from_mapping(terms)
    else:
        pauli_terms = tuple(_coerce_pauli_term(term) for term in terms)
    if not pauli_terms:
        raise ValueError("At least one Pauli term is required to define an observable.")
    operator_label = " + ".join(
        f"{term.coefficient}*{term.label}" for term in pauli_terms
    )
    return ObservableDefinition(
        name=name,
        operator_label=operator_label,
        physical_meaning=physical_meaning,
        measurement_basis=measurement_basis,
        units=units,
        pauli_terms=pauli_terms,
        metadata={} if metadata is None else dict(metadata),
    )


def infer_pauli_qubit_count(observable: ObservableDefinition) -> int | None:
    """Infer the qubit count for a Pauli-based observable if possible."""

    if observable.pauli_terms:
        return len(observable.pauli_terms[0].label)
    label = observable.operator_label.strip().upper()
    if label and all(symbol in {"I", "X", "Y", "Z"} for symbol in label):
        return len(label)
    return None


def observable_to_qiskit(observable: ObservableDefinition) -> Any:
    """Convert an observable definition into a Qiskit-compatible payload.

    Primitive APIs accept several observable formats, including strings and
    ``SparsePauliOp`` objects. Single-term unit-coefficient Pauli observables
    are therefore returned as plain strings to avoid unnecessary dependency
    work. Multi-term observables are converted lazily to ``SparsePauliOp``.
    """

    if observable.pauli_terms:
        if len(observable.pauli_terms) == 1 and observable.pauli_terms[0].coefficient == 1:
            return observable.pauli_terms[0].label
        quantum_info = require_dependency(
            "qiskit.quantum_info",
            "convert multi-term Pauli observables into SparsePauliOp objects",
        )
        sparse_pauli_op = quantum_info.SparsePauliOp
        return sparse_pauli_op.from_list(
            [(term.label, term.coefficient) for term in observable.pauli_terms]
        )
    return observable.operator_label


def coerce_observable_sequence(
    observables: ObservableDefinition | Sequence[ObservableDefinition],
) -> tuple[ObservableDefinition, ...]:
    """Normalize one or more observables into a tuple."""

    if isinstance(observables, ObservableDefinition):
        return (observables,)
    normalized = tuple(observables)
    if not normalized:
        raise ValueError("At least one observable must be provided.")
    return normalized
