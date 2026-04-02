"""Common plotting defaults for lab reports and figures."""

from __future__ import annotations


def publication_style() -> dict[str, object]:
    """Return a conservative matplotlib style for analytical figures."""

    return {
        "axes.grid": True,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "figure.dpi": 120,
        "legend.frameon": False,
        "lines.linewidth": 1.8,
        "savefig.bbox": "tight",
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    }


def apply_publication_style() -> None:
    """Apply the lab plotting style to matplotlib rcParams."""

    import matplotlib as mpl

    mpl.rcParams.update(publication_style())
