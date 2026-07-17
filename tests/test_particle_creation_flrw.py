"""Tests for the reduced FLRW particle-creation experiment."""

from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from tests.path_setup import ensure_src_path

ensure_src_path()

from experiments.particle_creation_flrw.analyze import run_analysis
from experiments.particle_creation_flrw.benchmark import compute_benchmark
from experiments.particle_creation_flrw.circuit import build_particle_creation_artifact
from experiments.particle_creation_flrw.common import (
    DEFAULT_CONFIG_PATH,
    canonicalize_statevector,
    evolution_slices,
    load_experiment_definition,
)
from experiments.particle_creation_flrw.observables import build_observables
from experiments.particle_creation_flrw.run_ibm import (
    main as run_ibm_main,
    run_hardware_preflight,
)
from qclab.validation import HardwareValidationGateError


QISKIT_AVAILABLE = importlib.util.find_spec("qiskit") is not None


class ParticleCreationFLRWTests(unittest.TestCase):
    """Verify the second official particle-creation experiment line."""

    def test_configuration_is_official_and_complete(self) -> None:
        experiment = load_experiment_definition()
        self.assertTrue(experiment.configuration.official_experiment)
        self.assertEqual(experiment.configuration.status, "official")
        self.assertEqual(
            experiment.configuration.observables,
            (
                "single_mode_particle_number_expectation",
                "total_particle_number_expectation",
                "pairing_correlator_expectation",
            ),
        )
        validation = experiment.configuration.metadata["validation"]
        self.assertEqual(validation["schema_version"], 1)
        self.assertEqual(
            set(validation["tiers"]),
            {"exact_local", "noisy_local", "ibm_hardware"},
        )
        self.assertEqual(
            validation["independent_benchmark"]["convergence_time_steps"],
            [6, 12, 24, 48, 96],
        )
        feasibility = experiment.configuration.metadata["hardware_feasibility"]
        self.assertEqual(feasibility["status"], "exploratory")
        self.assertEqual(feasibility["time_steps"], [6, 12, 24])
        self.assertEqual(feasibility["live_hardware_recommendation"], "defer")

    def test_evolution_slices_are_monotone_and_match_time_steps(self) -> None:
        experiment = load_experiment_definition()
        slices = evolution_slices(experiment.parameters)
        self.assertEqual(len(slices), experiment.parameters.time_steps)
        self.assertLess(slices[0].scale_factor_start, slices[-1].scale_factor_end)
        self.assertLess(
            slices[0].mode_frequency_start,
            slices[-1].mode_frequency_end,
        )
        self.assertGreater(slices[0].squeezing_angle, 0.0)

    def test_benchmark_values_match_regression_reference(self) -> None:
        experiment = load_experiment_definition()
        benchmark = compute_benchmark(experiment.parameters)
        self.assertAlmostEqual(
            benchmark.single_mode_particle_number_expectation,
            0.03422860544437149,
        )
        self.assertAlmostEqual(
            benchmark.total_particle_number_expectation,
            0.06845721088874299,
        )
        self.assertAlmostEqual(
            benchmark.pairing_correlator_expectation,
            -0.3465452307022458,
        )
        self.assertAlmostEqual(
            benchmark.pair_occupation_probability, 0.03422860544437149
        )
        self.assertAlmostEqual(benchmark.even_parity_probability, 1.0)

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
                    "single_mode_particle_number_expectation"
                ].pauli_terms
            ],
            [("II", 0.5), ("IZ", -0.5)],
        )
        self.assertEqual(
            [
                (term.label, term.coefficient)
                for term in observables["total_particle_number_expectation"].pauli_terms
            ],
            [("II", 1.0), ("IZ", -0.5), ("ZI", -0.5)],
        )
        self.assertEqual(
            [
                (term.label, term.coefficient)
                for term in observables["pairing_correlator_expectation"].pauli_terms
            ],
            [("XX", 0.5), ("YY", -0.5)],
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
            "|total_particle_number_expectation|0.068457|0.068457|0.000000|0.122302|0.053845|",
            table_text,
        )
        self.assertIn("|PASS|PASS|FAIL|", table_text)

        summary_payload = json.loads(
            Path(outputs["analysis_summary_json"]).read_text(encoding="utf-8")
        )
        validation = summary_payload["validation"]
        self.assertEqual(
            validation["independent_benchmark"]["lineage_status"],
            "current",
        )
        self.assertTrue(validation["independent_benchmark"]["stored_result_matches"])
        self.assertTrue(validation["independent_benchmark"]["assessment"]["passed"])
        self.assertIn("hardware_feasibility_json", summary_payload)
        self.assertIn("hardware_feasibility_report_markdown", summary_payload)
        self.assertIn("hardware_feasibility_table_markdown", summary_payload)
        self.assertEqual(validation["exact_local"]["lineage_status"], "current")
        self.assertTrue(validation["exact_local"]["assessment"]["passed"])
        self.assertTrue(validation["exact_local"]["stored_assessment_matches"])
        self.assertEqual(validation["noisy_local"]["lineage_status"], "current")
        self.assertTrue(validation["noisy_local"]["assessment"]["passed"])
        self.assertTrue(validation["noisy_local"]["stored_assessment_matches"])
        self.assertEqual(
            validation["ibm_runtime"]["lineage_status"],
            "legacy_unbound",
        )
        self.assertFalse(validation["ibm_runtime"]["assessment"]["passed"])

        report_text = Path(outputs["analysis_report_markdown"]).read_text(
            encoding="utf-8"
        )
        self.assertIn("| Independent benchmark | current |", report_text)
        self.assertIn("| Exact local | current |", report_text)
        self.assertIn("| Noisy local | current |", report_text)
        self.assertIn("| IBM Runtime | legacy_unbound |", report_text)

    def test_preflight_only_does_not_invoke_ibm_executor(self) -> None:
        preflight = run_hardware_preflight()
        self.assertTrue(preflight.passed)

        stdout = io.StringIO()
        with patch(
            "experiments.particle_creation_flrw.run_ibm.IBMRuntimeEstimatorExecutor.run"
        ) as executor_run:
            with redirect_stdout(stdout):
                return_code = run_ibm_main(["--preflight-only"])
        executor_run.assert_not_called()
        self.assertEqual(return_code, 0)
        self.assertIn("validation_preflight: PASS", stdout.getvalue())
        self.assertIn("independent_benchmark: PASS", stdout.getvalue())
        self.assertIn("exact_local: PASS", stdout.getvalue())
        self.assertIn("noisy_local: PASS", stdout.getvalue())

    def test_preflight_rejects_configuration_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_mapping = yaml.safe_load(
                DEFAULT_CONFIG_PATH.read_text(encoding="utf-8")
            )
            config_mapping["parameters"]["mass"] = 0.61
            config_path = Path(temp_dir) / "config.yaml"
            config_path.write_text(
                yaml.safe_dump(config_mapping, sort_keys=False),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                HardwareValidationGateError,
                "lineage does not match",
            ):
                run_hardware_preflight(str(config_path))

    def test_preflight_rejects_missing_independent_evidence_before_execution(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_mapping = yaml.safe_load(
                DEFAULT_CONFIG_PATH.read_text(encoding="utf-8")
            )
            config_mapping["artifacts"]["independent_validation_json"] = str(
                Path(temp_dir) / "missing-independent-validation.json"
            )
            config_path = Path(temp_dir) / "config.yaml"
            config_path.write_text(
                yaml.safe_dump(config_mapping, sort_keys=False),
                encoding="utf-8",
            )
            with patch(
                "experiments.particle_creation_flrw.run_ibm.IBMRuntimeEstimatorExecutor.run"
            ) as executor_run:
                with self.assertRaisesRegex(
                    HardwareValidationGateError,
                    "does not exist",
                ):
                    run_ibm_main(
                        [
                            "--config",
                            str(config_path),
                            "--local-testing-backend",
                            "FakeManilaV2",
                        ]
                    )
            executor_run.assert_not_called()

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
    def test_circuit_prepares_the_benchmark_state(self) -> None:
        from qiskit.quantum_info import Statevector

        experiment = load_experiment_definition()
        artifact = build_particle_creation_artifact(experiment.parameters)
        circuit_state = canonicalize_statevector(
            Statevector.from_instruction(artifact.payload).data
        )
        benchmark_state = canonicalize_statevector(
            compute_benchmark(experiment.parameters).final_statevector
        )
        for circuit_component, benchmark_component in zip(
            circuit_state, benchmark_state, strict=True
        ):
            self.assertAlmostEqual(
                circuit_component.real, benchmark_component.real, places=10
            )
            self.assertAlmostEqual(
                circuit_component.imag, benchmark_component.imag, places=10
            )
        self.assertEqual(artifact.qubit_count, 2)
