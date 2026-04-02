"""Matplotlib backend helpers for non-interactive repository workflows."""

from __future__ import annotations

import os
import sys


def configure_noninteractive_backend() -> None:
    """Prefer a file-writing backend for repository analysis scripts.

    The official analysis workflows persist figures to disk and do not require a
    GUI backend. An explicit ``MPLBACKEND`` environment override is respected.
    """

    if os.environ.get("MPLBACKEND"):
        return
    if "matplotlib.pyplot" in sys.modules:
        return
    import matplotlib

    matplotlib.use("Agg")
