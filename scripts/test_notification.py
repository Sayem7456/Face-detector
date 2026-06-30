#!/usr/bin/env python3
"""Test that notify-send is available and working."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Test desktop notifications via notify-send."
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Send a test notification (default: only check availability).",
    )
    parser.add_argument(
        "--title",
        default="Person Alert",
        help="Notification title (default: 'Person Alert').",
    )
    parser.add_argument(
        "--body",
        default="Notification system is working.",
        help="Notification body text.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    notify_path = shutil.which("notify-send")
    if notify_path is None:
        print(
            "ERROR: notify-send not found.\n"
            "Install it with:\n"
            "  sudo apt update && sudo apt install libnotify-bin",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"notify-send found at: {notify_path}")

    if args.send:
        cmd = [notify_path, args.title, args.body]
        try:
            result = subprocess.run(
                cmd,
                shell=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except subprocess.TimeoutExpired:
            print("ERROR: notify-send timed out after 10 seconds.", file=sys.stderr)
            sys.exit(2)
        except OSError as exc:
            print(f"ERROR: Failed to run notify-send: {exc}", file=sys.stderr)
            sys.exit(2)

        if result.returncode == 0:
            print(f"Notification sent: {args.title} / {args.body}")
        else:
            print(
                f"notify-send exited with code {result.returncode}:\n"
                f"  stderr: {result.stderr.strip()}",
                file=sys.stderr,
            )
            sys.exit(result.returncode)
    else:
        print("notify-send is available (use --send to send a test notification).")


if __name__ == "__main__":
    main()
