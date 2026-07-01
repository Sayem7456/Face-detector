from __future__ import annotations

import json
import tempfile
from collections import OrderedDict
from pathlib import Path
from unittest.mock import patch, MagicMock

import cv2
import numpy as np
import pytest

from src.config import AppConfig, ModelConfig
from src.face_engine import DetectionResult
from src.reference_scanner import scan_identities, SUPPORTED_EXTENSIONS
from scripts.validate_reference_images import (
    validate_images,
    write_json_report,
    _read_image_safe,
    _suffix_allowed,
)


def _make_dummy_image(path: Path) -> None:
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2.imwrite(str(path), img)


def _make_detection_result(
    score: float = 0.95,
    width: int = 150,
    height: int = 150,
) -> DetectionResult:
    return DetectionResult(
        bbox=(10, 10, 160, 160),
        detection_score=score,
        embedding=np.ones(512, dtype=np.float32),
        face_width=width,
        face_height=height,
    )


@pytest.fixture
def mock_engine() -> MagicMock:
    engine = MagicMock()
    engine.detect_and_embed.return_value = [_make_detection_result()]
    return engine


@pytest.fixture
def temp_ref_dir() -> Path:
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir) / "reference_images"
        base.mkdir()
        yield base


def test_read_image_safe_valid(temp_ref_dir: Path) -> None:
    p = temp_ref_dir / "test.jpg"
    _make_dummy_image(p)
    result = _read_image_safe(p)
    assert result is not None
    assert result.shape == (200, 200, 3)


def test_read_image_safe_nonexistent(temp_ref_dir: Path) -> None:
    p = temp_ref_dir / "nonexistent.jpg"
    result = _read_image_safe(p)
    assert result is None


def test_suffix_allowed() -> None:
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        assert _suffix_allowed(Path(f"img{ext}")) is True
    assert _suffix_allowed(Path("img.bmp")) is False
    assert _suffix_allowed(Path("img.gif")) is False
    assert _suffix_allowed(Path("img")) is False


class TestValidateImages:
    def _config(self) -> AppConfig:
        return AppConfig()

    def test_valid_image_accepted(self, mock_engine: MagicMock, temp_ref_dir: Path) -> None:
        identity_dir = temp_ref_dir / "alice"
        identity_dir.mkdir()
        _make_dummy_image(identity_dir / "img.jpg")

        identities = scan_identities(temp_ref_dir)
        config = self._config()

        reports = validate_images(mock_engine, identities, config)
        assert len(reports) == 1
        assert reports[0].identity == "alice"
        assert reports[0].valid == 1
        assert reports[0].rejected == 0
        assert reports[0].images[0].valid is True

    def test_zero_faces_rejected(self, mock_engine: MagicMock, temp_ref_dir: Path) -> None:
        mock_engine.detect_and_embed.return_value = []

        identity_dir = temp_ref_dir / "alice"
        identity_dir.mkdir()
        _make_dummy_image(identity_dir / "img.jpg")

        identities = scan_identities(temp_ref_dir)
        reports = validate_images(mock_engine, identities, self._config())
        assert reports[0].valid == 0
        assert reports[0].rejected == 1
        assert reports[0].images[0].reason == "No face detected"

    def test_multiple_faces_rejected(self, mock_engine: MagicMock, temp_ref_dir: Path) -> None:
        mock_engine.detect_and_embed.return_value = [
            _make_detection_result(score=0.9),
            _make_detection_result(score=0.85),
        ]

        identity_dir = temp_ref_dir / "alice"
        identity_dir.mkdir()
        _make_dummy_image(identity_dir / "img.jpg")

        identities = scan_identities(temp_ref_dir)
        reports = validate_images(mock_engine, identities, self._config())
        assert reports[0].valid == 0
        assert "Multiple faces" in reports[0].images[0].reason

    def test_small_face_rejected(self, mock_engine: MagicMock, temp_ref_dir: Path) -> None:
        mock_engine.detect_and_embed.return_value = [
            _make_detection_result(score=0.95, width=30, height=30),
        ]

        identity_dir = temp_ref_dir / "alice"
        identity_dir.mkdir()
        _make_dummy_image(identity_dir / "img.jpg")

        identities = scan_identities(temp_ref_dir)
        reports = validate_images(mock_engine, identities, self._config())
        assert reports[0].valid == 0
        assert "Face too small" in reports[0].images[0].reason

    def test_detection_confidence_recorded(self, mock_engine: MagicMock, temp_ref_dir: Path) -> None:
        mock_engine.detect_and_embed.return_value = [
            _make_detection_result(score=0.88),
        ]

        identity_dir = temp_ref_dir / "alice"
        identity_dir.mkdir()
        _make_dummy_image(identity_dir / "img.jpg")

        identities = scan_identities(temp_ref_dir)
        reports = validate_images(mock_engine, identities, self._config())
        assert reports[0].images[0].detection_confidence == pytest.approx(0.88)

    def test_unreadable_image_rejected(self, mock_engine: MagicMock, temp_ref_dir: Path) -> None:
        identity_dir = temp_ref_dir / "alice"
        identity_dir.mkdir()
        bad_path = identity_dir / "corrupt.jpg"
        bad_path.write_bytes(b"not an image")

        identities = scan_identities(temp_ref_dir)
        reports = validate_images(mock_engine, identities, self._config())
        assert reports[0].valid == 0
        assert "Unreadable" in reports[0].images[0].reason

    def test_unsupported_extension(self, mock_engine: MagicMock, temp_ref_dir: Path) -> None:
        identity_dir = temp_ref_dir / "alice"
        identity_dir.mkdir()
        bad_path = identity_dir / "img.bmp"
        bad_path.write_bytes(b"fake")

        identities = OrderedDict({"alice": [bad_path]})
        reports = validate_images(mock_engine, identities, self._config())
        assert reports[0].valid == 0
        assert "Unsupported extension" in reports[0].images[0].reason

    def test_multiple_identities_reports(self, mock_engine: MagicMock, temp_ref_dir: Path) -> None:
        for name in ["alice", "bob"]:
            d = temp_ref_dir / name
            d.mkdir()
            _make_dummy_image(d / "img.jpg")

        identities = scan_identities(temp_ref_dir)
        reports = validate_images(mock_engine, identities, self._config())
        assert len(reports) == 2
        assert all(r.valid == 1 for r in reports)

    def test_substantial_threshold_uses_config(self, mock_engine: MagicMock, temp_ref_dir: Path) -> None:
        cfg = AppConfig()
        cfg.model.minimum_detection_confidence = 0.60
        mock_engine.detect_and_embed.return_value = [
            _make_detection_result(score=0.65),
            _make_detection_result(score=0.75),
        ]

        identity_dir = temp_ref_dir / "alice"
        identity_dir.mkdir()
        _make_dummy_image(identity_dir / "img.jpg")

        identities = scan_identities(temp_ref_dir)
        reports = validate_images(mock_engine, identities, cfg)
        assert reports[0].valid == 0
        assert "Multiple faces" in reports[0].images[0].reason

    def test_substantial_threshold_uses_config_below(self, mock_engine: MagicMock, temp_ref_dir: Path) -> None:
        cfg = AppConfig()
        cfg.model.minimum_detection_confidence = 0.80
        mock_engine.detect_and_embed.return_value = [
            _make_detection_result(score=0.65),
            _make_detection_result(score=0.75),
        ]

        identity_dir = temp_ref_dir / "alice"
        identity_dir.mkdir()
        _make_dummy_image(identity_dir / "img.jpg")

        identities = scan_identities(temp_ref_dir)
        reports = validate_images(mock_engine, identities, cfg)
        assert reports[0].valid == 1

    def test_json_report_output(self, mock_engine: MagicMock, temp_ref_dir: Path) -> None:
        identity_dir = temp_ref_dir / "alice"
        identity_dir.mkdir()
        _make_dummy_image(identity_dir / "img.jpg")

        identities = scan_identities(temp_ref_dir)
        reports = validate_images(mock_engine, identities, self._config())

        json_path = temp_ref_dir / "report.json"
        write_json_report(reports, json_path)

        assert json_path.exists()
        with open(json_path) as f:
            loaded = json.load(f)
        assert len(loaded) == 1
        assert loaded[0]["identity"] == "alice"
        assert loaded[0]["valid"] == 1
        assert loaded[0]["images"][0]["valid"] is True

    def test_json_report_writes_multiple_identities(self, mock_engine: MagicMock, temp_ref_dir: Path) -> None:
        for name in ["alice", "bob"]:
            d = temp_ref_dir / name
            d.mkdir()
            _make_dummy_image(d / "img.jpg")

        identities = scan_identities(temp_ref_dir)
        reports = validate_images(mock_engine, identities, self._config())

        json_path = temp_ref_dir / "report.json"
        write_json_report(reports, json_path)

        with open(json_path) as f:
            loaded = json.load(f)
        assert len(loaded) == 2
        assert loaded[0]["identity"] == "alice"
        assert loaded[1]["identity"] == "bob"
        assert all(r["valid"] == 1 for r in loaded)
