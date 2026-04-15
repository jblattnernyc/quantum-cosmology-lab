"""Repository text-surface hygiene tests."""

from __future__ import annotations

import unittest
from pathlib import Path


FORBIDDEN_PREFIXES = (
    "/Users/john-blattner/Documents/QUANTUM COMPUTING/QUANTUM COSMOLOGY LAB",
    "/Users/john-blattner/Documents/QUANTUM%20COMPUTING/QUANTUM%20COSMOLOGY%20LAB",
)

FORBIDDEN_ACCOUNT_MARKERS = ("crn" + ":v1:",)


class RepositoryHygieneTests(unittest.TestCase):
    """Verify that publication-facing text files avoid local absolute-path coupling."""

    def test_public_text_surfaces_do_not_embed_local_repository_root(self) -> None:
        root = Path(__file__).resolve().parents[1]
        candidate_paths = [root / "README.md"]
        candidate_paths.extend((root / "docs").rglob("*.md"))
        candidate_paths.extend((root / "scripts").rglob("*.md"))
        candidate_paths.extend((root / "experiments").rglob("*.md"))
        candidate_paths.extend((root / "results" / "reports").rglob("*.md"))
        candidate_paths.extend((root / "data" / "processed" / "releases").glob("*.json"))
        candidate_paths.extend((root / "data" / "raw").glob("*/ibm_runtime_runs.jsonl"))

        for path in candidate_paths:
            text = path.read_text(encoding="utf-8")
            for prefix in FORBIDDEN_PREFIXES:
                with self.subTest(path=path, prefix=prefix):
                    self.assertNotIn(prefix, text)

    def test_tracked_ibm_provenance_does_not_embed_account_crns(self) -> None:
        root = Path(__file__).resolve().parents[1]
        candidate_paths = list((root / "data" / "raw").glob("*/ibm_runtime_metadata*.json"))
        candidate_paths.extend((root / "data" / "raw").glob("*/ibm_runtime_runs.jsonl"))
        candidate_paths.extend((root / "results" / "reports").glob("*/ibm_runtime_report*.md"))

        for path in candidate_paths:
            text = path.read_text(encoding="utf-8")
            for marker in FORBIDDEN_ACCOUNT_MARKERS:
                with self.subTest(path=path, marker=marker):
                    self.assertNotIn(marker, text)
