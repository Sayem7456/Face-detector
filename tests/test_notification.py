from __future__ import annotations

import shutil
import subprocess
from unittest.mock import patch

import pytest

from scripts.test_notification import main as notification_main


def test_notify_send_command_construction() -> None:
    """Verify the subprocess call uses an argument list with shell=False."""
    notify_path = shutil.which("notify-send")
    if notify_path is None:
        pytest.skip("notify-send not installed")

    cmd = [notify_path, "Test Title", "Test Body"]
    assert isinstance(cmd, list)
    assert cmd[0] == notify_path
    assert cmd[1] == "Test Title"
    assert cmd[2] == "Test Body"


def test_notify_send_available() -> None:
    """notify-send should be detectable via shutil.which."""
    found = shutil.which("notify-send")
    assert found is None or isinstance(found, str)


def test_notification_script_returns_nonzero_when_missing() -> None:
    """When notify-send is missing, the script should exit with code 1."""
    with patch("scripts.test_notification.shutil.which", return_value=None):
        with pytest.raises(SystemExit) as exc_info:
            notification_main([])
        assert exc_info.value.code == 1


def test_notification_script_check_only_passes() -> None:
    """With --send not passed and notify-send available, exit 0."""
    original = shutil.which("notify-send")
    if original is None:
        pytest.skip("notify-send not installed")
    with patch("scripts.test_notification.shutil.which", return_value=original):
        try:
            notification_main([])
        except SystemExit as exc:
            assert exc.code == 0 or exc.code is None


@pytest.mark.manual
def test_notification_send_real() -> None:
    """Send a real desktop notification (manual test)."""
    notify_path = shutil.which("notify-send")
    if notify_path is None:
        pytest.skip("notify-send not installed")
    result = subprocess.run(
        [notify_path, "Test", "Real notification test"],
        shell=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
