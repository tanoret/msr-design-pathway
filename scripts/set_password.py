#!/usr/bin/env python3
from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.auth_utils import hash_password


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create or rotate the Project-MSR Streamlit password hash."
    )
    parser.add_argument(
        "--password",
        help="Password to hash. Omit to enter it securely at the prompt.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".streamlit/secrets.toml"),
        help="Secrets file to write (default: .streamlit/secrets.toml).",
    )
    parser.add_argument(
        "--session-timeout-minutes",
        type=int,
        default=720,
        help="Authenticated idle-session timeout in minutes.",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=5,
        help="Failed attempts before temporary lockout.",
    )
    parser.add_argument(
        "--lockout-seconds",
        type=int,
        default=30,
        help="Temporary lockout duration in seconds.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    password = args.password
    if password is None:
        first = getpass.getpass("New Project-MSR password: ")
        second = getpass.getpass("Confirm password: ")
        if first != second:
            raise SystemExit("Passwords do not match.")
        password = first
    if not password:
        raise SystemExit("Password must not be empty.")

    encoded = hash_password(password)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "[auth]\n"
        f'password_hash = "{encoded}"\n'
        f"session_timeout_minutes = {max(5, args.session_timeout_minutes)}\n"
        f"max_attempts = {max(1, args.max_attempts)}\n"
        f"lockout_seconds = {max(1, args.lockout_seconds)}\n"
    )
    args.output.write_text(content, encoding="utf-8")
    print(f"Wrote password hash configuration to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
