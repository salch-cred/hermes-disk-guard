"""Offline tests for the disk-guard skill (no filesystem or network I/O)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import check_disk  # noqa: E402

GIB = check_disk.GIB


def test_render_status_formats_gib_and_percent():
    row = check_disk.render_status("C:\\", 500 * GIB, 250 * GIB, 250 * GIB)
    assert "| `C:\\` |" in row
    assert "500.0 GiB" in row
    assert "250.0 GiB" in row
    assert "50.0%" in row


def test_is_alert_on_free_floor():
    total = 100 * GIB
    assert check_disk.is_alert(4 * GIB, total, min_free_gib=5, max_used_percent=100)
    assert not check_disk.is_alert(6 * GIB, total, min_free_gib=5, max_used_percent=100)


def test_is_alert_on_used_percent():
    total = 100 * GIB
    # 95 GiB used of 100 -> 95% used
    assert check_disk.is_alert(5 * GIB, total, min_free_gib=0, max_used_percent=90)
    assert not check_disk.is_alert(20 * GIB, total, min_free_gib=0, max_used_percent=90)


def test_zero_total_volume_never_percent_alerts():
    assert not check_disk.is_alert(0, 0, min_free_gib=0, max_used_percent=50)


def test_main_alert_exit_code(tmp_path):
    # Simulate a tiny volume by pointing at a path that does not exist:
    # that yields an alert line ("Path not found") and exit code 1.
    rc = check_disk.main(["--path", str(tmp_path / "missing"), "--quiet-ok"])
    assert rc == 1


def test_main_missing_path_reports_not_found(tmp_path, capsys):
    check_disk.main(["--path", str(tmp_path / "nope")])
    out = capsys.readouterr().out
    assert "not found" in out.lower()
