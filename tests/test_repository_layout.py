"""Repository structure tests for the implemented repository baseline."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


class RepositoryLayoutTests(unittest.TestCase):
    """Verify that the baseline repository files and directories exist."""

    def test_required_paths_exist(self) -> None:
        root = Path(__file__).resolve().parents[1]
        required_paths = (
            root / "README.md",
            root / "LICENSE",
            root / "NOTICE",
            root / "CITATION.cff",
            root / ".gitattributes",
            root / ".gitignore",
            root / "pyproject.toml",
            root / "CHANGELOG.md",
            root / "Makefile",
            root / ".github" / "workflows" / "ci.yml",
            root / "docs" / "architecture" / "overview.md",
            root / "docs" / "methods" / "experiment-standard.md",
            root / "docs" / "methods" / "figure-and-table-style-guide.md",
            root / "docs" / "operations" / "user-guide.md",
            root / "docs" / "operations" / "ibm-runtime-setup.md",
            root / "docs" / "operations" / "results-and-provenance.md",
            root / "docs" / "operations" / "internal-review-checklist.md",
            root / "docs" / "operations" / "replication-checklist.md",
            root / "docs" / "operations" / "archival-release-workflow.md",
            root / "docs" / "references" / "citation-and-bibliography-policy.md",
            root / "scripts" / "ibm_runtime" / "README.md",
            root / "scripts" / "ibm_runtime" / "save_account_from_env.py",
            root / "scripts" / "ibm_runtime" / "check_account.py",
            root / "scripts" / "release" / "README.md",
            root / "scripts" / "release" / "build_current_repository_report.py",
            root
            / "scripts"
            / "release"
            / "build_current_official_experiment_manifest.py",
            root / "scripts" / "release" / "build_phase6_milestone_report.py",
            root / "scripts" / "release" / "build_archival_release_manifest.py",
            root / "src" / "qclab" / "__init__.py",
            root / "experiments" / "minisuperspace_frw" / "README.md",
            root / "experiments" / "particle_creation_flrw" / "README.md",
            root / "experiments" / "gut_toy_gauge" / "README.md",
            root
            / "results"
            / "reports"
            / "repository"
            / "current_official_experiments.md",
            root
            / "results"
            / "reports"
            / "repository"
            / "v1.1.0-current-20260403.md",
            root / "results" / "reports" / "milestones" / "v1.0.0-phase6-20260402.md",
            root
            / "data"
            / "processed"
            / "repository"
            / "current_official_experiments.json",
            root
            / "data"
            / "processed"
            / "repository"
            / "v1.1.0-current-20260403_manifest.json",
            root
            / "data"
            / "processed"
            / "releases"
            / "v1.0.0-phase6-20260402_manifest.json",
        )
        for path in required_paths:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), f"Missing required path: {path}")

    def test_citation_metadata_matches_live_package_release(self) -> None:
        root = Path(__file__).resolve().parents[1]
        citation_text = (root / "CITATION.cff").read_text(encoding="utf-8")
        init_text = (root / "src" / "qclab" / "__init__.py").read_text(encoding="utf-8")

        citation_version_match = re.search(r'^version:\s*"([^"]+)"$', citation_text, re.MULTILINE)
        citation_date_match = re.search(
            r'^date-released:\s*"([^"]+)"$',
            citation_text,
            re.MULTILINE,
        )
        package_version_match = re.search(
            r'__version__\s*=\s*"([^"]+)"',
            init_text,
        )

        self.assertIsNotNone(citation_version_match)
        self.assertIsNotNone(citation_date_match)
        self.assertIsNotNone(package_version_match)
        self.assertEqual(citation_version_match.group(1), package_version_match.group(1))
        self.assertEqual(citation_date_match.group(1), "2026-04-03")
