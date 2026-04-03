"""Build the current official experiment manifest."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from qclab.analysis.repository_state import (
    collect_current_repository_snapshot,
    default_current_official_experiment_manifest_path,
    default_current_repository_report_path,
    write_current_official_experiment_manifest,
)


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Write the phase-neutral machine-readable manifest for the "
            "current official experiment state of the repository."
        )
    )
    parser.add_argument(
        "--report",
        default=None,
        help=(
            "Path to the current repository report referenced by the manifest. "
            "When omitted, the default current report path is used."
        ),
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Override the manifest output path.",
    )
    parser.add_argument(
        "--generated-at-utc",
        default=None,
        help=(
            "Override the manifest generation timestamp with an ISO 8601 UTC "
            "value for deterministic output."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Collect the current repository snapshot and write the manifest."""

    parser = build_parser()
    args = parser.parse_args(argv)

    snapshot = collect_current_repository_snapshot(
        generated_at_utc=args.generated_at_utc,
    )
    report_path = (
        default_current_repository_report_path()
        if args.report is None
        else Path(args.report).expanduser().resolve()
    )
    output_path = (
        default_current_official_experiment_manifest_path()
        if args.output is None
        else Path(args.output).expanduser().resolve()
    )
    manifest_path = write_current_official_experiment_manifest(
        snapshot,
        report_path=report_path,
        output_path=output_path,
    )
    print(f"Wrote current official experiment manifest to {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
