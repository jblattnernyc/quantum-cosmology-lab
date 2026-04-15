"""Tests for the reduced Grand-Unification-Epoch-context toy experiment."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import yaml

from tests.path_setup import ensure_src_path

ensure_src_path()

from experiments.grand_unification_epoch_toy.analyze import run_analysis
from experiments.grand_unification_epoch_toy.benchmark import compute_benchmark
from experiments.grand_unification_epoch_toy.circuit import build_ground_state_artifact
from experiments.grand_unification_epoch_toy.common import (
    DEFAULT_CONFIG_PATH,
    canonicalize_real_statevector,
    domain_wall_operator,
    effective_hamiltonian_matrix,
    load_experiment_definition,
)
from experiments.grand_unification_epoch_toy.observables import build_observables
from experiments.grand_unification_epoch_toy.run_aer import run_noisy_local
from experiments.grand_unification_epoch_toy.run_local import run_exact_local
from qclab.utils.runtime import is_aer_execution_guard_required


QISKIT_AVAILABLE = importlib.util.find_spec("qiskit") is not None
QISKIT_AER_AVAILABLE = importlib.util.find_spec("qiskit_aer") is not None
AER_LOCAL_GUARD = is_aer_execution_guard_required()


class GrandUnificationEpochToyTests(unittest.TestCase):
    """Verify the Grand-Unification-Epoch-context toy experiment line."""

    def test_configuration_is_official_and_complete(self) -> None:
        experiment = load_experiment_definition()
        self.assertTrue(experiment.configuration.official_experiment)
        self.assertEqual(experiment.configuration.status, "official")
        self.assertEqual(
            experiment.configuration.observables,
            (
                "order_parameter_expectation",
                "domain_wall_density",
                "transverse_coherence_expectation",
                "effective_hamiltonian_expectation",
            ),
        )

    def test_benchmark_values_match_default_parameter_choice(self) -> None:
        experiment = load_experiment_definition()
        benchmark = compute_benchmark(experiment.parameters)
        self.assertAlmostEqual(benchmark.ground_energy, -0.8204719227933479)
        self.assertAlmostEqual(benchmark.order_parameter_expectation, 0.8941919634759182)
        self.assertAlmostEqual(benchmark.domain_wall_density, 0.029822206193642085)
        self.assertAlmostEqual(
            benchmark.transverse_coherence_expectation,
            0.28339891995741684,
        )
        self.assertAlmostEqual(
            benchmark.effective_hamiltonian_expectation,
            -0.8204719227933478,
        )

    def test_hamiltonian_and_domain_wall_operator_have_expected_entries(self) -> None:
        experiment = load_experiment_definition()
        hamiltonian = effective_hamiltonian_matrix(experiment.parameters)
        domain_wall = domain_wall_operator(experiment.parameters)
        self.assertEqual(
            hamiltonian.tolist(),
            [
                [-0.7799999999999999, -0.16, -0.16, -0.0],
                [-0.16, 0.7, -0.0, -0.16],
                [-0.16, -0.0, 0.7, -0.16],
                [-0.0, -0.16, -0.16, -0.62],
            ],
        )
        self.assertEqual(
            domain_wall.tolist(),
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
                for term in observables["order_parameter_expectation"].pauli_terms
            ],
            [("IZ", 0.5), ("ZI", 0.5)],
        )
        self.assertEqual(
            [
                (term.label, term.coefficient)
                for term in observables["domain_wall_density"].pauli_terms
            ],
            [("II", 0.5), ("ZZ", -0.5)],
        )
        self.assertEqual(
            [
                (term.label, term.coefficient)
                for term in observables[
                    "transverse_coherence_expectation"
                ].pauli_terms
            ],
            [("IX", 0.5), ("XI", 0.5)],
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
            "|order_parameter_expectation|0.894192|0.894192|0.000000|",
            table_text,
        )

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
            circuit_state,
            benchmark_state,
            strict=True,
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
        QISKIT_AVAILABLE and (QISKIT_AER_AVAILABLE or AER_LOCAL_GUARD),
        "qiskit plus either qiskit_aer or the guarded analytic fallback are required",
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


if __name__ == "__main__":
    unittest.main()

