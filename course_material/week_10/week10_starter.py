"""
Week 10 Starter — IOC Feed ETL Pipeline
Tier 2: Beginner

Read -> filter -> transform -> write pipeline over a paginated, synthetic
threat-intel feed (sample_data/ioc_feed_page_*.json).

Fill in the functions below. See week10_challenge.md for the full problem
statement, constraints, and a worked trace example before you start.
"""

import argparse
import csv
import glob
import json
from datetime import datetime, timedelta, timezone


def iter_records(page_paths):
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
    raise NotImplementedError("TODO: implement iter_records")


def filter_record(record, min_severities=("high", "critical"), max_age_days=30, now=None):
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
    raise NotImplementedError("TODO: implement filter_record")


def transform_record(record):
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
    raise NotImplementedError("TODO: implement transform_record")


def write_csv(records, output_path):
    """Write `records` to a CSV file at `output_path` using csv.DictWriter.

    Args:
        records: list[dict] -- all dicts should have the same keys
        output_path: str
    """
    raise NotImplementedError("TODO: implement write_csv")


def write_json(records, output_path):
    """Write `records` to a JSON file at `output_path` as a single JSON
    array, using json.dump.

    Args:
        records: list[dict]
        output_path: str
    """
    raise NotImplementedError("TODO: implement write_json")


def main():
    parser = argparse.ArgumentParser(
        description="IOC feed ETL pipeline: read, filter, transform, write."
    )
    parser.add_argument(
        "--input-glob", default="sample_data/ioc_feed_page_*.json",
        help="Glob pattern matching the input page files",
    )
    parser.add_argument("--csv-out", default="ioc_report.csv")
    parser.add_argument("--json-out", default="ioc_report.json")
    parser.add_argument("--max-age-days", type=int, default=30)
    args = parser.parse_args()

    page_paths = sorted(glob.glob(args.input_glob))
    if not page_paths:
        print(f"No input pages matched: {args.input_glob}")
        return

    now = datetime.now(timezone.utc)

    # TODO, roughly in this order:
    #   1. Stream raw records with iter_records(page_paths)
    #   2. Apply filter_record(record, max_age_days=args.max_age_days, now=now)
    #      to each raw record, keeping only the survivors
    #   3. Apply transform_record() to each survivor
    #   4. Dedupe by `indicator`, keeping whichever version has the newest
    #      `last_seen` (see week10_challenge.md Hint 3 if you get stuck)
    #   5. write_csv(...) and write_json(...) with the final deduped list
    #   6. Print a short summary: records read / kept after filter / after dedupe
    raise NotImplementedError("TODO: wire the pipeline together in main()")


if __name__ == "__main__":
    main()
