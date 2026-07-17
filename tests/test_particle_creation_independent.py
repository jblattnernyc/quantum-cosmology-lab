"""Tests for independent validation of the FLRW particle-creation model."""

from __future__ import annotations

from dataclasses import replace
import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np
from scipy.linalg import expm
import yaml

from tests.path_setup import ensure_src_path

ensure_src_path()

from experiments.particle_creation_flrw.benchmark import (
    compute_benchmark,
    validation_context_for_benchmark,
)
from experiments.particle_creation_flrw.common import (
    DEFAULT_CONFIG_PATH,
    load_experiment_definition,
)
from experiments.particle_creation_flrw.independent_benchmark import (
    compute_independent_validation,
    independent_discrete_state,
    independent_operator_matrices,
    independent_slice_unitary,
    independent_validation_policy,
    independent_validation_record,
    independent_validation_to_serializable,
    write_independent_validation_artifacts,
)


class IndependentParticleCreationValidationTests(unittest.TestCase):
    """Verify independent reproduction, refinement, and persisted evidence."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.experiment = load_experiment_definition()
        cls.benchmark = compute_benchmark(cls.experiment.parameters)
        cls.context = validation_context_for_benchmark(
            cls.experiment,
            cls.benchmark,
        )
        cls.policy = independent_validation_policy(cls.experiment)
        cls.result = compute_independent_validation(
            cls.experiment.parameters,
            cls.benchmark.final_statevector,
            cls.benchmark.expected_observable_values(),
            cls.policy,
        )

    def test_matrix_implementation_is_hermitian_unitary_and_symmetric(self) -> None:
        matrices = independent_operator_matrices()
        for name, matrix in matrices.items():
            with self.subTest(operator=name):
                np.testing.assert_allclose(matrix, matrix.conj().T, atol=1.0e-14)

        parameters = self.experiment.parameters
        scale_factor_start = parameters.scale_factor_initial
        scale_factor_end = (
            scale_factor_start
            + (parameters.scale_factor_final - parameters.scale_factor_initial)
            / parameters.time_steps
        )
        frequency_start = math.sqrt(
            parameters.comoving_momentum**2
            + (parameters.mass * scale_factor_start) ** 2
        )
        frequency_end = math.sqrt(
            parameters.comoving_momentum**2 + (parameters.mass * scale_factor_end) ** 2
        )
        phase_angle = (
            0.5
            * (frequency_start + frequency_end)
            * parameters.time_extent
            / parameters.time_steps
        )
        squeezing_angle = 0.5 * math.log(frequency_end / frequency_start)
        unitary = independent_slice_unitary(phase_angle, squeezing_angle)
        np.testing.assert_allclose(
            unitary.conj().T @ unitary,
            np.eye(4),
            atol=1.0e-14,
        )

        phase_half_unitary = expm(-0.5j * phase_angle * matrices["phase_generator"])
        pairing_unitary = expm(-1.0j * squeezing_angle * matrices["pairing_generator"])
        np.testing.assert_allclose(
            unitary,
            phase_half_unitary @ pairing_unitary @ phase_half_unitary,
            atol=1.0e-14,
        )
        phase_unitary = phase_half_unitary @ phase_half_unitary
        self.assertGreater(
            float(np.max(np.abs(unitary - pairing_unitary @ phase_unitary))),
            1.0e-4,
        )

    def test_independent_discrete_result_reproduces_official_benchmark(self) -> None:
        independent_state = independent_discrete_state(self.experiment.parameters)
        official_state = np.asarray(self.benchmark.final_statevector, dtype=complex)
        overlap = np.vdot(official_state, independent_state)
        independent_state *= np.exp(-1.0j * np.angle(overlap))
        np.testing.assert_allclose(independent_state, official_state, atol=1.0e-12)
        self.assertTrue(self.result.assessment.passed)
        self.assertLessEqual(
            self.result.assessment.metrics[
                "official_maximum_observable_absolute_error"
            ],
            self.policy.observable_tolerance,
        )
        self.assertEqual(
            self.result.assessment.metrics["odd_parity_probability"],
            0.0,
        )

    def test_refinement_sequence_converges_under_declared_policy(self) -> None:
        records = self.result.convergence_records
        self.assertEqual(
            tuple(record.time_steps for record in records),
            (6, 12, 24, 48, 96),
        )
        errors = [record.maximum_observable_absolute_error for record in records]
        self.assertTrue(
            all(current < previous for previous, current in zip(errors, errors[1:]))
        )
        self.assertLessEqual(
            records[-1].maximum_observable_absolute_error,
            self.policy.maximum_final_observable_error,
        )
        self.assertLessEqual(
            records[-1].state_infidelity,
            self.policy.maximum_final_state_infidelity,
        )
        self.assertIsNotNone(records[-1].observable_convergence_order)
        self.assertGreaterEqual(
            records[-1].observable_convergence_order,
            self.policy.minimum_final_observable_convergence_order,
        )
        self.assertGreater(records[-1].observable_convergence_order, 1.99)

    def test_symmetric_ordering_improves_official_step_error(self) -> None:
        comparison = self.result.factor_ordering_comparison
        self.assertEqual(comparison.time_steps, 6)
        self.assertAlmostEqual(
            comparison.symmetric_maximum_observable_error,
            0.006417712569834921,
        )
        self.assertAlmostEqual(
            comparison.legacy_first_order_maximum_observable_error,
            0.027446425133081764,
        )
        self.assertGreater(
            comparison.observable_error_improvement_factor,
            self.policy.minimum_official_step_factor_ordering_improvement,
        )
        self.assertTrue(
            self.result.assessment.checks["official_step_factor_ordering_improvement"]
        )

    def test_factor_ordering_diagnostics_are_platform_stable(self) -> None:
        payload = independent_validation_to_serializable(
            self.experiment,
            self.result,
            self.policy,
            self.context,
        )
        comparison = self.result.factor_ordering_comparison
        serialized = payload["factor_ordering_comparison"]
        self.assertEqual(
            serialized["observable_error_improvement_factor"],
            round(comparison.observable_error_improvement_factor, 8),
        )
        self.assertNotIn(
            "official_step_factor_ordering_improvement",
            payload["assessment"]["metrics"],
        )
        self.assertEqual(
            payload["method"]["factor_ordering_comparison_canonical_decimal_places"],
            10,
        )
        self.assertEqual(
            payload["method"]["factor_ordering_improvement_canonical_decimal_places"],
            8,
        )

        perturbed_comparison = replace(
            comparison,
            symmetric_maximum_observable_error=(
                comparison.symmetric_maximum_observable_error + 5.0e-12
            ),
            legacy_first_order_maximum_observable_error=(
                comparison.legacy_first_order_maximum_observable_error + 5.0e-12
            ),
            observable_error_improvement_factor=(
                comparison.observable_error_improvement_factor + 5.0e-10
            ),
            symmetric_state_infidelity=(
                comparison.symmetric_state_infidelity + 5.0e-12
            ),
            legacy_first_order_state_infidelity=(
                comparison.legacy_first_order_state_infidelity + 5.0e-12
            ),
        )
        perturbed_payload = independent_validation_to_serializable(
            self.experiment,
            replace(
                self.result,
                factor_ordering_comparison=perturbed_comparison,
            ),
            self.policy,
            self.context,
        )
        self.assertEqual(
            serialized,
            perturbed_payload["factor_ordering_comparison"],
        )

    def test_independent_module_does_not_call_primary_evolution_helpers(self) -> None:
        module_path = Path(
            "experiments/particle_creation_flrw/independent_benchmark.py"
        )
        source = module_path.read_text(encoding="utf-8")
        forbidden_calls = (
            "evolution_slices(",
            "apply_evolution_slice(",
            "evolve_even_subspace_state(",
            "build_particle_creation_circuit(",
            "build_observables(",
        )
        for forbidden_call in forbidden_calls:
            with self.subTest(forbidden_call=forbidden_call):
                self.assertNotIn(forbidden_call, source)

    def test_persisted_evidence_is_recomputed_and_tamper_sensitive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            config_mapping = yaml.safe_load(
                DEFAULT_CONFIG_PATH.read_text(encoding="utf-8")
            )
            config_mapping["artifacts"]["independent_validation_json"] = str(
                temp_root / "independent_validation.json"
            )
            config_mapping["artifacts"]["independent_validation_report_markdown"] = str(
                temp_root / "independent_validation_report.md"
            )
            config_mapping["artifacts"]["convergence_summary_table_markdown"] = str(
                temp_root / "convergence_summary.md"
            )
            config_path = temp_root / "config.yaml"
            config_path.write_text(
                yaml.safe_dump(config_mapping, sort_keys=False),
                encoding="utf-8",
            )
            experiment = load_experiment_definition(config_path)
            benchmark = compute_benchmark(experiment.parameters)
            context = validation_context_for_benchmark(experiment, benchmark)
            policy = independent_validation_policy(experiment)
            result = compute_independent_validation(
                experiment.parameters,
                benchmark.final_statevector,
                benchmark.expected_observable_values(),
                policy,
            )
            write_independent_validation_artifacts(
                experiment,
                result,
                policy,
                context,
            )

            record, assessment = independent_validation_record(
                experiment,
                benchmark,
                context,
            )
            self.assertTrue(record["stored_result_matches"])
            self.assertTrue(assessment.passed)

            payload = json.loads(
                experiment.artifacts.independent_validation_json.read_text(
                    encoding="utf-8"
                )
            )
            payload["convergence"][0]["maximum_observable_absolute_error"] += 5.0e-13
            experiment.artifacts.independent_validation_json.write_text(
                json.dumps(payload, indent=2) + "\n",
                encoding="utf-8",
            )
            perturbed_record, perturbed_assessment = independent_validation_record(
                experiment,
                benchmark,
                context,
            )
            self.assertTrue(perturbed_record["stored_result_matches"])
            self.assertTrue(perturbed_assessment.passed)

            payload["convergence"][0]["time_steps"] = 7
            experiment.artifacts.independent_validation_json.write_text(
                json.dumps(payload, indent=2) + "\n",
                encoding="utf-8",
            )
            tampered_record, tampered_assessment = independent_validation_record(
                experiment,
                benchmark,
                context,
            )
            self.assertFalse(tampered_record["stored_result_matches"])
            self.assertFalse(tampered_assessment.passed)


if __name__ == "__main__":
    unittest.main()
