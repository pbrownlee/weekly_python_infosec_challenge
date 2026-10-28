"""
Week 10 CI tests — IOC Feed ETL Pipeline

These exercise the exact function signatures given in week10_starter.py.
They will fail (red) against the starter as shipped -- that's expected.
Get them to pass (green) as you implement each function.

CI-safe: everything here uses tempfile-based sample pages and in-memory
data -- no network access, no dependency on sample_data/ being present.
"""
import csv
import json
import tempfile
import types
from datetime import datetime, timezone
from pathlib import Path

import pytest

import week10_starter as w10


def _write_page(dir_path, name, records):
    path = Path(dir_path) / name
    with open(path, "w") as f:
        json.dump(records, f)
    return str(path)


def test_iter_records_yields_across_multiple_pages():
    """iter_records must be a generator that yields every record across
    all given pages, in page order, without requiring them all to be
    loaded into one list by the caller."""
    with tempfile.TemporaryDirectory() as tmp:
        page1 = _write_page(tmp, "page1.json", [
            {"indicator": "1.1.1.1", "type": "ip", "severity": "high",
             "first_seen": "2026-10-01T00:00:00Z", "last_seen": "2026-10-10T00:00:00Z",
             "source": "test-feed"},
        ])
        page2 = _write_page(tmp, "page2.json", [
            {"indicator": "evil.example.com", "type": "domain", "severity": "low",
             "first_seen": "2026-09-01 00:00:00", "last_seen": "2026-09-02 00:00:00",
             "source": "test-feed"},
        ])

        result = w10.iter_records([page1, page2])
        assert isinstance(result, types.GeneratorType), (
            "iter_records should be a generator function (use `yield`), "
            "not a function that returns a fully-built list"
        )

        records = list(result)
        assert len(records) == 2
        assert records[0]["indicator"] == "1.1.1.1"
        assert records[1]["indicator"] == "evil.example.com"


def test_filter_record_keeps_high_severity_recent_record():
    now = datetime(2026, 10, 18, tzinfo=timezone.utc)
    record = {
        "indicator": "1.1.1.1", "type": "ip", "severity": "high",
        "first_seen": "2026-10-01T00:00:00Z", "last_seen": "2026-10-10T00:00:00Z",
        "source": "test-feed",
    }
    assert w10.filter_record(record, max_age_days=30, now=now) is True


def test_filter_record_drops_low_severity_record():
    now = datetime(2026, 10, 18, tzinfo=timezone.utc)
    record = {
        "indicator": "benign.example.com", "type": "domain", "severity": "low",
        "first_seen": "2026-10-01T00:00:00Z", "last_seen": "2026-10-10T00:00:00Z",
        "source": "test-feed",
    }
    assert w10.filter_record(record, max_age_days=30, now=now) is False


def test_filter_record_drops_stale_high_severity_record():
    """High severity alone isn't enough -- a record last seen 60 days ago
    should be dropped under a 30-day staleness cutoff."""
    now = datetime(2026, 10, 18, tzinfo=timezone.utc)
    record = {
        "indicator": "9.9.9.9", "type": "ip", "severity": "critical",
        "first_seen": "2026-06-01T00:00:00Z", "last_seen": "2026-08-19T00:00:00Z",
        "source": "test-feed",
    }
    assert w10.filter_record(record, max_age_days=30, now=now) is False


def test_transform_record_normalizes_mixed_timestamp_formats():
    record = {
        "indicator": "1.1.1.1", "type": "ip", "severity": "high",
        "first_seen": "2026-10-01 00:00:00",       # space-separated, no Z
        "last_seen": "2026-10-10T00:00:00",         # ISO, no Z
        "source": "test-feed",
    }
    original_copy = dict(record)

    result = w10.transform_record(record)

    assert result["first_seen"] == "2026-10-01T00:00:00Z"
    assert result["last_seen"] == "2026-10-10T00:00:00Z"
    # original dict must not be mutated
    assert record == original_copy


def test_write_csv_and_write_json_round_trip():
    records = [
        {"indicator": "1.1.1.1", "type": "ip", "severity": "high",
         "first_seen": "2026-10-01T00:00:00Z", "last_seen": "2026-10-10T00:00:00Z",
         "source": "test-feed"},
        {"indicator": "evil.example.com", "type": "domain", "severity": "critical",
         "first_seen": "2026-09-01T00:00:00Z", "last_seen": "2026-10-15T00:00:00Z",
         "source": "test-feed"},
    ]

    with tempfile.TemporaryDirectory() as tmp:
        csv_path = Path(tmp) / "out.csv"
        json_path = Path(tmp) / "out.json"

        w10.write_csv(records, str(csv_path))
        w10.write_json(records, str(json_path))

        with open(csv_path, newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2
        assert rows[0]["indicator"] == "1.1.1.1"
        assert rows[1]["severity"] == "critical"

        with open(json_path) as f:
            loaded = json.load(f)
        assert loaded == records
