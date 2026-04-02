"""Tests for the reduced two-link Z2 toy-gauge experiment."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import platform
import sys
import tempfile
import unittest

import yaml

from tests.path_setup import ensure_src_path

ensure_src_path()

from experiments.gut_toy_gauge.analyze import run_analysis
from experiments.gut_toy_gauge.benchmark import compute_benchmark
from experiments.gut_toy_gauge.circuit import build_ground_state_artifact
from experiments.gut_toy_gauge.common import (
    DEFAULT_CONFIG_PATH,
    canonicalize_real_statevector,
    full_hamiltonian_matrix,
    gauge_violation_operator,
    load_experiment_definition,
)
from experiments.gut_toy_gauge.observables import build_observables
from experiments.gut_toy_gauge.run_aer import run_noisy_local
from experiments.gut_toy_gauge.run_local import run_exact_local


QISKIT_AVAILABLE = importlib.util.find_spec("qiskit") is not None
QISKIT_AER_AVAILABLE = importlib.util.find_spec("qiskit_aer") is not None
AER_LOCAL_GUARD = (
    platform.system() == "Darwin"
    and platform.machine() == "arm64"
    and sys.version_info >= (3, 14)
)


class GutToyGaugeTests(unittest.TestCase):
    """Verify the third official toy-gauge experiment line."""

    def test_configuration_is_official_and_complete(self) -> None:
        experiment = load_experiment_definition()
        self.assertTrue(experiment.configuration.official_experiment)
        self.assertEqual(experiment.configuration.status, "official")
        self.assertEqual(
            experiment.configuration.observables,
            (
                "gauge_invariance_violation_expectation",
                "link_alignment_order_parameter",
                "wilson_line_correlator_proxy",
            ),
        )

    def test_benchmark_values_match_default_parameter_choice(self) -> None:
        experiment = load_experiment_definition()
        benchmark = compute_benchmark(experiment.parameters)
        expected_spectrum = (-0.3, 0.3, 0.96, 1.44)
        for observed, expected in zip(benchmark.spectrum, expected_spectrum, strict=True):
            self.assertAlmostEqual(observed, expected)
        self.assertAlmostEqual(benchmark.ground_energy, -0.3)
        self.assertAlmostEqual(benchmark.gauge_invariance_violation_expectation, 0.0)
        self.assertAlmostEqual(benchmark.link_alignment_order_parameter, -0.6)
        self.assertAlmostEqual(benchmark.wilson_line_correlator_proxy, 0.8)
        self.assertAlmostEqual(benchmark.physical_sector_probability, 1.0)

    def test_hamiltonian_and_gauge_projector_have_expected_entries(self) -> None:
        experiment = load_experiment_definition()
        hamiltonian = full_hamiltonian_matrix(experiment.parameters)
        gauge_projector = gauge_violation_operator(experiment.parameters)
        self.assertEqual(
            hamiltonian.tolist(),
            [
                [0.18, 0.0, 0.0, -0.24],
                [0.0, 1.2, -0.24, 0.0],
                [0.0, -0.24, 1.2, 0.0],
                [-0.24, 0.0, 0.0, -0.18],
            ],
        )
        self.assertEqual(
            gauge_projector.tolist(),
            [
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
            ],
        )

    def test_observables_have_expected_pauli_decomposition(self) -> None:
        experiment = load_experiment_definition()
        observables = {
            observable.name: observable
            for observable in build_observables(experiment.parameters)
        }
        self.assertEqual(
            [
                (term.label, term.coefficient)
                for term in observables[
                    "gauge_invariance_violation_expectation"
                ].pauli_terms
            ],
            [("II", 0.5), ("ZZ", -0.5)],
        )
        self.assertEqual(
            [
                (term.label, term.coefficient)
                for term in observables[
                    "link_alignment_order_parameter"
                ].pauli_terms
            ],
            [("IZ", 0.5), ("ZI", 0.5)],
        )
        self.assertEqual(
            [
                (term.label, term.coefficient)
                for term in observables[
                    "wilson_line_correlator_proxy"
                ].pauli_terms
            ],
            [("XX", 1.0)],
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
        self.assertIn(
            "|gauge_invariance_violation_expectation|0.000000|0.000000|0.000000|",
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

    @unittest.skipUnless(QISKIT_AVAILABLE, "qiskit is not installed")
    def test_circuit_prepares_the_benchmark_ground_state(self) -> None:
        from qiskit.quantum_info import Statevector

        experiment = load_experiment_definition()
        artifact = build_ground_state_artifact(experiment.parameters)
        circuit_state = canonicalize_real_statevector(
            Statevector.from_instruction(artifact.payload).data
        )
        benchmark_state = canonicalize_real_statevector(
            compute_benchmark(experiment.parameters).ground_state
        )
        for circuit_component, benchmark_component in zip(
            circuit_state, benchmark_state, strict=True
        ):
            self.assertAlmostEqual(circuit_component, benchmark_component, places=12)
        self.assertEqual(artifact.qubit_count, 2)

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
                config_mapping["artifacts"][artifact_key] = str(temp_root / f"{artifact_key}.json")
            config_path = temp_root / "config.yaml"
            config_path.write_text(
                yaml.safe_dump(config_mapping, sort_keys=False),
                encoding="utf-8",
            )
            outputs = run_exact_local(str(config_path))

        self.assertIn("benchmark_json", outputs)
        self.assertIn("exact_local_json", outputs)
        self.assertIn("exact_local_comparisons_json", outputs)

    @unittest.skipUnless(
        QISKIT_AVAILABLE and QISKIT_AER_AVAILABLE,
        "qiskit and qiskit_aer are both required for Aer workflow tests",
    )
    @unittest.skipIf(
        AER_LOCAL_GUARD,
        "Aer workflow tests are guarded on macOS arm64 with Python 3.14+ due to local libomp runtime aborts.",
    )
    def test_noisy_local_workflow_writes_expected_outputs_for_temp_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            config_mapping = yaml.safe_load(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"))
            for artifact_key in (
                "benchmark_json",
                "noisy_local_json",
                "noisy_local_comparisons_json",
            ):
                config_mapping["artifacts"][artifact_key] = str(temp_root / f"{artifact_key}.json")
            config_path = temp_root / "config.yaml"
            config_path.write_text(
                yaml.safe_dump(config_mapping, sort_keys=False),
                encoding="utf-8",
            )
            outputs = run_noisy_local(str(config_path))

        self.assertIn("benchmark_json", outputs)
        self.assertIn("noisy_local_json", outputs)
        self.assertIn("noisy_local_comparisons_json", outputs)
