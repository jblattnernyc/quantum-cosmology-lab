"""Build the versioned Phase 6 repository milestone report."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from qclab.analysis.milestones import (
    collect_phase6_snapshot,
    default_phase6_milestone_id,
    default_phase6_milestone_report_path,
    write_phase6_milestone_report,
)


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Write the repository-level Phase 6 milestone report from the "
            "current official experiments and preserved IBM provenance."
        )
    )
    parser.add_argument(
        "--milestone-id",
        default=None,
        help="Override the default milestone identifier.",
    )
    parser.add_argument(
        "--date-label",
        default="20260402",
        help="UTC date label used when constructing the default milestone identifier.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Override the milestone-report output path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Collect the current Phase 6 snapshot and write the report."""

    parser = build_parser()
    args = parser.parse_args(argv)

    snapshot = collect_phase6_snapshot()
    milestone_id = args.milestone_id or default_phase6_milestone_id(
        snapshot.package_version,
        date_label=args.date_label,
    )
    output_path = (
        default_phase6_milestone_report_path(milestone_id)
        if args.output is None
        else Path(args.output).expanduser().resolve()
    )
    report_path = write_phase6_milestone_report(
        snapshot,
        milestone_id=milestone_id,
        output_path=output_path,
    )
    print(f"Wrote Phase 6 milestone report to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
