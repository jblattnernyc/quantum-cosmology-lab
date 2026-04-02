"""Helpers for optional scientific dependencies."""

from __future__ import annotations

import importlib


def require_dependency(module_name: str, purpose: str):
    """Import a dependency lazily and raise a precise error if unavailable."""

    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            f"The optional dependency '{module_name}' is required to {purpose}. "
            "Install the project dependencies declared in pyproject.toml first."
        ) from exc
