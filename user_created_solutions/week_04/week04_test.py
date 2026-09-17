# Keeing tests confined to 3 main working funcitons for now:
# collect_log_files
# hash_file
# scan_log_file

import hashlib
from collections import Counter
from unittest.mock import patch

import pytest
from week04_finished import (
    collect_log_files,
    hash_file,
    scan_log_file,
)


def test_collect_log_files_invalid_file(tmp_path):
    """Non-.log files in the top-level directory should be ignored."""
    (tmp_path / "app.log").write_text("valid")
    (tmp_path / "notes.txt").write_text("shoud be ignored")
    (tmp_path / "readme.md").write_text("should be ignored")

    result = collect_log_files(tmp_path)

    assert result == [tmp_path / "app.log"]


def test_collect_log_files_subdir_invalid_file(tmp_path):
    """.log files nested in subdirectories should still be collected recursively."""
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "nested.log").write_text("x")
    (tmp_path / "top.log").write_text("x")

    result = collect_log_files(tmp_path)

    assert sorted(result) == sorted(
        [tmp_path / "top.log", tmp_path / "sub" / "nested.log"]
    )


def test_collect_log_files_exception_issues(tmp_path):
    """A PermissionError mid-iteration should be swallowed, keeping files found before it."""

    def broken_rglob(self, pattern):
        yield tmp_path / "ok.log"
        raise PermissionError("denied")

    with patch("pathlib.Path.rglob", broken_rglob):
        result = collect_log_files(tmp_path)

    assert result == [tmp_path / "ok.log"]


def test_hash_file_invalid_file(tmp_path):
    """A nonexistent file should return an empty string, not raise."""
    missing = tmp_path / "does_not_exist.log"

    result = hash_file(missing)

    assert result == ""


def test_hash_file_invalid_file_is_directory(tmp_path):
    """Passing a directory should return an empty string, not raise."""
    result = hash_file(tmp_path)

    assert result == ""


def test_hash_file_correct_value(tmp_path):
    """hash_file should return the SHA-256 hex digest matching the file's contents."""
    test_string = "dfasdfdasfsafwaefesfs"
    hasher = hashlib.sha256(test_string.encode())
    hash_result = hasher.hexdigest()

    logfile = tmp_path / "hashme.log"
    logfile.write_text(test_string)
    result = hash_file(logfile)

    assert hash_result == result


def test_scan_log_file_exception_issues(tmp_path):
    """Passing a path that can't be opened as a file should return an empty Counter, not raise."""
    result = scan_log_file(tmp_path)

    assert result == Counter()


@pytest.mark.parametrize(
    "content, expected",
    [
        ("Possible SQL injection detected", Counter({"sql_injection": 1})),
        ("nope", Counter()),
    ],
)
def test_scan_log_file_correct_findings(tmp_path, content, expected):
    """scan_log_file should count matches against SUSPICIOUS_PATTERNS, or return an empty Counter for clean content."""
    logfile = tmp_path / "app.log"
    logfile.write_text(content)
    result = scan_log_file(logfile)

    assert result == expected
