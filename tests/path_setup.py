"""Helpers for ensuring the local src layout is importable during tests."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_src_path() -> None:
    """Insert the repository's src directory into sys.path if required."""

    src_path = Path(__file__).resolve().parents[1] / "src"
    src_path_string = str(src_path)
    if src_path_string not in sys.path:
        sys.path.insert(0, src_path_string)
