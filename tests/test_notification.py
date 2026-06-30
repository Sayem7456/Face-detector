from __future__ import annotations

import subprocess
from unittest.mock import patch

import pytest

from scripts.test_notification import main as notification_main


def test_notification_sends_via_subprocess() -> None:
    """Verify that --send calls subprocess.run with the correct command."""
    with patch("scripts.test_notification.shutil.which", return_value="/usr/bin/notify-send"):
        with patch("scripts.test_notification.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            notification_main(["--send", "--title", "T", "--body", "B"])

    mock_run.assert_called_once_with(
        ["/usr/bin/notify-send", "T", "B"],
        shell=False,
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_notification_script_returns_nonzero_when_missing() -> None:
    """When notify-send is missing, the script should exit with code 1."""
    with patch("scripts.test_notification.shutil.which", return_value=None):
        with pytest.raises(SystemExit) as exc_info:
            notification_main([])
        assert exc_info.value.code == 1


def test_notification_check_only_exits_zero() -> None:
    """Without --send and with notify-send available, exit cleanly (code 0)."""
    with patch("scripts.test_notification.shutil.which", return_value="/usr/bin/notify-send"):
        with patch("scripts.test_notification.subprocess.run"):
            try:
                notification_main([])
            except SystemExit as exc:
                assert exc.code == 0
            else:
                pass  # normal return without exit is also acceptable


@pytest.mark.manual
def test_notification_send_real() -> None:
    """Send a real desktop notification (manual test)."""
    import shutil

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
