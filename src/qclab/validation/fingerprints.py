"""Deterministic fingerprints for scientific validation lineage."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from typing import Any

from qclab.observables import ObservableDefinition
from qclab.utils.configuration import ModelConfiguration


def canonical_json(value: Any) -> str:
    """Return a deterministic JSON representation suitable for hashing."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def sha256_fingerprint(value: Any) -> str:
    """Return the SHA-256 digest of a canonical JSON payload."""

    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def model_payload(configuration: ModelConfiguration) -> dict[str, Any]:
    """Return the mathematical model content used for lineage."""

    payload: dict[str, Any] = {
        "experiment_name": configuration.experiment_name,
        "parameters": dict(configuration.parameters),
        "truncation": dict(configuration.truncation),
        "declared_observables": list(configuration.observables),
    }
    model_metadata = configuration.metadata.get("model")
    if model_metadata is not None:
        payload["model_metadata"] = model_metadata
    return payload


def model_fingerprint(configuration: ModelConfiguration) -> str:
    """Fingerprint the declared model, truncation, and observable names."""

    return sha256_fingerprint(model_payload(configuration))


def configuration_payload(configuration: ModelConfiguration) -> dict[str, Any]:
    """Return execution and validation settings that affect artifact currency.

    Artifact locations and narrative notes are deliberately excluded. Moving a
    result file does not change its scientific content, while changing an
    execution or validation policy does require renewed validation.
    """

    execution = {
        tier.value: {
            "enabled": settings.enabled,
            "backend_name": settings.backend_name,
            "shots": settings.shots,
            "seed": settings.seed,
            "precision": settings.precision,
            "optimization_level": settings.optimization_level,
            "options": dict(settings.options),
        }
        for tier, settings in sorted(
            configuration.execution.items(), key=lambda item: item[0].value
        )
    }
    return {
        "model": model_payload(configuration),
        "execution": execution,
        "noise_model": configuration.metadata.get("noise_model"),
        "validation": configuration.metadata.get("validation"),
    }


def configuration_fingerprint(configuration: ModelConfiguration) -> str:
    """Fingerprint model-adjacent execution and validation configuration."""

    return sha256_fingerprint(configuration_payload(configuration))


def observable_payload(
    observables: Sequence[ObservableDefinition],
) -> list[dict[str, Any]]:
    """Return the mathematically relevant content of declared observables."""

    payload: list[dict[str, Any]] = []
    for observable in sorted(observables, key=lambda item: item.name):
        payload.append(
            {
                "name": observable.name,
                "operator_label": observable.operator_label,
                "measurement_basis": observable.measurement_basis,
                "units": observable.units,
                "pauli_terms": [
                    {
                        "label": term.label,
                        "coefficient": {
                            "real": float(complex(term.coefficient).real),
                            "imag": float(complex(term.coefficient).imag),
                        },
                    }
                    for term in sorted(
                        observable.pauli_terms,
                        key=lambda term: (
                            term.label,
                            complex(term.coefficient).real,
                            complex(term.coefficient).imag,
                        ),
                    )
                ],
                "metadata": dict(observable.metadata),
            }
        )
    return payload


def observable_fingerprint(
    observables: Sequence[ObservableDefinition],
) -> str:
    """Fingerprint observable operators and encoding metadata."""

    return sha256_fingerprint(observable_payload(observables))


def benchmark_fingerprint(benchmark_payload: Mapping[str, Any]) -> str:
    """Fingerprint the complete benchmark payload before lineage is attached."""

    sanitized_payload = dict(benchmark_payload)
    sanitized_payload.pop("validation_context", None)
    return sha256_fingerprint(sanitized_payload)


def lineage_fingerprint(
    *,
    configuration_digest: str,
    model_digest: str,
    observable_digest: str,
    benchmark_digest: str,
) -> str:
    """Combine component fingerprints into one validation-lineage identifier."""

    return sha256_fingerprint(
        {
            "configuration_fingerprint": configuration_digest,
            "model_fingerprint": model_digest,
            "observable_fingerprint": observable_digest,
            "benchmark_fingerprint": benchmark_digest,
        }
    )
