"""
Week 9 CI tests — Brute-Force Log Analyzer

Exercises the exact function signatures defined in week09_starter.py.
CI-safe: everything runs against in-memory strings or a tempfile, no network,
no real hosts.
"""

import sys
from datetime import datetime

import pytest
from week09_finished import (
    find_brute_force_ips,
    generate_report,
    load_log_entries,
    main,
    parse_log_line,
)


def test_parse_log_line_valid_failed():
    line = "2026-10-10 02:30:11 sshd[1021]: Failed password for invalid user admin from 203.0.113.50 port 44210 ssh2"
    result = parse_log_line(line)
    assert result is not None
    assert result["status"] == "Failed"
    assert result["user"] == "admin"
    assert result["ip"] == "203.0.113.50"
    assert result["timestamp"] == datetime(2026, 10, 10, 2, 30, 11)  # noqa: DTZ001


def test_parse_log_line_valid_accepted():
    line = "2026-10-10 02:14:01 sshd[1021]: Accepted password for paul from 10.0.0.5 port 51200 ssh2"
    result = parse_log_line(line)
    assert result is not None
    assert result["status"] == "Accepted"
    assert result["user"] == "paul"
    assert result["ip"] == "10.0.0.5"


def test_parse_log_line_garbage_returns_none():
    assert parse_log_line("this is not a log line at all") is None
    assert parse_log_line("") is None


def test_load_log_entries_skips_bad_lines(tmp_path):
    log_file = tmp_path / "auth.log"
    log_file.write_text(
        "2026-10-10 02:30:11 sshd[1021]: Failed password for invalid user admin from 203.0.113.50 port 44210 ssh2\n"
        "garbage line that should be skipped\n"
        "2026-10-10 02:14:01 sshd[1021]: Accepted password for paul from 10.0.0.5 port 51200 ssh2\n"
    )
    entries = load_log_entries(str(log_file))
    assert len(entries) == 2
    assert entries[0]["ip"] == "203.0.113.50"
    assert entries[1]["ip"] == "10.0.0.5"


def test_find_brute_force_ips_flags_clustered_failures():
    # 6 failed attempts from the same IP within ~41 seconds -> should be flagged at threshold=5
    base_lines = [
        "2026-10-10 02:30:11 sshd[1]: Failed password for invalid user admin from 203.0.113.50 port 1 ssh2",
        "2026-10-10 02:30:19 sshd[1]: Failed password for invalid user admin from 203.0.113.50 port 2 ssh2",
        "2026-10-10 02:30:27 sshd[1]: Failed password for invalid user root from 203.0.113.50 port 3 ssh2",
        "2026-10-10 02:30:35 sshd[1]: Failed password for invalid user root from 203.0.113.50 port 4 ssh2",
        "2026-10-10 02:30:44 sshd[1]: Failed password for invalid user test from 203.0.113.50 port 5 ssh2",
        "2026-10-10 02:30:52 sshd[1]: Failed password for invalid user test from 203.0.113.50 port 6 ssh2",
    ]
    entries = [parse_log_line(line) for line in base_lines]
    flagged = find_brute_force_ips(entries, window_seconds=60, threshold=5)
    assert "203.0.113.50" in flagged
    assert len(flagged["203.0.113.50"]) >= 5


def test_find_brute_force_ips_ignores_sparse_failures():
    # Same IP, same count of failures, but spread far apart in time -> should NOT be flagged
    base_lines = [
        "2026-10-10 02:00:00 sshd[1]: Failed password for invalid user admin from 192.0.2.77 port 1 ssh2",
        "2026-10-10 03:00:00 sshd[1]: Failed password for invalid user admin from 192.0.2.77 port 2 ssh2",
        "2026-10-10 04:00:00 sshd[1]: Failed password for invalid user admin from 192.0.2.77 port 3 ssh2",
    ]
    entries = [parse_log_line(line) for line in base_lines]
    flagged = find_brute_force_ips(entries, window_seconds=60, threshold=2)
    assert "192.0.2.77" not in flagged


def test_find_brute_force_ips_ignores_successful_logins():
    base_lines = [
        "2026-10-10 02:00:00 sshd[1]: Accepted password for paul from 10.0.0.5 port 1 ssh2",
        "2026-10-10 02:00:05 sshd[1]: Accepted password for paul from 10.0.0.5 port 2 ssh2",
        "2026-10-10 02:00:10 sshd[1]: Accepted password for paul from 10.0.0.5 port 3 ssh2",
    ]
    entries = [parse_log_line(line) for line in base_lines]
    flagged = find_brute_force_ips(entries, window_seconds=60, threshold=2)
    assert flagged == {}


def test_generate_report_empty():
    report = generate_report({})
    assert isinstance(report, str)
    assert len(report) > 0


def test_generate_report_contains_flagged_ip():
    flagged = {
        "203.0.113.50": [
            datetime(2026, 10, 10, 2, 30, 11),  # noqa: DTZ001
            datetime(2026, 10, 10, 2, 30, 19),  # noqa: DTZ001
        ]
    }
    report = generate_report(flagged)
    assert "203.0.113.50" in report


def test_main_rejects_zero_threshold(monkeypatch, tmp_path):
    log = tmp_path / "auth.log"
    log.write_text("")
    monkeypatch.setattr(
        sys, "argv", ["prog", "--logfile", str(log), "--threshold", "0"]
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2


def test_main_rejects_missing_logfile(monkeypatch, tmp_path):
    missing = tmp_path / "nope.log"
    monkeypatch.setattr(sys, "argv", ["prog", "--logfile", str(missing)])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
