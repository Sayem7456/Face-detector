from __future__ import annotations

import os
import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest

from src.reference_scanner import (
    SUPPORTED_EXTENSIONS,
    is_safe_identity_name,
    scan_identities,
)


def _make_dummy_image(path: Path) -> None:
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(path), img)


class TestIsSafeIdentityName:
    def test_valid_name(self) -> None:
        assert is_safe_identity_name("Alice") is True

    def test_name_with_spaces(self) -> None:
        assert is_safe_identity_name("person 1") is True

    def test_empty_string(self) -> None:
        assert is_safe_identity_name("") is False

    def test_whitespace_only(self) -> None:
        assert is_safe_identity_name("   ") is False

    def test_dot_prefix(self) -> None:
        assert is_safe_identity_name(".hidden") is False

    def test_dotdot(self) -> None:
        assert is_safe_identity_name("..") is False

    def test_double_dot_in_name(self) -> None:
        assert is_safe_identity_name("a..b") is False

    def test_path_separator(self) -> None:
        assert is_safe_identity_name("a/b") is False
        assert is_safe_identity_name("a\\b") is False

    def test_special_chars(self) -> None:
        for ch in ':*?"<>|~#':
            assert is_safe_identity_name(f"person{ch}") is False


class TestScanIdentities:
    @pytest.fixture
    def tmp_base(self) -> Path:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir) / "refs"
            base.mkdir()
            yield base

    def test_no_directory(self) -> None:
        with pytest.raises(NotADirectoryError):
            scan_identities("/nonexistent/path")

    def test_empty_directory(self, tmp_base: Path) -> None:
        result = scan_identities(tmp_base)
        assert result == {}

    def test_single_identity(self, tmp_base: Path) -> None:
        identity_dir = tmp_base / "person_a"
        identity_dir.mkdir()
        _make_dummy_image(identity_dir / "img1.jpg")
        _make_dummy_image(identity_dir / "img2.png")

        result = scan_identities(tmp_base)
        assert list(result.keys()) == ["person_a"]
        assert len(result["person_a"]) == 2

    def test_deterministic_ordering(self, tmp_base: Path) -> None:
        for name in ["zelda", "alice", "bob"]:
            (tmp_base / name).mkdir()
        result = scan_identities(tmp_base)
        assert list(result.keys()) == ["alice", "bob", "zelda"]

    def test_deterministic_file_ordering(self, tmp_base: Path) -> None:
        identity_dir = tmp_base / "person_a"
        identity_dir.mkdir()
        for fname in ["z.jpg", "a.jpg", "m.jpg"]:
            _make_dummy_image(identity_dir / fname)
        result = scan_identities(tmp_base)
        paths = [p.name for p in result["person_a"]]
        assert paths == ["a.jpg", "m.jpg", "z.jpg"]

    def test_supported_extensions(self, tmp_base: Path) -> None:
        identity_dir = tmp_base / "p1"
        identity_dir.mkdir()
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            _make_dummy_image(identity_dir / f"img{ext}")
        for ext in [".JPG", ".JPEG"]:
            _make_dummy_image(identity_dir / f"img{ext}")
        result = scan_identities(tmp_base)
        found_exts = {p.suffix.lower() for p in result["p1"]}
        assert found_exts == {".jpg", ".jpeg", ".png", ".webp"}

    def test_unsupported_extensions_ignored(self, tmp_base: Path) -> None:
        identity_dir = tmp_base / "p1"
        identity_dir.mkdir()
        _make_dummy_image(identity_dir / "img.jpg")
        _make_dummy_image(identity_dir / "img.bmp")
        _make_dummy_image(identity_dir / "img.gif")
        result = scan_identities(tmp_base)
        assert len(result["p1"]) == 1

    def test_hidden_files_ignored(self, tmp_base: Path) -> None:
        identity_dir = tmp_base / "p1"
        identity_dir.mkdir()
        _make_dummy_image(identity_dir / "visible.jpg")
        _make_dummy_image(identity_dir / ".hidden.jpg")
        result = scan_identities(tmp_base)
        assert len(result["p1"]) == 1

    def test_hidden_directories_ignored(self, tmp_base: Path) -> None:
        (tmp_base / "visible").mkdir()
        _make_dummy_image(tmp_base / "visible" / "img.jpg")
        (tmp_base / ".hidden").mkdir()
        _make_dummy_image(tmp_base / ".hidden" / "img.jpg")
        result = scan_identities(tmp_base)
        assert list(result.keys()) == ["visible"]

    def test_multiple_identities(self, tmp_base: Path) -> None:
        for name in ["alice", "bob", "charlie"]:
            d = tmp_base / name
            d.mkdir()
            _make_dummy_image(d / "img.jpg")
        result = scan_identities(tmp_base)
        assert list(result.keys()) == ["alice", "bob", "charlie"]
        assert all(len(v) == 1 for v in result.values())

    def test_identity_with_no_images(self, tmp_base: Path) -> None:
        (tmp_base / "empty_person").mkdir()
        result = scan_identities(tmp_base)
        assert "empty_person" in result
        assert result["empty_person"] == []

    def test_unsafe_identity_names_skipped(self, tmp_base: Path) -> None:
        for name in [".hidden", "..", "a..b"]:
            if name == "..":
                continue
            Path(tmp_base / name).mkdir(parents=False, exist_ok=True)
        (tmp_base / "safe_person").mkdir()
        _make_dummy_image(tmp_base / "safe_person" / "img.jpg")
        result = scan_identities(tmp_base)
        assert list(result.keys()) == ["safe_person"]

    def test_case_insensitive_extensions(self, tmp_base: Path) -> None:
        identity_dir = tmp_base / "p1"
        identity_dir.mkdir()
        _make_dummy_image(identity_dir / "img1.JPG")
        _make_dummy_image(identity_dir / "img2.jpg")
        result = scan_identities(tmp_base)
        assert len(result["p1"]) == 2

    def test_mixed_case_extensions(self, tmp_base: Path) -> None:
        identity_dir = tmp_base / "p1"
        identity_dir.mkdir()
        _make_dummy_image(identity_dir / "img1.Jpg")
        _make_dummy_image(identity_dir / "img2.jPEG")
        _make_dummy_image(identity_dir / "img3.PNG")
        _make_dummy_image(identity_dir / "img4.webp")
        result = scan_identities(tmp_base)
        assert len(result["p1"]) == 4
