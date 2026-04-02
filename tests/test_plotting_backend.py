"""Tests for non-interactive plotting backend configuration."""

from __future__ import annotations

import sys
import unittest
from unittest.mock import patch

from tests.path_setup import ensure_src_path

ensure_src_path()

from qclab.plotting.backend import configure_noninteractive_backend


class PlottingBackendTests(unittest.TestCase):
    """Verify plotting backend selection for repository analysis scripts."""

    def test_backend_defaults_to_agg_without_environment_override(self) -> None:
        pyplot_module = sys.modules.pop("matplotlib.pyplot", None)
        try:
            with patch.dict("os.environ", {}, clear=True), patch(
                "matplotlib.use"
            ) as mocked_use:
                configure_noninteractive_backend()
        finally:
            if pyplot_module is not None:
                sys.modules["matplotlib.pyplot"] = pyplot_module

        mocked_use.assert_called_once_with("Agg")

    def test_backend_respects_explicit_mplbackend_override(self) -> None:
        with patch.dict("os.environ", {"MPLBACKEND": "pdf"}, clear=True), patch(
            "matplotlib.use"
        ) as mocked_use:
            configure_noninteractive_backend()

        mocked_use.assert_not_called()
