"""
Week 10 Finished — IOC Feed ETL Pipeline
Tier 2: Beginner

Read -> filter -> transform -> write pipeline over a paginated, synthetic
threat-intel feed (sample_data/ioc_feed_page_*.json).

See week10_challenge.md for the full problem statement and constraints.

Note: Works with Python 3.11 or newer
"""

import argparse
import csv
import glob
import json
from datetime import UTC, datetime, timedelta

CSV_FIELDS = ["indicator", "type", "severity", "first_seen", "last_seen", "source"]


def iter_records(page_paths: list[str]):
    """Yield one raw IOC record (dict) at a time, across all given page files.

    Must NOT load every page -- or every record -- into memory at once.
    Read and yield page-by-page, so this works the same whether you give
    it 5 pages or 5,000.

    Args:
        page_paths: list[str] -- file paths, e.g.
            sorted(glob.glob("sample_data/ioc_feed_page_*.json"))

    Yields:
        dict: one raw record per yield, e.g.
            {"indicator": "1.2.3.4", "type": "ip", "severity": "high",
             "first_seen": "...", "last_seen": "...", "source": "..."}
    """
    # open each json data file one at a time
    for item in page_paths:
        try:
            with open(item, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Error loading feed file {item}: {e}, skipping")
            continue
        # the ioc files are a data array
        yield from data


def filter_record(
    record: dict,
    min_severities: tuple = ("high", "critical"),
    max_age_days: int = 30,
    now: datetime | None = None,
) -> bool:
    """Return True if this record should be KEPT, False if it should be dropped.

    A record should be kept only if BOTH:
      - its severity is in `min_severities`, AND
      - its last_seen timestamp is no older than `max_age_days` relative to `now`

    Args:
        record: a raw record dict (as yielded by iter_records)
        min_severities: iterable of severity strings considered high-priority
        max_age_days: drop records whose last_seen is older than this many days
        now: a datetime to treat as "the current time" -- pass this in
             explicitly (don't call datetime.now() inside this function)
             so the function stays testable without depending on the
             real wall clock.

    Returns:
        bool
    """
    # make sure record has right values
    ids = ("indicator", "type", "severity", "first_seen", "last_seen", "source")
    if not isinstance(record, dict) or not all(k in record for k in ids):
        return False
    # make sure timestamps parse properly
    try:
        last_seen = _parse_ts(record["last_seen"])
        _parse_ts(record["first_seen"])
    except (ValueError, TypeError):
        return False
    # first check if record is critical or high, then check if the date range is within the expected threshold
    return (
        record["severity"] in min_severities
        and (now - timedelta(days=max_age_days)) <= last_seen <= now
    )


def transform_record(record: dict) -> dict:
    """Return a NEW dict with the record normalized:
      - `first_seen` and `last_seen` converted to one consistent ISO 8601
        UTC string format, e.g. "2026-10-07T00:00:00Z"
        (the raw data mixes at least two different formats on purpose --
        see week10_challenge.md for examples)
      - everything else carried over unchanged

    Do NOT mutate the input dict in place -- build and return a new one.

    Args:
        record: a raw record dict (should already have passed filter_record)

    Returns:
        dict: the normalized record, same keys as the input
    """
    return {
        "indicator": record["indicator"],
        "type": record["type"],
        "severity": record["severity"],
        "first_seen": _format_ts(_parse_ts(record["first_seen"])),
        "last_seen": _format_ts(_parse_ts(record["last_seen"])),
        "source": record["source"],
    }


# added by user
def dedupe_records(records: list[dict]) -> list[dict]:
    """Collapse records that share an `indicator`, keeping the newest one.

    For each indicator, the record with the latest `last_seen` wins. On a
    tie, the record seen first is kept. Output order follows the order in
    which each indicator first appears in `records`.

    Args:
        records: list[dict] -- records with `indicator` and `last_seen` keys

    Returns:
        list[dict]: one record per unique indicator
    """
    kept = {}
    for record in records:
        existing = kept.get(record["indicator"])
        if existing is None or _parse_ts(record["last_seen"]) > _parse_ts(
            existing["last_seen"]
        ):
            kept[record["indicator"]] = record
    return list(kept.values())


def write_csv(records: list[dict], output_path: str) -> None:
    """Write `records` to a CSV file at `output_path` using csv.DictWriter.

    Args:
        records: list[dict] -- all dicts should have the same keys
        output_path: str
    """
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(records)


def write_json(records: list[dict], output_path: str) -> None:
    """Write `records` to a JSON file at `output_path` as a single JSON
    array, using json.dump.

    Args:
        records: list[dict]
        output_path: str
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


# added by user
def _parse_ts(date_string: str) -> datetime:
    """Parse an ISO 8601 timestamp string into a timezone-aware datetime.

    Naive timestamps (no UTC offset) are assumed to be UTC, so the result
    can always be compared against other aware datetimes.

    Args:
        date_string: str -- an ISO 8601 timestamp, e.g. "2026-10-07T00:00:00Z"
            or "2026-10-07 00:00:00"

    Returns:
        datetime: a timezone-aware datetime

    Raises:
        ValueError: if `date_string` isn't a format fromisoformat accepts
    """
    dt = datetime.fromisoformat(date_string)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


# added by user
def _format_ts(date_obj: datetime) -> str:
    """Format a datetime as an ISO 8601 UTC string with a trailing "Z".

    The "Z" suffix is appended literally; `date_obj` is not converted, so
    it should already be in UTC (e.g. a value returned by `_parse_ts`).

    Args:
        date_obj: datetime -- the datetime to format, expected to be in UTC

    Returns:
        str: a timestamp like "2026-10-07T00:00:00Z" (seconds precision)
    """
    return date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    parser = argparse.ArgumentParser(
        description="IOC feed ETL pipeline: read, filter, transform, write."
    )
    parser.add_argument(
        "--input-glob",
        default="sample_data/ioc_feed_page_*.json",
        help="Glob pattern matching the input page files",
    )
    parser.add_argument("--csv-out", default="ioc_report.csv")
    parser.add_argument("--json-out", default="ioc_report.json")
    parser.add_argument("--max-age-days", type=int, default=30)
    args = parser.parse_args()

    if args.max_age_days < 0:
        parser.error("--max-age-days must be 0 or greater")

    page_paths = sorted(glob.glob(args.input_glob))
    if not page_paths:
        parser.error(f"No input pages matched: {args.input_glob}")

    now = datetime.now(UTC)

    validated_records = []
    processed_count = 0
    for record in iter_records(page_paths):
        processed_count += 1
        if filter_record(record, max_age_days=args.max_age_days, now=now):
            validated_records.append(transform_record(record))

    final_records = dedupe_records(validated_records)

    # Optional bonus (not in the brief): most severe, then most recent, first
    SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    final_records.sort(
        key=lambda r: (
            SEVERITY_RANK[r["severity"]],
            -_parse_ts(r["last_seen"]).timestamp(),
        )
    )

    write_json(final_records, args.json_out)
    write_csv(final_records, args.csv_out)

    print(f"Read {processed_count} raw records across {len(page_paths)} pages.")
    print(
        f"{processed_count} -> {len(validated_records)} after filtering (severity + staleness)."
    )
    print(f"{len(validated_records)} -> {len(final_records)} after deduplication.")
    print(f"Wrote {len(final_records)} records to {args.csv_out} and {args.json_out}.")


if __name__ == "__main__":
    main()
