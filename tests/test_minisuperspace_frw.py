"""Tests for the reduced FRW minisuperspace experiment."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from tests.path_setup import ensure_src_path

ensure_src_path()

from experiments.minisuperspace_frw.benchmark import compute_benchmark
from experiments.minisuperspace_frw.analyze import run_analysis
from experiments.minisuperspace_frw.circuit import build_ground_state_artifact
from experiments.minisuperspace_frw.common import (
    DEFAULT_CONFIG_PATH,
    effective_hamiltonian_matrix,
    ground_state_rotation_angle,
    load_experiment_definition,
    scale_factor_matrix,
)
from experiments.minisuperspace_frw.observables import build_observables
from experiments.minisuperspace_frw.run_ibm import run_ibm_hardware


QISKIT_AVAILABLE = importlib.util.find_spec("qiskit") is not None
SMALL_SCALE_FACTOR_CONFIG_PATH = DEFAULT_CONFIG_PATH.with_name(
    "config_small_scale_factor.yaml"
)


class MinisuperspaceFRWTests(unittest.TestCase):
    """Verify the first official minisuperspace experiment line."""

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
            ),
        )

    def test_benchmark_values_match_closed_form_parameter_choice(self) -> None:
        experiment = load_experiment_definition()
        benchmark = compute_benchmark(experiment.parameters)
        self.assertAlmostEqual(benchmark.ground_energy, -0.3)
        self.assertAlmostEqual(benchmark.scale_factor_expectation_value, 1.24)
        self.assertAlmostEqual(benchmark.volume_expectation_value, 2.2384)
        self.assertAlmostEqual(benchmark.large_scale_factor_probability, 0.8)
        self.assertAlmostEqual(benchmark.rotation_angle, 2.0 * math.atan2(2.0, 1.0))

    def test_hamiltonian_and_scale_factor_matrices_have_expected_entries(self) -> None:
        experiment = load_experiment_definition()
        hamiltonian = effective_hamiltonian_matrix(experiment.parameters)
        scale_factor = scale_factor_matrix(experiment.parameters)
        self.assertEqual(hamiltonian.tolist(), [[0.18, -0.24], [-0.24, -0.18]])
        self.assertEqual(scale_factor.tolist(), [[0.6, 0.0], [0.0, 1.4]])

    def test_observables_have_expected_pauli_decomposition(self) -> None:
        experiment = load_experiment_definition()
        observables = {observable.name: observable for observable in build_observables(experiment.parameters)}
        self.assertEqual(
            [(term.label, term.coefficient) for term in observables["scale_factor_expectation_value"].pauli_terms],
            [("I", 1.0), ("Z", -0.39999999999999997)],
        )
        self.assertEqual(
            [(term.label, term.coefficient) for term in observables["effective_hamiltonian_expectation"].pauli_terms],
            [("Z", 0.18), ("X", -0.24)],
        )

    def test_small_scale_factor_configuration_is_exploratory_and_complete(self) -> None:
        experiment = load_experiment_definition(str(SMALL_SCALE_FACTOR_CONFIG_PATH))
        self.assertFalse(experiment.configuration.official_experiment)
        self.assertEqual(experiment.configuration.status, "exploratory")
        self.assertEqual(
            experiment.configuration.observables,
            (
                "scale_factor_expectation_value",
                "volume_expectation_value",
                "effective_hamiltonian_expectation",
                "smallest_scale_factor_probability",
            ),
        )
        self.assertEqual(experiment.parameters.scale_factor_bins, (0.15, 0.25, 0.4, 0.6))
        self.assertEqual(experiment.parameters.qubit_count, 2)

    def test_small_scale_factor_benchmark_values_match_reference_parameter_set(self) -> None:
        experiment = load_experiment_definition(str(SMALL_SCALE_FACTOR_CONFIG_PATH))
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
        self.assertAlmostEqual(
            benchmark.large_scale_factor_probability,
            0.12809746928767865,
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

    def test_small_scale_factor_observables_include_focus_bin_projector(self) -> None:
        experiment = load_experiment_definition(str(SMALL_SCALE_FACTOR_CONFIG_PATH))
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
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            config_mapping = yaml.safe_load(
                DEFAULT_CONFIG_PATH.read_text(encoding="utf-8")
            )
            config_mapping["artifacts"]["analysis_summary_json"] = str(
                temp_root / "analysis_summary.json"
            )
            config_mapping["artifacts"]["analysis_report_markdown"] = str(
                temp_root / "analysis_report.md"
            )
            config_mapping["artifacts"]["observable_summary_table_markdown"] = str(
                temp_root / "observable_summary.md"
            )
            config_mapping["artifacts"]["comparison_figure"] = str(
                temp_root / "observable_comparison.png"
            )
            config_path = temp_root / "config.yaml"
            config_path.write_text(
                yaml.safe_dump(config_mapping, sort_keys=False),
                encoding="utf-8",
            )

            outputs = run_analysis(str(config_path))
            table_path = Path(outputs["observable_summary_table_markdown"])
            self.assertTrue(table_path.exists())
            table_text = table_path.read_text(encoding="utf-8")

        self.assertIn(
            "|Observable|Benchmark|Exact local|Exact abs. error|Noisy local|Noisy abs. error|",
            table_text,
        )
        self.assertIn(
            "|scale_factor_expectation_value|1.240000|1.240000|0.000000|1.227840|0.012160|",
            table_text,
        )

    def test_analysis_exposes_ibm_artifact_paths_when_ibm_outputs_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            config_mapping = yaml.safe_load(
                DEFAULT_CONFIG_PATH.read_text(encoding="utf-8")
            )
            config_mapping["artifacts"]["analysis_summary_json"] = str(
                temp_root / "analysis_summary.json"
            )
            config_mapping["artifacts"]["analysis_report_markdown"] = str(
                temp_root / "analysis_report.md"
            )
            config_mapping["artifacts"]["observable_summary_table_markdown"] = str(
                temp_root / "observable_summary.md"
            )
            config_mapping["artifacts"]["comparison_figure"] = str(
                temp_root / "observable_comparison.png"
            )
            config_mapping["artifacts"]["ibm_runtime_json"] = str(
                temp_root / "ibm_runtime.json"
            )
            config_mapping["artifacts"]["ibm_runtime_metadata_json"] = str(
                temp_root / "ibm_runtime_metadata.json"
            )
            config_mapping["artifacts"]["ibm_runtime_report_markdown"] = str(
                temp_root / "ibm_runtime_report.md"
            )
            config_path = temp_root / "config.yaml"
            config_path.write_text(
                yaml.safe_dump(config_mapping, sort_keys=False),
                encoding="utf-8",
            )
            exact_local_payload = json.loads(
                load_experiment_definition().artifacts.exact_local_json.read_text(
                    encoding="utf-8"
                )
            )
            Path(config_mapping["artifacts"]["ibm_runtime_json"]).write_text(
                json.dumps(exact_local_payload, indent=2) + "\n",
                encoding="utf-8",
            )
            Path(config_mapping["artifacts"]["ibm_runtime_metadata_json"]).write_text(
                "{}\n",
                encoding="utf-8",
            )
            Path(config_mapping["artifacts"]["ibm_runtime_report_markdown"]).write_text(
                "# Placeholder IBM hardware report\n",
                encoding="utf-8",
            )

            outputs = run_analysis(str(config_path))
            summary_payload = json.loads(
                Path(outputs["analysis_summary_json"]).read_text(encoding="utf-8")
            )

        self.assertIn("ibm_runtime_json", outputs)
        self.assertIn("ibm_runtime_metadata_json", outputs)
        self.assertIn("ibm_runtime_report_markdown", outputs)
        self.assertIn("ibm_runtime_json", summary_payload)
        self.assertIn("ibm_runtime_metadata_json", summary_payload)
        self.assertIn("ibm_runtime_report_markdown", summary_payload)

    def test_ibm_local_testing_routes_outputs_to_local_testing_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            config_mapping = yaml.safe_load(
                DEFAULT_CONFIG_PATH.read_text(encoding="utf-8")
            )
            config_mapping["artifacts"]["benchmark_json"] = str(
                temp_root / "benchmark.json"
            )
            config_mapping["artifacts"]["exact_local_json"] = str(
                temp_root / "exact_local.json"
            )
            config_mapping["artifacts"]["noisy_local_json"] = str(
                temp_root / "noisy_local.json"
            )
            config_mapping["artifacts"]["ibm_runtime_json"] = str(
                temp_root / "ibm_runtime.json"
            )
            config_mapping["artifacts"]["ibm_runtime_comparisons_json"] = str(
                temp_root / "ibm_runtime_comparisons.json"
            )
            config_mapping["artifacts"]["ibm_runtime_metadata_json"] = str(
                temp_root / "ibm_runtime_metadata.json"
            )
            config_mapping["artifacts"]["ibm_runtime_report_markdown"] = str(
                temp_root / "ibm_runtime_report.md"
            )
            config_path = temp_root / "config.yaml"
            config_path.write_text(
                yaml.safe_dump(config_mapping, sort_keys=False),
                encoding="utf-8",
            )
            Path(config_mapping["artifacts"]["exact_local_json"]).write_text(
                "{}\n",
                encoding="utf-8",
            )
            Path(config_mapping["artifacts"]["noisy_local_json"]).write_text(
                "{}\n",
                encoding="utf-8",
            )

            with patch(
                "experiments.minisuperspace_frw.run_ibm.instantiate_local_testing_backend",
                return_value=object(),
            ), patch(
                "experiments.minisuperspace_frw.run_ibm.IBMRuntimeEstimatorExecutor.run",
                return_value=object(),
            ), patch(
                "experiments.minisuperspace_frw.run_ibm.comparison_records_for_result",
                return_value=(),
            ), patch(
                "experiments.minisuperspace_frw.run_ibm.write_ibm_runtime_artifacts"
            ) as mocked_write:
                mocked_write.return_value = {
                    "ibm_runtime_json": temp_root / "ibm_runtime_local_testing.json",
                    "ibm_runtime_comparisons_json": (
                        temp_root / "ibm_runtime_comparisons_local_testing.json"
                    ),
                    "ibm_runtime_metadata_json": (
                        temp_root / "ibm_runtime_metadata_local_testing.json"
                    ),
                    "ibm_runtime_report_markdown": (
                        temp_root / "ibm_runtime_report_local_testing.md"
                    ),
                }
                outputs = run_ibm_hardware(
                    config_path=str(config_path),
                    local_testing_backend="FakeManilaV2",
                )

        kwargs = mocked_write.call_args.kwargs
        self.assertTrue(
            str(kwargs["execution_json_path"]).endswith("ibm_runtime_local_testing.json")
        )
        self.assertTrue(
            str(kwargs["comparison_json_path"]).endswith(
                "ibm_runtime_comparisons_local_testing.json"
            )
        )
        self.assertTrue(
            str(kwargs["metadata_json_path"]).endswith(
                "ibm_runtime_metadata_local_testing.json"
            )
        )
        self.assertTrue(
            str(kwargs["report_markdown_path"]).endswith(
                "ibm_runtime_report_local_testing.md"
            )
        )
        self.assertIn("ibm_runtime_json", outputs)
        self.assertTrue(outputs["ibm_runtime_json"].endswith("ibm_runtime_local_testing.json"))

    @unittest.skipUnless(QISKIT_AVAILABLE, "qiskit is not installed")
    def test_circuit_prepares_the_benchmark_ground_state(self) -> None:
        from qiskit.quantum_info import Statevector

        experiment = load_experiment_definition()
        artifact = build_ground_state_artifact(experiment.parameters)
        statevector = Statevector.from_instruction(artifact.payload).data
        self.assertAlmostEqual(abs(statevector[0]), 1.0 / math.sqrt(5.0), places=10)
        self.assertAlmostEqual(abs(statevector[1]), 2.0 / math.sqrt(5.0), places=10)
        self.assertAlmostEqual(
            artifact.parameter_values["theta"],
            ground_state_rotation_angle(experiment.parameters),
            places=12,
        )

    @unittest.skipUnless(QISKIT_AVAILABLE, "qiskit is not installed")
    def test_small_scale_factor_circuit_prepares_the_benchmark_ground_state(self) -> None:
        from qiskit.quantum_info import Statevector

        experiment = load_experiment_definition(str(SMALL_SCALE_FACTOR_CONFIG_PATH))
        benchmark = compute_benchmark(experiment.parameters)
        artifact = build_ground_state_artifact(experiment.parameters)
        statevector = Statevector.from_instruction(artifact.payload).data
        self.assertEqual(artifact.qubit_count, 2)
        self.assertEqual(artifact.parameter_values, {})
        for observed, expected in zip(statevector, benchmark.ground_state, strict=True):
            self.assertAlmostEqual(float(observed.real), expected, places=10)
            self.assertAlmostEqual(float(observed.imag), 0.0, places=10)
