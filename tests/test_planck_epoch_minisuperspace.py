"""Tests for the Planck-epoch-motivated minisuperspace experiment."""

from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import tempfile
import unittest

import yaml

from tests.path_setup import ensure_src_path

ensure_src_path()

from experiments.planck_epoch_minisuperspace.analyze import run_analysis
from experiments.planck_epoch_minisuperspace.benchmark import compute_benchmark
from experiments.planck_epoch_minisuperspace.circuit import build_ground_state_circuit
from experiments.planck_epoch_minisuperspace.common import (
    DEFAULT_CONFIG_PATH,
    canonicalize_real_statevector,
    load_experiment_definition,
)
from experiments.planck_epoch_minisuperspace.observables import build_observables
from experiments.planck_epoch_minisuperspace.run_aer import run_noisy_local
from experiments.planck_epoch_minisuperspace.run_local import run_exact_local


QISKIT_AVAILABLE = importlib.util.find_spec("qiskit") is not None


class PlanckEpochMinisuperspaceTests(unittest.TestCase):
    """Verify the official Planck-epoch-motivated minisuperspace experiment."""

    def test_configuration_is_official_and_complete(self) -> None:
        experiment = load_experiment_definition()
        self.assertTrue(experiment.configuration.official_experiment)
        self.assertEqual(experiment.configuration.status, "official")
        self.assertEqual(
            experiment.configuration.observables,
            (
                "scale_factor_expectation_value",
                "volume_expectation_value",
                "effective_hamiltonian_expectation",
                "smallest_scale_factor_probability",
            ),
        )

    def test_benchmark_values_match_reference_parameter_set(self) -> None:
        experiment = load_experiment_definition()
        benchmark = compute_benchmark(experiment.parameters)
        self.assertAlmostEqual(benchmark.ground_energy, -0.13427869803736275)
        self.assertAlmostEqual(
            benchmark.scale_factor_expectation_value,
            0.3409579452907098,
        )
        self.assertAlmostEqual(
            benchmark.volume_expectation_value,
            0.058451698470842514,
        )
        self.assertEqual(
            benchmark.focus_bin_probability_name,
            "smallest_scale_factor_probability",
        )
        self.assertAlmostEqual(
            benchmark.focus_bin_probability,
            0.11421160961397295,
        )
        self.assertIsNone(benchmark.rotation_angle)

    def test_observables_include_smallest_bin_projector(self) -> None:
        experiment = load_experiment_definition()
        observables = {
            observable.name: observable for observable in build_observables(experiment.parameters)
        }
        self.assertIn("smallest_scale_factor_probability", observables)
        self.assertEqual(
            [
                (term.label, term.coefficient)
                for term in observables["smallest_scale_factor_probability"].pauli_terms
            ],
            [("II", 0.25), ("IZ", 0.25), ("ZI", 0.25), ("ZZ", 0.25)],
        )

    def test_analysis_writes_observable_summary_table(self) -> None:
        outputs = run_analysis()
        table_path = Path(outputs["observable_summary_table_markdown"])
        self.assertTrue(table_path.exists())
        table_text = table_path.read_text(encoding="utf-8")
        self.assertIn(
            "|Observable|Benchmark|Exact local|Exact abs. error|Noisy local|Noisy abs. error|",
            table_text,
        )
        self.assertIn("|IBM Runtime|IBM abs. error|", table_text)
        self.assertIn(
            "|smallest_scale_factor_probability|0.114212|0.114212|0.000000|0.124591|0.010379|",
            table_text,
        )

    def test_analysis_exposes_live_ibm_artifacts_when_present(self) -> None:
        outputs = run_analysis()
        self.assertIn("ibm_runtime_json", outputs)
        self.assertIn("ibm_runtime_comparisons_json", outputs)
        self.assertIn("ibm_runtime_metadata_json", outputs)
        self.assertIn("ibm_runtime_report_markdown", outputs)

        summary_path = Path(outputs["analysis_summary_json"])
        self.assertTrue(summary_path.exists())
        summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertIn("ibm_runtime_values", summary_payload)
        self.assertIn("ibm_runtime_absolute_errors", summary_payload)
        self.assertIn("ibm_runtime_report_markdown", summary_payload)
        self.assertIn(
            "smallest_scale_factor_probability",
            summary_payload["ibm_runtime_values"],
        )
        report_path = Path(outputs["analysis_report_markdown"])
        report_text = report_path.read_text(encoding="utf-8")
        self.assertIn("## IBM Runtime Summary", report_text)
        self.assertIn("- IBM backend: `ibm_kingston`", report_text)
        self.assertIn("- IBM job id: `d782gp9q1efs73d18kng`", report_text)
        self.assertIn("smallest_scale_factor_probability: 0.113559", report_text)

    @unittest.skipUnless(QISKIT_AVAILABLE, "qiskit is not installed")
    def test_circuit_prepares_the_benchmark_state(self) -> None:
        from qiskit.quantum_info import Statevector

        experiment = load_experiment_definition()
        circuit_state = canonicalize_real_statevector(
            Statevector.from_instruction(
                build_ground_state_circuit(experiment.parameters)
            ).data
        )
        benchmark_state = canonicalize_real_statevector(
            compute_benchmark(experiment.parameters).ground_state
        )
        for circuit_component, benchmark_component in zip(
            circuit_state, benchmark_state, strict=True
        ):
            self.assertAlmostEqual(circuit_component, benchmark_component, places=10)

    @unittest.skipUnless(QISKIT_AVAILABLE, "qiskit is not installed")
    def test_exact_local_workflow_writes_expected_outputs_for_temp_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            config_mapping = yaml.safe_load(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"))
            for artifact_key in (
                "benchmark_json",
                "exact_local_json",
                "exact_local_comparisons_json",
            ):
                config_mapping["artifacts"][artifact_key] = str(
                    temp_root / f"{artifact_key}.json"
                )
            config_path = temp_root / "config.yaml"
            config_path.write_text(
                yaml.safe_dump(config_mapping, sort_keys=False),
                encoding="utf-8",
            )
            outputs = run_exact_local(str(config_path))

        self.assertIn("benchmark_json", outputs)
        self.assertIn("exact_local_json", outputs)
        self.assertIn("exact_local_comparisons_json", outputs)

    @unittest.skipUnless(QISKIT_AVAILABLE, "qiskit is not installed")
    def test_noisy_local_workflow_writes_expected_outputs_for_temp_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            config_mapping = yaml.safe_load(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"))
            for artifact_key in (
                "benchmark_json",
                "noisy_local_json",
                "noisy_local_comparisons_json",
            ):
                config_mapping["artifacts"][artifact_key] = str(
                    temp_root / f"{artifact_key}.json"
                )
            config_path = temp_root / "config.yaml"
            config_path.write_text(
                yaml.safe_dump(config_mapping, sort_keys=False),
                encoding="utf-8",
            )
            outputs = run_noisy_local(str(config_path))

        self.assertIn("benchmark_json", outputs)
        self.assertIn("noisy_local_json", outputs)
        self.assertIn("noisy_local_comparisons_json", outputs)
