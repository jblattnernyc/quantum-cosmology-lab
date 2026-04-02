"""Configuration-loading tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.path_setup import ensure_src_path

ensure_src_path()

from qclab.backends.base import ExecutionTier
from qclab.utils.configuration import load_model_configuration, validate_configuration_mapping


class ConfigurationLoaderTests(unittest.TestCase):
    """Verify the shared configuration loader."""

    def test_json_compatible_yaml_loads_without_optional_yaml_parser(self) -> None:
        configuration_text = """
{
  "experiment_name": "foundation_example",
  "scientific_question": "Does the shared configuration loader preserve explicit metadata?",
  "parameters": {"theta": 0.5},
  "truncation": {"basis": "toy", "cutoff": 2},
  "observables": ["toy_pauli_z_expectation"],
  "execution": {"exact_local": {"enabled": true, "optimization_level": 1}},
  "status": "scaffold"
}
""".strip()
        with tempfile.TemporaryDirectory() as temp_dir:
            configuration_path = Path(temp_dir) / "config.yaml"
            configuration_path.write_text(configuration_text, encoding="utf-8")
            configuration = load_model_configuration(configuration_path)

        self.assertEqual(configuration.experiment_name, "foundation_example")
        self.assertEqual(configuration.status, "scaffold")
        self.assertEqual(configuration.parameters["theta"], 0.5)
        self.assertEqual(configuration.truncation["cutoff"], 2)
        self.assertEqual(configuration.observables, ("toy_pauli_z_expectation",))
        self.assertTrue(configuration.execution[ExecutionTier.EXACT_LOCAL].enabled)
        self.assertEqual(
            configuration.execution[ExecutionTier.EXACT_LOCAL].optimization_level,
            1,
        )
        self.assertFalse(configuration.official_experiment)

    def test_official_configuration_requires_exact_and_noisy_tiers(self) -> None:
        with self.assertRaises(ValueError):
            validate_configuration_mapping(
                {
                    "experiment_name": "candidate_official_experiment",
                    "scientific_question": "Is the configuration validation enforcing execution policy?",
                    "official_experiment": True,
                    "truncation": {"basis": "toy", "cutoff": 2},
                    "observables": ["toy_pauli_z_expectation"],
                    "execution": {
                        "exact_local": {"enabled": True},
                        "noisy_local": {"enabled": False},
                    },
                }
            )
