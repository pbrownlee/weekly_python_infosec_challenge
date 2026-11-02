"""
Week 10 Solution -- IOC Feed ETL Pipeline
Topic 6 (Tier 2: Beginner)

Reads a paginated, synthetic threat-intel IOC feed (several small JSON
"pages" -- the way a real paginated API hands you results one page at a
time), filters down to the indicators worth keeping, normalizes and
dedupes them, and writes the result out in two formats: CSV and JSON.

This is the classic shape of a lot of real security-engineering work:

    read -> filter -> transform -> write-to-format

Run it directly:  python week10_solution.py
"""

import csv
import json
import os
import random
import tempfile
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Step 0: sample data generation.
#
# In a real job this function wouldn't exist -- you'd be handed actual
# page files, or making real HTTP calls to a paginated API. It's here
# purely so this script is runnable end-to-end on its own, and so it can
# plant a few deliberately messy records (duplicates, low severity,
# different timestamp formats) that exercise every stage of the pipeline.
# ---------------------------------------------------------------------------
def generate_sample_pages(directory, num_pages=3, records_per_page=6):
    """Write `num_pages` small JSON files into `directory`, each containing
    a list of IOC records. Mimics a paginated API response saved to disk."""
    random.seed(7)  # reproducible sample data
    types = ["ip", "domain", "hash", "url"]
    sources = ["feedA", "feedB", "osint-pull"]
    timestamp_formats = [
        lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S"),
        lambda dt: dt.strftime("%Y-%m-%d"),
    ]

    all_records = []
    base = datetime(2026, 9, 1)
    for i in range(num_pages * records_per_page - 2):
        dt_first = base.replace(day=1 + (i % 27))
        dt_last = base.replace(day=1 + ((i + 3) % 27))
        fmt = timestamp_formats[i % len(timestamp_formats)]
        all_records.append(
            {
                "indicator": f" 185.220.{100 + i % 50}.{i % 255} "
                if i % 4 != 0
                else f"evil-{i}.example.com",
                "type": types[i % len(types)],
                "severity": (i % 10) + 1,  # 1-10
                "first_seen": fmt(dt_first),
                "last_seen": fmt(dt_last),
                "source": sources[i % len(sources)],
            }
        )

    # Plant a couple of exact duplicates (same indicator+type, different
    # casing/whitespace/source) so dedupe has something real to catch.
    dup = dict(all_records[0])
    dup["indicator"] = dup["indicator"].upper()
    dup["source"] = "osint-pull"
    all_records.append(dup)
    dup2 = dict(all_records[5])
    dup2["source"] = "feedB"
    all_records.append(dup2)

    random.shuffle(all_records)

    # Split into pages of roughly equal size -- this is the "pagination".
    for page_num in range(num_pages):
        chunk = all_records[page_num::num_pages]
        path = os.path.join(directory, f"page_{page_num + 1}.json")
        with open(path, "w") as f:
            json.dump(chunk, f)


# ---------------------------------------------------------------------------
# Step 1: read -- one page at a time, never the whole feed at once.
# ---------------------------------------------------------------------------
def iter_records(directory):
    """Generator that yields one IOC record (dict) at a time.

    Reads a single page file into memory, yields its records, then moves
    on to the next page. A feed with 500 pages never needs all 500 in
    memory simultaneously -- only whichever one page is "current".
    """
    for filename in sorted(os.listdir(directory)):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(directory, filename)
        with open(path) as f:
            page = json.load(f)  # one page is small; fine to load as a whole
        for record in page:
            yield record


# ---------------------------------------------------------------------------
# Step 2: filter -- keep only what's worth carrying forward.
# ---------------------------------------------------------------------------
ALLOWED_TYPES = {"ip", "domain", "hash", "url"}


def filter_record(record, min_severity=5):
    """Return True if this record should be kept."""
    return (
        record.get("severity", 0) >= min_severity
        and record.get("type") in ALLOWED_TYPES
        and bool(record.get("indicator", "").strip())
    )


# ---------------------------------------------------------------------------
# Step 3: transform -- normalize timestamps, clean up the indicator field.
# ---------------------------------------------------------------------------
_TIMESTAMP_FORMATS = ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d")


def normalize_timestamp(ts):
    """Parse a timestamp that might arrive in any of a few vendor formats
    and return it as a consistent ISO-8601 string. Falls back to the raw
    value rather than crashing the whole pipeline on one bad record."""
    for fmt in _TIMESTAMP_FORMATS:
        try:
            dt = datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except ValueError:
            continue
    return ts


def transform_record(record):
    """Return a clean, normalized copy of one record."""
    return {
        "indicator": record["indicator"].strip().lower(),
        "type": record["type"],
        "severity": record["severity"],
        "first_seen": normalize_timestamp(record["first_seen"]),
        "last_seen": normalize_timestamp(record["last_seen"]),
        "source": record.get("source", "unknown"),
    }


# ---------------------------------------------------------------------------
# The pipeline itself: wires read -> filter -> transform -> dedupe together.
# ---------------------------------------------------------------------------
def run_pipeline(directory, min_severity=5):
    """Run the full ETL pipeline over the feed in `directory` and return a
    deduped list of clean records."""
    seen_keys = set()
    results = []

    for raw in iter_records(directory):
        if not filter_record(raw, min_severity=min_severity):
            continue

        clean = transform_record(raw)

        dedupe_key = (clean["indicator"], clean["type"])
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)

        results.append(clean)

    return results


# ---------------------------------------------------------------------------
# Step 4: write -- two output formats.
# ---------------------------------------------------------------------------
_FIELDNAMES = ["indicator", "type", "severity", "first_seen", "last_seen", "source"]


def write_csv(records, path):
    with open(path, "w", newline="") as f:  # newline="" avoids blank rows on Windows
        writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)


def write_json(records, path):
    with open(path, "w") as f:
        json.dump(records, f, indent=2)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        generate_sample_pages(tmp)
        records = run_pipeline(tmp, min_severity=5)

        write_csv(records, "ioc_feed_clean.csv")
        write_json(records, "ioc_feed_clean.json")

        print(f"Processed feed -> {len(records)} clean, deduped indicators kept")
        print("Wrote ioc_feed_clean.csv and ioc_feed_clean.json")


if __name__ == "__main__":
    main()
