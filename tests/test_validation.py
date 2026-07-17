"""Tests for shared validation lineage and hardware progression gates."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

from tests.path_setup import ensure_src_path

ensure_src_path()

from experiments.particle_creation_flrw.benchmark import (
    benchmark_to_serializable,
    compute_benchmark,
    validation_context_for_benchmark,
)
from experiments.particle_creation_flrw.common import (
    load_experiment_definition,
    validation_configuration_for_experiment,
)
from experiments.particle_creation_flrw.observables import build_observables
from qclab.observables import make_pauli_observable
from qclab.validation import (
    ArtifactLineageStatus,
    HardwareValidationGateError,
    assess_observable_values,
    benchmark_fingerprint,
    classify_artifact_lineage,
    configuration_fingerprint,
    model_fingerprint,
    observable_fingerprint,
    validate_hardware_prerequisites,
)


class ValidationLineageTests(unittest.TestCase):
    """Verify deterministic, content-sensitive validation lineage."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.experiment = load_experiment_definition()
        cls.benchmark = compute_benchmark(cls.experiment.parameters)
        cls.observables = build_observables(cls.experiment.parameters)
        cls.benchmark_payload = benchmark_to_serializable(cls.experiment, cls.benchmark)
        cls.context = validation_context_for_benchmark(cls.experiment, cls.benchmark)
        cls.validation_configuration = validation_configuration_for_experiment(
            cls.experiment
        )

    def test_fingerprints_are_deterministic_and_ignore_artifact_locations(self) -> None:
        reordered_payload = {
            key: self.benchmark_payload[key]
            for key in reversed(tuple(self.benchmark_payload))
        }
        self.assertEqual(
            benchmark_fingerprint(self.benchmark_payload),
            benchmark_fingerprint(reordered_payload),
        )

        metadata = dict(self.experiment.configuration.metadata)
        metadata["artifacts"] = {"benchmark_json": "/tmp/moved-benchmark.json"}
        relocated_configuration = replace(
            self.experiment.configuration,
            metadata=metadata,
        )
        self.assertEqual(
            configuration_fingerprint(self.experiment.configuration),
            configuration_fingerprint(relocated_configuration),
        )

    def test_parameter_operator_and_benchmark_changes_break_lineage(self) -> None:
        parameters = dict(self.experiment.configuration.parameters)
        parameters["mass"] = float(parameters["mass"]) + 0.01
        changed_configuration = replace(
            self.experiment.configuration,
            parameters=parameters,
        )
        self.assertNotEqual(
            model_fingerprint(self.experiment.configuration),
            model_fingerprint(changed_configuration),
        )

        changed_observables = list(self.observables)
        changed_observables[0] = make_pauli_observable(
            name="single_mode_particle_number_expectation",
            terms={"II": 0.5, "IZ": -0.49},
            physical_meaning="Deliberately changed test operator.",
        )
        self.assertNotEqual(
            observable_fingerprint(self.observables),
            observable_fingerprint(tuple(changed_observables)),
        )

        changed_benchmark = deepcopy(self.benchmark_payload)
        changed_benchmark["benchmark"]["single_mode_particle_number_expectation"] += (
            0.01
        )
        self.assertNotEqual(
            benchmark_fingerprint(self.benchmark_payload),
            benchmark_fingerprint(changed_benchmark),
        )

    def test_artifact_lineage_classification_covers_current_stale_legacy_and_invalid(
        self,
    ) -> None:
        current_payload = {
            "validation_context": self.context.to_serializable(),
        }
        stale_context = replace(self.context, lineage_id="0" * 64)
        stale_payload = {
            "validation_context": stale_context.to_serializable(),
        }
        classifications = {
            "current": classify_artifact_lineage(current_payload, self.context),
            "stale": classify_artifact_lineage(stale_payload, self.context),
            "legacy": classify_artifact_lineage({}, self.context),
            "invalid": classify_artifact_lineage(
                {"validation_context": "not-a-mapping"},
                self.context,
            ),
        }
        self.assertEqual(
            classifications["current"].status,
            ArtifactLineageStatus.CURRENT,
        )
        self.assertEqual(
            classifications["stale"].status,
            ArtifactLineageStatus.STALE,
        )
        self.assertEqual(
            classifications["legacy"].status,
            ArtifactLineageStatus.LEGACY_UNBOUND,
        )
        self.assertEqual(
            classifications["invalid"].status,
            ArtifactLineageStatus.INVALID,
        )

    def test_current_local_results_pass_and_archived_ibm_result_fails(self) -> None:
        expected_values = self.benchmark.expected_observable_values()
        assessments = {}
        for tier, path in (
            ("exact_local", self.experiment.artifacts.exact_local_json),
            ("noisy_local", self.experiment.artifacts.noisy_local_json),
            ("ibm_hardware", self.experiment.artifacts.ibm_runtime_json),
        ):
            payload = json.loads(path.read_text(encoding="utf-8"))
            assessments[tier] = assess_observable_values(
                tier=tier,
                lineage_id=self.context.lineage_id,
                evaluations=payload["evaluations"],
                benchmark_values=expected_values,
                validation_configuration=self.validation_configuration,
            )
            if tier in {"exact_local", "noisy_local"}:
                self.assertEqual(
                    payload["validation_context"],
                    self.context.to_serializable(),
                )
                self.assertEqual(
                    payload["validation_assessment"],
                    assessments[tier].to_serializable(),
                )

        self.assertTrue(assessments["exact_local"].passed)
        self.assertTrue(assessments["noisy_local"].passed)
        self.assertFalse(assessments["ibm_hardware"].passed)
        failed_names = {
            item.observable_name
            for item in assessments["ibm_hardware"].observables
            if not item.passed
        }
        self.assertEqual(failed_names, set(expected_values))


class HardwareValidationGateTests(unittest.TestCase):
    """Verify that hardware readiness depends on current, passing content."""

    def setUp(self) -> None:
        self.experiment = load_experiment_definition()
        self.benchmark = compute_benchmark(self.experiment.parameters)
        self.context = validation_context_for_benchmark(self.experiment, self.benchmark)
        self.validation_configuration = validation_configuration_for_experiment(
            self.experiment
        )
        self.expected_values = self.benchmark.expected_observable_values()

    def _execution_payload(
        self,
        tier: str,
        values: dict[str, float],
        *,
        context=None,
        uncertainties: dict[str, float] | None = None,
    ) -> dict:
        current_context = self.context if context is None else context
        uncertainty_values = uncertainties or {}
        evaluations = [
            {
                "observable_name": name,
                "value": value,
                "uncertainty": uncertainty_values.get(name, 0.0),
            }
            for name, value in values.items()
        ]
        assessment = assess_observable_values(
            tier=tier,
            lineage_id=current_context.lineage_id,
            evaluations=evaluations,
            benchmark_values=self.expected_values,
            validation_configuration=self.validation_configuration,
        )
        return {
            "request": {"tier": tier},
            "provenance": {"tier": tier},
            "evaluations": evaluations,
            "validation_context": current_context.to_serializable(),
            "validation_assessment": assessment.to_serializable(),
        }

    def _write_artifacts(
        self,
        root: Path,
        *,
        exact_payload: dict,
        noisy_payload: dict,
    ) -> tuple[Path, Path, Path]:
        benchmark_path = root / "benchmark.json"
        exact_path = root / "exact.json"
        noisy_path = root / "noisy.json"
        benchmark_payload = benchmark_to_serializable(
            self.experiment,
            self.benchmark,
            validation_context=self.context,
        )
        for path, payload in (
            (benchmark_path, benchmark_payload),
            (exact_path, exact_payload),
            (noisy_path, noisy_payload),
        ):
            path.write_text(json.dumps(payload), encoding="utf-8")
        return benchmark_path, exact_path, noisy_path

    def _run_gate(self, paths: tuple[Path, Path, Path]):
        benchmark_path, exact_path, noisy_path = paths
        return validate_hardware_prerequisites(
            current_context=self.context,
            benchmark_values=self.expected_values,
            validation_configuration=self.validation_configuration,
            benchmark_path=benchmark_path,
            exact_local_path=exact_path,
            noisy_local_path=noisy_path,
        )

    def test_gate_accepts_matching_passing_evidence(self) -> None:
        exact_payload = self._execution_payload("exact_local", self.expected_values)
        noisy_payload = self._execution_payload("noisy_local", self.expected_values)
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self._write_artifacts(
                Path(temp_dir),
                exact_payload=exact_payload,
                noisy_payload=noisy_payload,
            )
            result = self._run_gate(paths)
        self.assertTrue(result.passed)
        self.assertEqual(result.lineage_id, self.context.lineage_id)

    def test_gate_rejects_stale_lineage(self) -> None:
        stale_context = replace(self.context, lineage_id="0" * 64)
        exact_payload = self._execution_payload(
            "exact_local",
            self.expected_values,
            context=stale_context,
        )
        noisy_payload = self._execution_payload("noisy_local", self.expected_values)
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self._write_artifacts(
                Path(temp_dir),
                exact_payload=exact_payload,
                noisy_payload=noisy_payload,
            )
            with self.assertRaisesRegex(
                HardwareValidationGateError,
                "lineage does not match",
            ):
                self._run_gate(paths)

    def test_gate_rejects_failing_or_tampered_assessment(self) -> None:
        exact_payload = self._execution_payload("exact_local", self.expected_values)
        failed_values = dict(self.expected_values)
        failed_values["total_particle_number_expectation"] = 1.5
        noisy_payload = self._execution_payload("noisy_local", failed_values)
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self._write_artifacts(
                Path(temp_dir),
                exact_payload=exact_payload,
                noisy_payload=noisy_payload,
            )
            with self.assertRaisesRegex(
                HardwareValidationGateError,
                "fails the configured observable acceptance policy",
            ):
                self._run_gate(paths)

        noisy_payload = self._execution_payload("noisy_local", self.expected_values)
        noisy_payload["validation_assessment"]["passed"] = False
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self._write_artifacts(
                Path(temp_dir),
                exact_payload=exact_payload,
                noisy_payload=noisy_payload,
            )
            with self.assertRaisesRegex(
                HardwareValidationGateError,
                "stored assessment is missing or does not match",
            ):
                self._run_gate(paths)
