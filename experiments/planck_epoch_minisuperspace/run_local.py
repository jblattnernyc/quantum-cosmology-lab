"""Exact local execution for the Planck-epoch-motivated minisuperspace model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from experiments.minisuperspace_frw.run_local import run_exact_local as _run_exact_local

from experiments.planck_epoch_minisuperspace.common import DEFAULT_CONFIG_PATH


def run_exact_local(config_path: str = str(DEFAULT_CONFIG_PATH)) -> dict[str, str]:
    """Execute the exact local reference path and persist its outputs."""

    return _run_exact_local(config_path)


def main(argv: list[str] | None = None) -> int:
    """Run the exact local experiment path."""

    parser = argparse.ArgumentParser(
        description=(
            "Run the exact local Planck-epoch-motivated reduced minisuperspace workflow."
        )
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    outputs = run_exact_local(args.config)
    for label, path in outputs.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
