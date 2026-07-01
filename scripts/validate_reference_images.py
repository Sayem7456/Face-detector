from __future__ import annotations

import argparse
import json
import sys
from collections import OrderedDict
from dataclasses import dataclass, asdict
from pathlib import Path

import cv2
import numpy as np
import numpy.typing as npt

from src.config import AppConfig, load_config
from src.face_engine import FaceEngine, DetectionResult
from src.reference_scanner import scan_identities, SUPPORTED_EXTENSIONS


@dataclass
class ImageResult:
    path: str
    valid: bool
    reason: str | None = None
    num_faces: int | None = None
    detection_confidence: float | None = None
    face_width: int | None = None
    face_height: int | None = None


@dataclass
class IdentityReport:
    identity: str
    total: int
    valid: int
    rejected: int
    images: list[ImageResult]


def _read_image_safe(path: Path) -> npt.NDArray[np.uint8] | None:
    img = cv2.imread(str(path))
    if img is None:
        return None
    if img.size == 0:
        return None
    return img


def _suffix_allowed(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def validate_images(
    engine: FaceEngine,
    identities: OrderedDict[str, list[Path]],
    config: AppConfig,
) -> list[IdentityReport]:
    min_w = config.model.minimum_face_width
    min_h = config.model.minimum_face_height

    reports: list[IdentityReport] = []

    for identity, image_paths in identities.items():
        results: list[ImageResult] = []
        valid_count = 0

        for img_path in image_paths:
            if not _suffix_allowed(img_path):
                results.append(ImageResult(
                    path=str(img_path),
                    valid=False,
                    reason=f"Unsupported extension '{img_path.suffix}'",
                ))
                continue

            frame = _read_image_safe(img_path)
            if frame is None:
                results.append(ImageResult(
                    path=str(img_path),
                    valid=False,
                    reason="Unreadable or corrupt image",
                ))
                continue

            if frame.ndim != 3 or frame.shape[2] != 3:
                results.append(ImageResult(
                    path=str(img_path),
                    valid=False,
                    reason="Image is not a 3-channel color image",
                ))
                continue

            try:
                detections: list[DetectionResult] = engine.detect_and_embed(frame)
            except Exception as exc:
                results.append(ImageResult(
                    path=str(img_path),
                    valid=False,
                    reason=f"Face detection error: {exc}",
                ))
                continue

            if len(detections) == 0:
                results.append(ImageResult(
                    path=str(img_path),
                    valid=False,
                    reason="No face detected",
                ))
                continue

            if len(detections) > 1:
                substantial = [
                    d for d in detections
                    if d.detection_score >= config.model.minimum_detection_confidence
                ]
                if len(substantial) > 1:
                    results.append(ImageResult(
                        path=str(img_path),
                        valid=False,
                        reason=f"Multiple faces detected ({len(substantial)} substantial)",
                        num_faces=len(detections),
                    ))
                    continue

            det = detections[0]

            if det.face_width < min_w or det.face_height < min_h:
                results.append(ImageResult(
                    path=str(img_path),
                    valid=False,
                    reason=f"Face too small ({det.face_width}x{det.face_height}, "
                           f"minimum {min_w}x{min_h})",
                    num_faces=1,
                    detection_confidence=float(det.detection_score),
                    face_width=det.face_width,
                    face_height=det.face_height,
                ))
                continue

            results.append(ImageResult(
                path=str(img_path),
                valid=True,
                num_faces=1,
                detection_confidence=float(det.detection_score),
                face_width=det.face_width,
                face_height=det.face_height,
            ))
            valid_count += 1

        reports.append(IdentityReport(
            identity=identity,
            total=len(results),
            valid=valid_count,
            rejected=len(results) - valid_count,
            images=results,
        ))

    return reports


def _print_report(reports: list[IdentityReport]) -> None:
    print("=" * 60)
    print("  Reference Image Validation Report")
    print("=" * 60)
    print()

    any_invalid_identity = False

    for report in reports:
        status = "OK" if report.valid > 0 else "FAIL"
        if report.valid == 0:
            any_invalid_identity = True
        print(f"  {report.identity}  [{status}]")
        print(f"    Total:   {report.total}")
        print(f"    Valid:   {report.valid}")
        print(f"    Rejected: {report.rejected}")
        print()

        for img in report.images:
            label = "VALID" if img.valid else "REJECTED"
            extras = ""
            if img.detection_confidence is not None:
                extras += f"  conf={img.detection_confidence:.3f}"
            if img.face_width is not None:
                extras += f"  face={img.face_width}x{img.face_height}"
            reason = f"  reason={img.reason}" if img.reason else ""
            print(f"      {label}  {img.path}{extras}{reason}")

        print()

    print("=" * 60)

    if any_invalid_identity:
        print("  RESULT: FAIL — at least one identity has no valid images.")
    else:
        print("  RESULT: PASS — all identities have valid images.")

    print("=" * 60)


def write_json_report(reports: list[IdentityReport], path: str | Path) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "identity": r.identity,
            "total": r.total,
            "valid": r.valid,
            "rejected": r.rejected,
            "images": [asdict(img) for img in r.images],
        }
        for r in reports
    ]
    with open(report_path, "w") as f:
        json.dump(data, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate reference images for face enrollment."
    )
    parser.add_argument(
        "--config", "-c",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "--json-report",
        type=str,
        default=None,
        help="Write JSON validation report to this path",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Configuration file not found: {config_path}", file=sys.stderr)
        sys.exit(2)

    config = load_config(config_path)

    try:
        identities = scan_identities("data/reference_images")
    except NotADirectoryError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    if not identities:
        print(
            "No identity directories found under data/reference_images/.\n"
            "Create one directory per person, e.g.:\n"
            "  data/reference_images/person_1/\n"
            "  data/reference_images/person_2/",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        engine = FaceEngine(config)
    except Exception as exc:
        print(
            f"Model-dependent validation failed: unable to load face model.\n"
            f"Error: {exc}\n\n"
            f"Ensure InsightFace models are downloaded and available. "
            f"The first run usually downloads them automatically.",
            file=sys.stderr,
        )
        sys.exit(2)

    reports = validate_images(engine, identities, config)

    if args.json_report:
        write_json_report(reports, args.json_report)
        print(f"JSON report written to {args.json_report}")

    _print_report(reports)

    any_fail = any(r.valid == 0 for r in reports)
    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
