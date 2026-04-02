"""Plot styling helpers for analysis outputs."""

from qclab.plotting.backend import configure_noninteractive_backend
from qclab.plotting.comparison import plot_scalar_comparison
from qclab.plotting.style import apply_publication_style, publication_style

__all__ = [
    "apply_publication_style",
    "configure_noninteractive_backend",
    "plot_scalar_comparison",
    "publication_style",
]
