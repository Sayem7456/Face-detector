#!/usr/bin/env python3
"""Smoke test for InsightFace face-analysis model.

Verifies the model loads on CPU. If an image path is supplied, performs
detection and reports results.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2

from src.config import load_config
from src.face_engine import FaceEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Smoke-test the InsightFace face model."
    )
    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="Path to an image file for face detection.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(
            f"ERROR: Configuration file not found: {args.config}",
            file=sys.stderr,
        )
        sys.exit(1)
    except ValueError as exc:
        print(f"ERROR: Invalid configuration: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Model provider: {config.model.provider}")
    print(f"Detection size: {config.model.detection_size}")
    print("Loading InsightFace model…", end=" ", flush=True)

    try:
        engine = FaceEngine(config)
    except Exception as exc:
        print(f"\nERROR: Failed to load face model: {exc}", file=sys.stderr)
        print(
            "This may require a network download of model assets "
            "(~150–300 MB).",
            file=sys.stderr,
        )
        sys.exit(1)

    print("OK")
    print(f"  {engine}")

    if args.image is not None:
        img_path = Path(args.image)
        if not img_path.is_file():
            print(f"ERROR: Image not found: {img_path}", file=sys.stderr)
            sys.exit(1)

        frame = cv2.imread(str(img_path))
        if frame is None:
            print(f"ERROR: Could not read image: {img_path}", file=sys.stderr)
            sys.exit(1)

        print(f"Processing: {img_path} ({frame.shape[1]}x{frame.shape[0]})")
        try:
            detections = engine.detect_and_embed(frame)
        except Exception as exc:
            print(f"ERROR: Detection failed: {exc}", file=sys.stderr)
            sys.exit(1)

        print(f"Faces detected: {len(detections)}")
        for i, det in enumerate(detections):
            x1, y1, x2, y2 = det.bbox
            print(
                f"  Face {i + 1}: "
                f"bbox=({x1},{y1},{x2},{y2}) "
                f"size={det.face_width}x{det.face_height} "
                f"confidence={det.detection_score:.3f} "
                f"embedding_dim={len(det.embedding)}"
            )
    else:
        print("No image supplied — model load verified only.")


if __name__ == "__main__":
    main()
