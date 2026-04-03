"""IBM Runtime execution for the Planck-epoch-motivated minisuperspace model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from experiments.minisuperspace_frw.run_ibm import run_ibm_hardware as _run_ibm_hardware

from experiments.planck_epoch_minisuperspace.common import DEFAULT_CONFIG_PATH


def run_ibm_hardware(
    *,
    config_path: str = str(DEFAULT_CONFIG_PATH),
    backend_name: str | None = None,
    instance: str | None = None,
    channel: str | None = None,
    mitigation_enabled: bool = False,
    resilience_level: int | None = None,
    local_testing_backend: str | None = None,
) -> dict[str, str]:
    """Execute the IBM Runtime path after exact-local and noisy-local validation."""

    return _run_ibm_hardware(
        config_path=config_path,
        backend_name=backend_name,
        instance=instance,
        channel=channel,
        mitigation_enabled=mitigation_enabled,
        resilience_level=resilience_level,
        local_testing_backend=local_testing_backend,
    )


def main(argv: list[str] | None = None) -> int:
    """Run the IBM Runtime hardware workflow."""

    parser = argparse.ArgumentParser(
        description=(
            "Run the IBM Runtime Planck-epoch-motivated reduced minisuperspace workflow."
        )
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--backend-name", default=None)
    parser.add_argument("--instance", default=None)
    parser.add_argument("--channel", default=None)
    parser.add_argument(
        "--mitigation",
        action="store_true",
        help="Enable at least the default resilience policy for the IBM Runtime request.",
    )
    parser.add_argument(
        "--resilience-level",
        type=int,
        choices=(0, 1, 2),
        default=None,
        help="Override the configured IBM Runtime resilience level.",
    )
    parser.add_argument(
        "--local-testing-backend",
        default=None,
        help=(
            "Instantiate a fake backend from qiskit_ibm_runtime.fake_provider for "
            "credential-free IBM Runtime local testing mode."
        ),
    )
    args = parser.parse_args(argv)
    outputs = run_ibm_hardware(
        config_path=args.config,
        backend_name=args.backend_name,
        instance=args.instance,
        channel=args.channel,
        mitigation_enabled=args.mitigation,
        resilience_level=args.resilience_level,
        local_testing_backend=args.local_testing_backend,
    )
    for label, path in outputs.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
