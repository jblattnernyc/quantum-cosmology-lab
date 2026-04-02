"""Tests for repository-aware path formatting."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.path_setup import ensure_src_path

ensure_src_path()

from qclab.utils.paths import repository_relative_path


class RepositoryPathFormattingTests(unittest.TestCase):
    """Verify conservative repository-relative path formatting."""

    def test_repository_relative_path_uses_repo_relative_strings_for_repo_artifacts(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(repository_relative_path(root / "README.md"), "README.md")
        self.assertEqual(
            repository_relative_path(root / "docs" / "operations" / "user-guide.md"),
            "docs/operations/user-guide.md",
        )

    def test_repository_relative_path_preserves_external_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            external_path = Path(temp_dir) / "external.json"
            self.assertEqual(
                repository_relative_path(external_path),
                str(external_path.resolve()),
            )
