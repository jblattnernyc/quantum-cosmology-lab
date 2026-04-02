"""Configuration loading and validation for experiment metadata."""

from __future__ import annotations

from collections.abc import Mapping
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from qclab.backends.base import ExecutionTier


@dataclass(frozen=True)
class ExecutionConfiguration:
    """Execution settings for a single execution tier."""

    enabled: bool = False
    backend_name: str | None = None
    shots: int | None = None
    seed: int | None = None
    precision: float | None = None
    optimization_level: int | None = None
    options: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.shots is not None and self.shots <= 0:
            raise ValueError("ExecutionConfiguration.shots must be positive when set.")
        if self.precision is not None and self.precision < 0:
            raise ValueError(
                "ExecutionConfiguration.precision must be non-negative when set."
            )
        if self.optimization_level is not None and self.optimization_level < 0:
            raise ValueError(
                "ExecutionConfiguration.optimization_level must be non-negative when set."
            )


@dataclass(frozen=True)
class ModelConfiguration:
    """Structured experiment configuration metadata."""

    experiment_name: str
    scientific_question: str
    status: str = "unspecified"
    official_experiment: bool = False
    parameters: dict[str, Any] = field(default_factory=dict)
    truncation: dict[str, Any] = field(default_factory=dict)
    observables: tuple[str, ...] = ()
    execution: dict[ExecutionTier, ExecutionConfiguration] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.experiment_name.strip():
            raise ValueError("ModelConfiguration.experiment_name must be non-empty.")
        if not self.scientific_question.strip():
            raise ValueError("ModelConfiguration.scientific_question must be non-empty.")
        if any(not observable.strip() for observable in self.observables):
            raise ValueError("Observable names in ModelConfiguration must be non-empty.")

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any]) -> "ModelConfiguration":
        """Create a configuration object from a parsed mapping."""

        configuration = cls(
            experiment_name=str(mapping["experiment_name"]),
            scientific_question=str(mapping["scientific_question"]),
            status=str(mapping.get("status", "unspecified")),
            official_experiment=bool(mapping.get("official_experiment", False)),
            parameters=dict(mapping.get("parameters", {})),
            truncation=dict(mapping.get("truncation", {})),
            observables=tuple(str(item) for item in mapping.get("observables", ())),
            execution=_normalize_execution_mapping(mapping.get("execution", {})),
            metadata={
                key: value
                for key, value in mapping.items()
                if key
                not in {
                    "experiment_name",
                    "scientific_question",
                    "status",
                    "official_experiment",
                    "parameters",
                    "truncation",
                    "observables",
                    "execution",
                }
            },
        )
        validate_model_configuration(configuration)
        return configuration

    def execution_for_tier(self, tier: ExecutionTier) -> ExecutionConfiguration:
        """Return the configuration for the requested execution tier."""

        return self.execution.get(tier, ExecutionConfiguration())


def _coerce_execution_configuration(value: Mapping[str, Any] | None) -> ExecutionConfiguration:
    """Normalize raw execution-tier settings into an ``ExecutionConfiguration``."""

    if value is None:
        return ExecutionConfiguration()
    if not isinstance(value, Mapping):
        raise TypeError("Each execution-tier configuration must be a mapping.")
    return ExecutionConfiguration(
        enabled=bool(value.get("enabled", False)),
        backend_name=(
            None if value.get("backend_name") is None else str(value.get("backend_name"))
        ),
        shots=None if value.get("shots") is None else int(value.get("shots")),
        seed=None if value.get("seed") is None else int(value.get("seed")),
        precision=(
            None if value.get("precision") is None else float(value.get("precision"))
        ),
        optimization_level=(
            None
            if value.get("optimization_level") is None
            else int(value.get("optimization_level"))
        ),
        options=dict(value.get("options", {})),
    )


def _normalize_execution_mapping(
    raw_execution: Mapping[str, Any] | None,
) -> dict[ExecutionTier, ExecutionConfiguration]:
    """Normalize raw execution configuration into tier-keyed settings."""

    if raw_execution is None:
        raw_execution = {}
    if not isinstance(raw_execution, Mapping):
        raise TypeError("The top-level execution configuration must be a mapping.")
    return {
        tier: _coerce_execution_configuration(raw_execution.get(tier.value))
        for tier in ExecutionTier
    }


def validate_model_configuration(configuration: ModelConfiguration) -> None:
    """Validate structural expectations for a model configuration."""

    if not isinstance(configuration.parameters, dict):
        raise TypeError("ModelConfiguration.parameters must be a mapping.")
    if not isinstance(configuration.truncation, dict):
        raise TypeError("ModelConfiguration.truncation must be a mapping.")
    if configuration.official_experiment:
        if not configuration.observables:
            raise ValueError(
                "Official experiments must declare at least one observable in configuration."
            )
        if not configuration.truncation:
            raise ValueError(
                "Official experiments must declare an explicit truncation in configuration."
            )
        if not configuration.execution_for_tier(ExecutionTier.EXACT_LOCAL).enabled:
            raise ValueError(
                "Official experiments must enable the exact_local execution tier."
            )
        if not configuration.execution_for_tier(ExecutionTier.NOISY_LOCAL).enabled:
            raise ValueError(
                "Official experiments must enable the noisy_local execution tier."
            )


def validate_configuration_mapping(mapping: Mapping[str, Any]) -> ModelConfiguration:
    """Validate a raw configuration mapping and return a typed configuration."""

    if not isinstance(mapping, Mapping):
        raise TypeError("Configuration content must be a mapping.")
    return ModelConfiguration.from_mapping(dict(mapping))


def default_execution_mapping() -> dict[str, dict[str, Any]]:
    """Return a serializable default execution mapping for experiment templates."""

    return {
        tier.value: {
            "enabled": False,
            "backend_name": None,
            "shots": None,
            "seed": None,
            "precision": None,
            "optimization_level": None,
            "options": {},
        }
        for tier in ExecutionTier
    }


def _load_mapping(path: Path) -> dict[str, Any]:
    """Load YAML if available, otherwise fall back to JSON-compatible YAML."""

    text = path.read_text(encoding="utf-8")
    try:
        import yaml
    except ModuleNotFoundError:
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise TypeError(f"Configuration file must define a mapping: {path}")
    return data


def load_model_configuration(path: str | Path) -> ModelConfiguration:
    """Load and validate a model configuration from a path."""

    resolved_path = Path(path).expanduser().resolve()
    return validate_configuration_mapping(_load_mapping(resolved_path))
