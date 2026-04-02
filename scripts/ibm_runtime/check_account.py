"""Check IBM Runtime account connectivity without printing secrets."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))

from scripts.ibm_runtime.common import check_runtime_account


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Check IBM Runtime connectivity using either the saved local account "
            "or credentials supplied through environment variables."
        )
    )
    parser.add_argument(
        "--use-env-account",
        action="store_true",
        help=(
            "Authenticate directly from environment variables rather than using "
            "the saved local Runtime account."
        ),
    )
    parser.add_argument("--token-env-var", default="QISKIT_IBM_TOKEN")
    parser.add_argument("--channel", default=None)
    parser.add_argument("--instance", default=None)
    parser.add_argument("--url", default=None)
    parser.add_argument("--backend-limit", type=int, default=5)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate the IBM Runtime account and print a concise summary."""

    parser = build_parser()
    args = parser.parse_args(argv)
    summary = check_runtime_account(
        use_saved_account=not args.use_env_account,
        token_env_var=args.token_env_var,
        channel=args.channel,
        instance=args.instance,
        url=args.url,
        backend_limit=args.backend_limit,
    )
    print("IBM Runtime authentication succeeded.")
    print(f"Account source: {summary['account_source']}")
    print(f"Channel: {summary['channel']}")
    print(f"Instance configured: {summary['has_instance']}")
    print(f"Accessible backend count: {summary['backend_count']}")
    if summary["sample_backends"]:
        print("Sample backends: " + ", ".join(summary["sample_backends"]))
    print(f"Saved account path: {summary['saved_account_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
