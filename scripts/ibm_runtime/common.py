"""Shared helpers for credential-safe IBM Runtime account operations."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any, Callable

DEFAULT_CHANNEL = "ibm_quantum_platform"
DEFAULT_TOKEN_ENV_VAR = "QISKIT_IBM_TOKEN"
DEFAULT_BACKEND_LIMIT = 5


@dataclass(frozen=True)
class IBMRuntimeCredentialSettings:
    """Resolved IBM Runtime credential settings from explicit inputs and environment."""

    token: str
    channel: str
    instance: str | None
    url: str | None


def saved_account_path() -> Path:
    """Return the default local Qiskit Runtime account path."""

    return Path.home() / ".qiskit" / "qiskit-ibm.json"


def load_runtime_credentials_from_environment(
    *,
    token_env_var: str = DEFAULT_TOKEN_ENV_VAR,
    channel: str | None = None,
    instance: str | None = None,
    url: str | None = None,
) -> IBMRuntimeCredentialSettings:
    """Resolve IBM Runtime credentials from the shell environment.

    The token is required and must be supplied through ``token_env_var``.
    Other fields fall back to standard Qiskit IBM Runtime environment variables
    where available.
    """

    token = os.environ.get(token_env_var)
    if token is None or not token.strip():
        raise ValueError(
            f"Environment variable {token_env_var!r} is required and must be non-empty."
        )
    resolved_channel = channel or os.environ.get("QISKIT_IBM_CHANNEL") or DEFAULT_CHANNEL
    resolved_instance = instance or os.environ.get("QISKIT_IBM_INSTANCE")
    resolved_url = url or os.environ.get("QISKIT_IBM_URL")
    return IBMRuntimeCredentialSettings(
        token=token.strip(),
        channel=resolved_channel.strip(),
        instance=None if resolved_instance is None else resolved_instance.strip(),
        url=None if resolved_url is None else resolved_url.strip(),
    )


def summarize_backend_names(service: Any, *, limit: int = DEFAULT_BACKEND_LIMIT) -> list[str]:
    """Return a stable, bounded list of backend names for diagnostics."""

    backend_names = sorted(str(backend.name) for backend in service.backends())
    return backend_names[: max(limit, 0)]


def save_runtime_account(
    *,
    token_env_var: str = DEFAULT_TOKEN_ENV_VAR,
    channel: str | None = None,
    instance: str | None = None,
    url: str | None = None,
    name: str | None = None,
    overwrite: bool = True,
    set_as_default: bool = True,
    service_cls: Any | None = None,
) -> dict[str, Any]:
    """Save an IBM Runtime account using shell-provided credentials only."""

    credentials = load_runtime_credentials_from_environment(
        token_env_var=token_env_var,
        channel=channel,
        instance=instance,
        url=url,
    )
    if service_cls is None:
        from qiskit_ibm_runtime import QiskitRuntimeService

        service_cls = QiskitRuntimeService
    service_cls.save_account(
        channel=credentials.channel,
        token=credentials.token,
        instance=credentials.instance,
        url=credentials.url,
        name=name,
        overwrite=overwrite,
        set_as_default=set_as_default,
    )
    return {
        "channel": credentials.channel,
        "has_instance": credentials.instance is not None,
        "has_url": credentials.url is not None,
        "name": name,
        "overwrite": overwrite,
        "set_as_default": set_as_default,
        "saved_account_path": str(saved_account_path()),
    }


def check_runtime_account(
    *,
    use_saved_account: bool = True,
    token_env_var: str = DEFAULT_TOKEN_ENV_VAR,
    channel: str | None = None,
    instance: str | None = None,
    url: str | None = None,
    backend_limit: int = DEFAULT_BACKEND_LIMIT,
    service_factory: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Validate access to IBM Runtime using a saved or environment-backed account."""

    if service_factory is None:
        from qiskit_ibm_runtime import QiskitRuntimeService

        service_factory = QiskitRuntimeService

    service_kwargs: dict[str, Any] = {}
    account_source = "saved"
    if not use_saved_account:
        credentials = load_runtime_credentials_from_environment(
            token_env_var=token_env_var,
            channel=channel,
            instance=instance,
            url=url,
        )
        service_kwargs = {
            "channel": credentials.channel,
            "token": credentials.token,
        }
        if credentials.instance is not None:
            service_kwargs["instance"] = credentials.instance
        if credentials.url is not None:
            service_kwargs["url"] = credentials.url
        account_source = "environment"

    service = service_factory(**service_kwargs)
    active_account = service.active_account()
    backend_names = summarize_backend_names(service, limit=backend_limit)
    backend_count = len(service.backends())
    return {
        "account_source": account_source,
        "channel": active_account.get("channel"),
        "has_instance": bool(active_account.get("instance")),
        "backend_count": backend_count,
        "sample_backends": backend_names,
        "saved_account_path": str(saved_account_path()),
    }

