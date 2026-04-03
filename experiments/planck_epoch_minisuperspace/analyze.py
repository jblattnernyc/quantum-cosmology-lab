"""Analysis for the Planck-epoch-motivated minisuperspace model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from experiments.minisuperspace_frw.analyze import run_analysis as _run_analysis

from experiments.planck_epoch_minisuperspace.common import DEFAULT_CONFIG_PATH


def run_analysis(config_path: str = str(DEFAULT_CONFIG_PATH)) -> dict[str, str]:
    """Analyze benchmarked exact and noisy outputs for the experiment."""

    return _run_analysis(config_path)


def main(argv: list[str] | None = None) -> int:
    """Run the experiment analysis workflow."""

    parser = argparse.ArgumentParser(
        description=(
            "Analyze the Planck-epoch-motivated reduced minisuperspace benchmarked outputs."
        )
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    outputs = run_analysis(args.config)
    for label, path in outputs.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
