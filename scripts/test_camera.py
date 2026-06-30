#!/usr/bin/env python3
"""Test webcam capture and preview."""

from __future__ import annotations

import argparse
import sys
import time

import cv2

from src.config import load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Test webcam access and preview."
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Camera source (index or device path). Default: from config.yaml",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Requested frame width. Default: from config.yaml",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help="Requested frame height. Default: from config.yaml",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Exit after this many seconds (default: 10). 0 = no limit.",
    )
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="Run without an OpenCV preview window.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        cfg = load_config()
    except FileNotFoundError:
        cfg = None

    source: int | str = 0
    width: int = 640
    height: int = 480

    if cfg is not None:
        source = cfg.camera.source
        width = cfg.camera.width
        height = cfg.camera.height

    if args.source is not None:
        source = _parse_source(args.source)
    if args.width is not None:
        width = args.width
    if args.height is not None:
        height = args.height

    cap = cv2.VideoCapture(source)
    preview_name = "Camera Test (press Q to quit)"
    start = time.monotonic()
    frame_count = 0

    try:
        if not cap.isOpened():
            print(
                f"ERROR: Could not open camera source: {source}",
                file=sys.stderr,
            )
            sys.exit(1)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera source: {source}")
        print(f"Requested resolution: {width}x{height}")
        print(f"Actual resolution:    {actual_width}x{actual_height}")
        while True:
            if args.timeout > 0 and (time.monotonic() - start) >= args.timeout:
                print(f"Timeout reached ({args.timeout}s).")
                break

            ret, frame = cap.read()
            if not ret:
                print("ERROR: Failed to read frame.", file=sys.stderr)
                break

            frame_count += 1

            if not args.no_preview:
                cv2.imshow(preview_name, frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == ord("Q"):
                    print("Quit key pressed.")
                    break

    except KeyboardInterrupt:
        print("\nInterrupted.")

    finally:
        cap.release()
        if not args.no_preview:
            cv2.destroyWindow(preview_name)

    elapsed = time.monotonic() - start
    print(f"Frames received: {frame_count}")
    if elapsed > 0:
        print(f"Elapsed time:     {elapsed:.2f}s")
        print(f"Measured FPS:     {frame_count / elapsed:.1f}")
    else:
        print("Measured FPS:     N/A")


def _parse_source(value: str) -> int | str:
    try:
        return int(value)
    except ValueError:
        return value


if __name__ == "__main__":
    main()
