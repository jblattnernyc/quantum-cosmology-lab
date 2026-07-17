"""Classification helpers for persisted validation lineage."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

from qclab.validation.records import ValidationContext


class ArtifactLineageStatus(str, Enum):
    """Relationship between a persisted artifact and the current lineage."""

    CURRENT = "current"
    STALE = "stale"
    LEGACY_UNBOUND = "legacy_unbound"
    INVALID = "invalid"


@dataclass(frozen=True)
class ArtifactLineageClassification:
    """Structured result of inspecting an artifact validation context."""

    status: ArtifactLineageStatus
    artifact_context: ValidationContext | None = None
    reason: str | None = None

    def to_serializable(self) -> dict[str, Any]:
        """Return a JSON-safe classification record."""

        return {
            "status": self.status.value,
            "artifact_context": (
                None
                if self.artifact_context is None
                else self.artifact_context.to_serializable()
            ),
            "reason": self.reason,
        }


def classify_artifact_lineage(
    payload: Mapping[str, Any],
    current_context: ValidationContext,
) -> ArtifactLineageClassification:
    """Classify an artifact without treating legacy evidence as current.

    This helper is descriptive rather than permissive. The hardware gate still
    requires an exactly matching, valid context; analysis workflows may use
    this classification to report why historical evidence is ineligible.
    """

    if "validation_context" not in payload:
        return ArtifactLineageClassification(
            status=ArtifactLineageStatus.LEGACY_UNBOUND,
            reason="Artifact predates validation-lineage binding.",
        )
    raw_context = payload.get("validation_context")
    if not isinstance(raw_context, dict):
        return ArtifactLineageClassification(
            status=ArtifactLineageStatus.INVALID,
            reason="validation_context is not a JSON object.",
        )
    try:
        artifact_context = ValidationContext.from_mapping(raw_context)
    except ValueError as exc:
        return ArtifactLineageClassification(
            status=ArtifactLineageStatus.INVALID,
            reason=str(exc),
        )
    if artifact_context == current_context:
        return ArtifactLineageClassification(
            status=ArtifactLineageStatus.CURRENT,
            artifact_context=artifact_context,
        )
    return ArtifactLineageClassification(
        status=ArtifactLineageStatus.STALE,
        artifact_context=artifact_context,
        reason="Artifact lineage does not match the current configuration.",
    )
