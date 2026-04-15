"""Credential-safe helpers for backend provenance metadata."""

from __future__ import annotations

from typing import Any


REDACTED_RUNTIME_INSTANCE = "configured-redacted"


def runtime_instance_configured(instance: Any) -> bool:
    """Return whether an IBM Runtime instance identifier is present."""

    return isinstance(instance, str) and bool(instance.strip())


def redact_runtime_instance(instance: Any) -> str | None:
    """Return a non-secret placeholder for an IBM Runtime instance identifier."""

    if runtime_instance_configured(instance):
        return REDACTED_RUNTIME_INSTANCE
    return None
