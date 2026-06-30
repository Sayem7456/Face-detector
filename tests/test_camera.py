from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def test_camera_release_on_clean_exit() -> None:
    """Camera's release() should be called even on clean exit."""
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (False, None)

    with patch("cv2.VideoCapture", return_value=mock_cap):
        with patch("cv2.imshow"):
            with patch("cv2.waitKey", return_value=ord("q")):
                from scripts.test_camera import main

                main(["--source", "9", "--no-preview", "--timeout", "1"])

    mock_cap.release.assert_called_once()


def test_camera_release_on_keyboard_interrupt() -> None:
    """Camera's release() should be called on KeyboardInterrupt."""
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.side_effect = KeyboardInterrupt()

    with patch("cv2.VideoCapture", return_value=mock_cap):
        with patch("cv2.destroyWindow"):
            from scripts.test_camera import main

            main(["--source", "9", "--no-preview", "--timeout", "1"])

    mock_cap.release.assert_called_once()


def test_camera_returns_nonzero_releases_on_failure() -> None:
    """Camera failure should exit with code 1 and release the handle."""
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = False

    with patch("cv2.VideoCapture", return_value=mock_cap):
        with pytest.raises(SystemExit) as exc_info:
            from scripts.test_camera import main

            main(["--source", "9", "--no-preview", "--timeout", "1"])

    assert exc_info.value.code == 1
    mock_cap.release.assert_called_once()


def test_camera_read_failure_breaks_loop() -> None:
    """A failed read should break the capture loop."""
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (False, None)

    with patch("cv2.VideoCapture", return_value=mock_cap):
        with patch("cv2.destroyWindow"):
            from scripts.test_camera import main

            main(["--source", "9", "--no-preview", "--timeout", "1"])

    assert mock_cap.read.called


@pytest.mark.manual
def test_camera_hardware_real() -> None:
    """Open the real camera device and read one frame (manual test)."""
    import cv2

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        pytest.skip("No camera available")
    try:
        ret, frame = cap.read()
        assert ret, "Failed to read frame"
        assert frame is not None
        assert frame.shape[0] > 0
        assert frame.shape[1] > 0
    finally:
        cap.release()
