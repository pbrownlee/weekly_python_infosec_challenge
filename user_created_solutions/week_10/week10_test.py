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
import sys
import tempfile
import types
from datetime import UTC, datetime
from pathlib import Path

import pytest
import week10_finished as w10


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
        page1 = _write_page(
            tmp,
            "page1.json",
            [
                {
                    "indicator": "1.1.1.1",
                    "type": "ip",
                    "severity": "high",
                    "first_seen": "2026-10-01T00:00:00Z",
                    "last_seen": "2026-10-10T00:00:00Z",
                    "source": "test-feed",
                },
            ],
        )
        page2 = _write_page(
            tmp,
            "page2.json",
            [
                {
                    "indicator": "evil.example.com",
                    "type": "domain",
                    "severity": "low",
                    "first_seen": "2026-09-01 00:00:00",
                    "last_seen": "2026-09-02 00:00:00",
                    "source": "test-feed",
                },
            ],
        )

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
    now = datetime(2026, 10, 18, tzinfo=UTC)
    record = {
        "indicator": "1.1.1.1",
        "type": "ip",
        "severity": "high",
        "first_seen": "2026-10-01T00:00:00Z",
        "last_seen": "2026-10-10T00:00:00Z",
        "source": "test-feed",
    }
    assert w10.filter_record(record, max_age_days=30, now=now) is True


def test_filter_record_drops_low_severity_record():
    now = datetime(2026, 10, 18, tzinfo=UTC)
    record = {
        "indicator": "benign.example.com",
        "type": "domain",
        "severity": "low",
        "first_seen": "2026-10-01T00:00:00Z",
        "last_seen": "2026-10-10T00:00:00Z",
        "source": "test-feed",
    }
    assert w10.filter_record(record, max_age_days=30, now=now) is False


def test_filter_record_drops_stale_high_severity_record():
    """High severity alone isn't enough -- a record last seen 60 days ago
    should be dropped under a 30-day staleness cutoff."""
    now = datetime(2026, 10, 18, tzinfo=UTC)
    record = {
        "indicator": "9.9.9.9",
        "type": "ip",
        "severity": "critical",
        "first_seen": "2026-06-01T00:00:00Z",
        "last_seen": "2026-08-19T00:00:00Z",
        "source": "test-feed",
    }
    assert w10.filter_record(record, max_age_days=30, now=now) is False


def test_transform_record_normalizes_mixed_timestamp_formats():
    record = {
        "indicator": "1.1.1.1",
        "type": "ip",
        "severity": "high",
        "first_seen": "2026-10-01 00:00:00",  # space-separated, no Z
        "last_seen": "2026-10-10T00:00:00",  # ISO, no Z
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
        {
            "indicator": "1.1.1.1",
            "type": "ip",
            "severity": "high",
            "first_seen": "2026-10-01T00:00:00Z",
            "last_seen": "2026-10-10T00:00:00Z",
            "source": "test-feed",
        },
        {
            "indicator": "evil.example.com",
            "type": "domain",
            "severity": "critical",
            "first_seen": "2026-09-01T00:00:00Z",
            "last_seen": "2026-10-15T00:00:00Z",
            "source": "test-feed",
        },
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


# user added tests


def test_if_parse_ts_formats_dates():
    # record with a different time formats
    records = [
        {
            "indicator": "1.1.1.1",
            "type": "ip",
            "severity": "high",
            "first_seen": "2026-10-01 00:00:00",  # space-separated, no Z
            "last_seen": "2026-10-10 00:00:00",  # No iso, no z
            "source": "test-feed",
        },
        {
            "indicator": "1.1.1.1",
            "type": "ip",
            "severity": "high",
            "first_seen": "2026-10-01 00:00:00",  # space-separated, no Z
            "last_seen": "2026-10-10T00:00:00",  # ISO, no Z
            "source": "test-feed",
        },
        {
            "indicator": "1.1.1.1",
            "type": "ip",
            "severity": "high",
            "first_seen": "2026-10-01 00:00:00",  # space-separated, no Z
            "last_seen": "2026-10-10T00:00:00Z",  # already formatted
            "source": "test-feed",
        },
    ]
    # make sure the datetime formats match
    dt_expected = datetime(2026, 10, 10, 0, 0, 0, tzinfo=UTC)
    date_1 = w10._parse_ts(records[0]["last_seen"])
    date_2 = w10._parse_ts(records[1]["last_seen"])
    date_3 = w10._parse_ts(records[2]["last_seen"])
    assert date_1 == dt_expected
    assert date_2 == dt_expected
    assert date_3 == dt_expected


def test_if_format_ts_will_return_converted_string():
    dt_object = datetime(2026, 10, 10, 0, 0, 0, tzinfo=UTC)
    converted_obj = w10._format_ts(dt_object)
    # converted datetime should equal date string with timezone set
    assert converted_obj == "2026-10-10T00:00:00Z"


def test_if_dedup_records_removes_dupes():
    records = [
        {
            "indicator": "1.1.1.1",
            "type": "ip",
            "severity": "high",
            "first_seen": "2026-10-01 00:00:00",
            "last_seen": "2026-10-10T00:00:00Z",
            "source": "test-feed",
        },
        {
            "indicator": "1.1.1.1",
            "type": "ip",
            "severity": "high",
            "first_seen": "2026-10-01 00:00:00",
            "last_seen": "2026-10-10T10:00:00Z",
            "source": "test-feed",
        },
        {
            "indicator": "1.1.1.1",
            "type": "ip",
            "severity": "high",
            "first_seen": "2026-10-01 00:00:00",
            "last_seen": "2026-10-10T20:00:00Z",
            "source": "test-feed",
        },
    ]
    deduped_records = w10.dedupe_records(records)
    assert len(deduped_records) == 1  # should only be one record after deduping
    assert (
        deduped_records[0]["last_seen"] == "2026-10-10T20:00:00Z"
    )  # most recent record wins


def test_which_dedup_records_wins_in_a_tie():
    records = [
        {
            "indicator": "1.1.1.1",
            "type": "ip",
            "severity": "high",
            "first_seen": "2026-10-01 00:00:00",
            "last_seen": "2026-10-10T00:00:00Z",
            "source": "test-feed",
        },
        {
            "indicator": "1.1.1.1",
            "type": "ip",
            "severity": "high",
            "first_seen": "2026-10-01 00:00:00",
            "last_seen": "2026-10-10T00:00:00Z",
            "source": "yo-mama-com",
        },
    ]
    deduped_records = w10.dedupe_records(records)
    assert (
        deduped_records[0]["source"] == "test-feed"
    )  # test_feed was first so it wins when the last_seen timestamps are the same


@pytest.mark.parametrize(
    "bad_record",
    [
        None,
        "not a dict",
        {"indicator": "1.1.1.1"},  # missing fields
        {
            "indicator": "1.1.1.1",
            "type": "ip",
            "severity": "high",
            "first_seen": "2026-10-01T00:00:00Z",
            "last_seen": None,  # non-string timestamp
            "source": "test-feed",
        },
        {
            "indicator": "1.1.1.1",
            "type": "ip",
            "severity": "high",
            "first_seen": "2026-10-01T00:00:00Z",
            "last_seen": "not a date",
            "source": "test-feed",
        },
    ],
)
def test_filter_record_drops_junk_without_raising(bad_record):
    now = datetime(2026, 10, 18, tzinfo=UTC)
    assert w10.filter_record(bad_record, now=now) is False


def test_write_csv_with_no_records_still_writes_header(tmp_path):
    out = tmp_path / "empty.csv"
    w10.write_csv([], str(out))
    assert out.read_text(encoding="utf-8").strip() == (
        "indicator,type,severity,first_seen,last_seen,source"
    )


def test_main_rejects_negative_max_age(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--max-age-days", "-5"])
    with pytest.raises(SystemExit) as exc:
        w10.main()
    assert exc.value.code == 2
