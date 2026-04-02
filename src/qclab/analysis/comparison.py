"""Utilities for disciplined numerical comparison."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ComparisonRecord:
    """Scalar comparison between a benchmark and a candidate value."""

    observable_name: str
    benchmark_value: float
    candidate_value: float
    absolute_error: float
    relative_error: float | None
    interpretation: str


def compare_scalar_observable(
    *,
    observable_name: str,
    benchmark_value: float,
    candidate_value: float,
    interpretation: str,
) -> ComparisonRecord:
    """Compare two scalar values with explicit numerical error reporting."""

    absolute_error = abs(candidate_value - benchmark_value)
    relative_error = None
    if benchmark_value != 0:
        relative_error = absolute_error / abs(benchmark_value)
    return ComparisonRecord(
        observable_name=observable_name,
        benchmark_value=benchmark_value,
        candidate_value=candidate_value,
        absolute_error=absolute_error,
        relative_error=relative_error,
        interpretation=interpretation,
    )


def comparison_records_to_rows(
    records: tuple[ComparisonRecord, ...] | list[ComparisonRecord],
) -> list[dict[str, float | str | None]]:
    """Convert comparison records into row dictionaries."""

    return [asdict(record) for record in records]


def comparison_within_tolerance(
    record: ComparisonRecord,
    *,
    absolute_tolerance: float | None = None,
    relative_tolerance: float | None = None,
) -> bool:
    """Return whether a comparison record satisfies the declared tolerances."""

    if absolute_tolerance is not None and record.absolute_error > absolute_tolerance:
        return False
    if (
        relative_tolerance is not None
        and record.relative_error is not None
        and record.relative_error > relative_tolerance
    ):
        return False
    return True
