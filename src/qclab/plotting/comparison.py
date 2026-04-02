"""Plotting helpers for scalar benchmark comparisons."""

from __future__ import annotations

from collections.abc import Sequence

from qclab.analysis.comparison import ComparisonRecord
from qclab.plotting.style import apply_publication_style
from qclab.utils.optional import require_dependency


def plot_scalar_comparison(
    records: Sequence[ComparisonRecord],
    *,
    title: str | None = None,
):
    """Create a simple benchmark-versus-candidate comparison figure."""

    pyplot = require_dependency(
        "matplotlib.pyplot",
        "plot scalar comparison figures",
    )
    apply_publication_style()
    labels = [record.observable_name for record in records]
    benchmark_values = [record.benchmark_value for record in records]
    candidate_values = [record.candidate_value for record in records]
    figure, axis = pyplot.subplots(figsize=(7, 4))
    positions = list(range(len(records)))
    width = 0.38
    axis.bar(
        [position - width / 2 for position in positions],
        benchmark_values,
        width=width,
        label="Benchmark",
    )
    axis.bar(
        [position + width / 2 for position in positions],
        candidate_values,
        width=width,
        label="Candidate",
    )
    axis.set_xticks(positions, labels, rotation=20)
    axis.set_ylabel("Value")
    axis.legend()
    if title:
        axis.set_title(title)
    return figure, axis
