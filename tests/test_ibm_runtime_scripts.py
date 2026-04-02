"""Tests for credential-safe IBM Runtime helper scripts."""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ibm_runtime import check_account as check_account_script
from scripts.ibm_runtime import common
from scripts.ibm_runtime import save_account_from_env as save_account_script


class _NamedBackend:
    def __init__(self, name: str) -> None:
        self.name = name


class _FakeRuntimeService:
    last_init_kwargs: dict[str, object] | None = None
    last_save_kwargs: dict[str, object] | None = None

    def __init__(self, **kwargs: object) -> None:
        type(self).last_init_kwargs = dict(kwargs)

    @classmethod
    def save_account(cls, **kwargs: object) -> None:
        cls.last_save_kwargs = dict(kwargs)

    def active_account(self) -> dict[str, object]:
        init_kwargs = type(self).last_init_kwargs or {}
        return {
            "channel": init_kwargs.get("channel", "ibm_quantum_platform"),
            "instance": init_kwargs.get("instance", "instance-set"),
        }

    def backends(self) -> list[_NamedBackend]:
        return [
            _NamedBackend("ibm_torino"),
            _NamedBackend("ibm_fez"),
            _NamedBackend("ibm_kingston"),
        ]


class IBMRuntimeCommonTests(unittest.TestCase):
    """Validate the helper-layer behavior without live network access."""

    def test_load_runtime_credentials_from_environment_uses_defaults(self) -> None:
        with patch.dict(
            os.environ,
            {"QISKIT_IBM_TOKEN": "secret-token"},
            clear=False,
        ):
            credentials = common.load_runtime_credentials_from_environment()
        self.assertEqual(credentials.token, "secret-token")
        self.assertEqual(credentials.channel, "ibm_quantum_platform")
        self.assertIsNone(credentials.instance)
        self.assertIsNone(credentials.url)

    def test_load_runtime_credentials_from_environment_requires_token(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "QISKIT_IBM_TOKEN"):
                common.load_runtime_credentials_from_environment()

    def test_save_runtime_account_uses_environment_backed_token(self) -> None:
        with patch.dict(
            os.environ,
            {
                "QISKIT_IBM_TOKEN": "secret-token",
                "QISKIT_IBM_INSTANCE": "instance-crn",
            },
            clear=False,
        ):
            summary = common.save_runtime_account(
                service_cls=_FakeRuntimeService,
                name="lab-account",
            )
        self.assertEqual(
            _FakeRuntimeService.last_save_kwargs,
            {
                "channel": "ibm_quantum_platform",
                "token": "secret-token",
                "instance": "instance-crn",
                "url": None,
                "name": "lab-account",
                "overwrite": True,
                "set_as_default": True,
            },
        )
        self.assertTrue(summary["has_instance"])
        self.assertTrue(str(summary["saved_account_path"]).endswith(".qiskit/qiskit-ibm.json"))

    def test_check_runtime_account_supports_saved_account_mode(self) -> None:
        summary = common.check_runtime_account(
            service_factory=_FakeRuntimeService,
            backend_limit=2,
        )
        self.assertEqual(summary["account_source"], "saved")
        self.assertEqual(summary["channel"], "ibm_quantum_platform")
        self.assertTrue(summary["has_instance"])
        self.assertEqual(summary["backend_count"], 3)
        self.assertEqual(summary["sample_backends"], ["ibm_fez", "ibm_kingston"])
        self.assertEqual(_FakeRuntimeService.last_init_kwargs, {})

    def test_check_runtime_account_supports_environment_mode(self) -> None:
        with patch.dict(
            os.environ,
            {
                "QISKIT_IBM_TOKEN": "secret-token",
                "QISKIT_IBM_CHANNEL": "ibm_quantum_platform",
                "QISKIT_IBM_INSTANCE": "instance-crn",
            },
            clear=False,
        ):
            summary = common.check_runtime_account(
                use_saved_account=False,
                service_factory=_FakeRuntimeService,
            )
        self.assertEqual(summary["account_source"], "environment")
        self.assertEqual(
            _FakeRuntimeService.last_init_kwargs,
            {
                "channel": "ibm_quantum_platform",
                "token": "secret-token",
                "instance": "instance-crn",
            },
        )


class IBMRuntimeScriptEntryPointTests(unittest.TestCase):
    """Validate the script-facing entry points and their user-visible summaries."""

    def test_save_account_script_main_prints_non_secret_summary(self) -> None:
        with patch.object(
            save_account_script,
            "save_runtime_account",
            return_value={
                "channel": "ibm_quantum_platform",
                "has_instance": True,
                "has_url": False,
                "saved_account_path": "/tmp/qiskit-ibm.json",
                "set_as_default": True,
            },
        ) as mocked_save:
            stream = io.StringIO()
            with redirect_stdout(stream):
                exit_code = save_account_script.main([])
        self.assertEqual(exit_code, 0)
        mocked_save.assert_called_once()
        output = stream.getvalue()
        self.assertIn("IBM Runtime account saved successfully.", output)
        self.assertIn("Instance configured: True", output)
        self.assertNotIn("token", output.lower())

    def test_check_account_script_main_prints_backend_summary(self) -> None:
        with patch.object(
            check_account_script,
            "check_runtime_account",
            return_value={
                "account_source": "saved",
                "channel": "ibm_quantum_platform",
                "has_instance": True,
                "backend_count": 4,
                "sample_backends": ["ibm_fez", "ibm_kingston"],
                "saved_account_path": "/tmp/qiskit-ibm.json",
            },
        ) as mocked_check:
            stream = io.StringIO()
            with redirect_stdout(stream):
                exit_code = check_account_script.main([])
        self.assertEqual(exit_code, 0)
        mocked_check.assert_called_once()
        output = stream.getvalue()
        self.assertIn("IBM Runtime authentication succeeded.", output)
        self.assertIn("Sample backends: ibm_fez, ibm_kingston", output)

