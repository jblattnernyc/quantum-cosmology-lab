"""Save an IBM Runtime account from environment variables without storing secrets in code."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))

from scripts.ibm_runtime.common import save_runtime_account


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Save an IBM Runtime account using environment variables rather than "
            "tracked source files."
        )
    )
    parser.add_argument("--token-env-var", default="QISKIT_IBM_TOKEN")
    parser.add_argument("--channel", default=None)
    parser.add_argument("--instance", default=None)
    parser.add_argument("--url", default=None)
    parser.add_argument("--name", default=None)
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Do not overwrite an existing saved account entry of the same name.",
    )
    parser.add_argument(
        "--no-set-default",
        action="store_true",
        help="Save the account without making it the default Runtime account.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Save the IBM Runtime account and print a non-secret summary."""

    parser = build_parser()
    args = parser.parse_args(argv)
    summary = save_runtime_account(
        token_env_var=args.token_env_var,
        channel=args.channel,
        instance=args.instance,
        url=args.url,
        name=args.name,
        overwrite=not args.no_overwrite,
        set_as_default=not args.no_set_default,
    )
    print("IBM Runtime account saved successfully.")
    print(f"Channel: {summary['channel']}")
    print(f"Instance configured: {summary['has_instance']}")
    print(f"Custom URL configured: {summary['has_url']}")
    print(f"Saved account path: {summary['saved_account_path']}")
    print(f"Set as default: {summary['set_as_default']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
