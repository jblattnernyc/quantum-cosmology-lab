"""Build the current official experiment repository report."""

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
    default_current_repository_report_path,
    write_current_repository_report,
)


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Write the phase-neutral current official experiment report from "
            "repository metadata and preserved experiment artifacts."
        )
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Override the report output path.",
    )
    parser.add_argument(
        "--generated-at-utc",
        default=None,
        help=(
            "Override the report generation timestamp with an ISO 8601 UTC "
            "value for deterministic output."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Collect the current repository snapshot and write the report."""

    parser = build_parser()
    args = parser.parse_args(argv)

    snapshot = collect_current_repository_snapshot(
        generated_at_utc=args.generated_at_utc,
    )
    output_path = (
        default_current_repository_report_path()
        if args.output is None
        else Path(args.output).expanduser().resolve()
    )
    report_path = write_current_repository_report(
        snapshot,
        output_path=output_path,
    )
    print(f"Wrote current repository report to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
