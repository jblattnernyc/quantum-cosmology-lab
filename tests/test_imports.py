"""Import integrity tests for the repository foundation."""

from __future__ import annotations

import importlib
import unittest

from tests.path_setup import ensure_src_path

ensure_src_path()


class ImportIntegrityTests(unittest.TestCase):
    """Verify that the foundational package modules import cleanly."""

    def test_core_modules_import(self) -> None:
        module_names = (
            "experiments.gut_toy_gauge",
            "experiments.minisuperspace_frw",
            "experiments.particle_creation_flrw",
            "qclab",
            "qclab.analysis",
            "qclab.analysis.milestones",
            "qclab.analysis.repository_state",
            "qclab.analysis.reporting",
            "qclab.backends",
            "qclab.backends.execution",
            "qclab.backends.hardware",
            "qclab.benchmarks",
            "qclab.benchmarks.scalar",
            "qclab.circuits",
            "qclab.encodings",
            "qclab.models",
            "qclab.observables",
            "qclab.observables.pauli",
            "qclab.plotting",
            "qclab.plotting.backend",
            "qclab.plotting.comparison",
            "qclab.utils",
            "qclab.utils.paths",
            "qclab.utils.runtime",
        )
        for module_name in module_names:
            with self.subTest(module=module_name):
                importlib.import_module(module_name)
