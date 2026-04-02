"""Build the Phase 6 archival release manifest."""

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
    default_archival_release_manifest_path,
    default_phase6_milestone_id,
    default_phase6_milestone_report_path,
    write_archival_release_manifest,
)


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Write the machine-readable archival release manifest for the "
            "current Phase 6 repository baseline."
        )
    )
    parser.add_argument(
        "--release-id",
        default=None,
        help="Override the default archival release identifier.",
    )
    parser.add_argument(
        "--date-label",
        default="20260402",
        help="UTC date label used when constructing the default release identifier.",
    )
    parser.add_argument(
        "--milestone-report",
        default=None,
        help=(
            "Path to the milestone report referenced by the manifest. When "
            "omitted, the default Phase 6 milestone-report path is used."
        ),
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Override the archival-manifest output path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Collect the Phase 6 snapshot and write the archival manifest."""

    parser = build_parser()
    args = parser.parse_args(argv)

    snapshot = collect_phase6_snapshot()
    release_id = args.release_id or default_phase6_milestone_id(
        snapshot.package_version,
        date_label=args.date_label,
    )
    milestone_report_path = (
        default_phase6_milestone_report_path(release_id)
        if args.milestone_report is None
        else Path(args.milestone_report).expanduser().resolve()
    )
    output_path = (
        default_archival_release_manifest_path(release_id)
        if args.output is None
        else Path(args.output).expanduser().resolve()
    )
    manifest_path = write_archival_release_manifest(
        snapshot,
        release_id=release_id,
        milestone_report_path=milestone_report_path,
        output_path=output_path,
    )
    print(f"Wrote archival release manifest to {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
