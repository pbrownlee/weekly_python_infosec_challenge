"""
Week 7 CI tests -- File Integrity Checker

These exercise the exact function signatures defined in week07_starter.py.
They will fail against the unmodified starter (every function raises
NotImplementedError) -- that's expected. Implement the functions, then run
`pytest -q` locally until these go green, same as the Week 3 red-to-green habit.

CI-safe: everything runs against tempfile-created directories/files, no
network access, no real filesystem paths outside the temp dir.
"""

import hashlib
import tempfile
from pathlib import Path

import pytest
from week07_finished import (
    build_baseline,
    compute_file_hash,
    load_baseline,
    save_baseline,
    verify_against_baseline,
)


@pytest.fixture
def sample_dir():
    """Create a temporary directory with two known files, clean up after."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "a.txt").write_text("hello")
        (tmp_path / "b.txt").write_text("world")
        yield tmp_path


def test_compute_file_hash_matches_known_sha256(sample_dir):
    expected = hashlib.sha256(b"hello").hexdigest()
    assert compute_file_hash(sample_dir / "a.txt") == expected


def test_compute_file_hash_differs_for_different_content(sample_dir):
    hash_a = compute_file_hash(sample_dir / "a.txt")
    hash_b = compute_file_hash(sample_dir / "b.txt")
    assert hash_a != hash_b


def test_build_baseline_includes_all_files_with_relative_keys(sample_dir):
    baseline = build_baseline(sample_dir)
    assert set(baseline.keys()) == {"a.txt", "b.txt"}
    assert baseline["a.txt"] == hashlib.sha256(b"hello").hexdigest()


def test_save_and_load_baseline_roundtrip(sample_dir, tmp_path):
    baseline = build_baseline(sample_dir)
    output_path = tmp_path / "baseline.json"
    save_baseline(baseline, output_path)

    assert output_path.exists()
    loaded = load_baseline(output_path)
    assert loaded == baseline


def test_load_baseline_missing_file_raises_file_not_found(tmp_path):
    missing_path = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        load_baseline(missing_path)


def test_verify_against_baseline_detects_all_four_states(sample_dir):
    baseline = build_baseline(sample_dir)

    # Simulate changes: modify a.txt, add c.txt, leave b.txt unchanged,
    # remove nothing from disk but pretend baseline had a file that's now gone.
    (sample_dir / "a.txt").write_text("hello!")
    (sample_dir / "c.txt").write_text("new file")
    baseline_with_removed = dict(baseline)
    baseline_with_removed["removed.txt"] = (
        "deadbeef" * 8
    )  # fake hash, file never existed on disk

    report = verify_against_baseline(sample_dir, baseline_with_removed)

    assert "b.txt" in report["unchanged"]
    assert "a.txt" in report["modified"]
    assert "c.txt" in report["added"]
    assert "removed.txt" in report["removed"]
