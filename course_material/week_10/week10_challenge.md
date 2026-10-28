# Week 10 — IOC Feed ETL Pipeline

**Tier 2: Beginner** · Topic 6 of 19

## Why this one matters

This challenge is built directly around the pattern you described as your actual day-to-day work: read a file or API response with a large number of entries, modify/transform/filter it, and output it to a desired format. Everything from here through the rest of the series will assume you have this shape — read → filter → transform → write — solidly in your hands, because it comes back constantly in real security tooling (parsing feeds, normalizing logs, reshaping API responses for a report or a SIEM import).

## Problem statement

You're given a synthetic threat-intelligence indicator feed, delivered the way a real API often delivers one: in pages. `sample_data/` contains five JSON files (`ioc_feed_page_1.json` through `ioc_feed_page_5.json`), each a JSON array of indicator-of-compromise (IOC) records. Each record looks like:

```json
{
  "indicator": "143.233.228.238",
  "type": "ip",
  "severity": "high",
  "first_seen": "2026-09-25 00:00:00",
  "last_seen": "2026-10-07T00:00:00Z",
  "source": "VirusTotal"
}
```

Build a pipeline that:

1. **Reads** all five pages *without ever holding the entire feed in memory at once* — process one page (and its records) at a time.
2. **Filters** to a meaningful subset: keep only `high` or `critical` severity indicators that have actually been seen recently (not stale, long-dead entries that happen to have a scary severity label).
3. **Transforms** each surviving record: normalize `first_seen` and `last_seen` into one consistent timestamp format, and **deduplicate** — the feed deliberately contains the same indicator reported more than once (sometimes from different sources, sometimes with a more recent `last_seen`). You should end up with one entry per unique indicator, keeping whichever version is most current.
4. **Writes** the final result to *two* output formats: a CSV file (via `csv.DictWriter`) and a JSON file (via `json.dump`).

## Learning objectives

- Write a **generator** that reads multiple files page-by-page and yields individual records one at a time, instead of loading everything into a big list up front — this is memory-safe chunked processing, and it's the difference between code that works on a sample file and code that survives being pointed at a real multi-gigabyte export.
- Use the `csv` module (`csv.DictWriter`) and `json` module (`json.dump`) for **multi-format output** from the same in-memory data.
- Practice the **read → filter → transform → write** shape as its own explicit, reusable pattern — not just "a script that happens to do four things," but four named stages you could swap, reorder, or reuse independently.

## On the Job

This is about as close to daily reality for a security engineer as this series gets. You will be handed a feed, a log export, or an API dump that's bigger than you'd like to hold in memory, and asked to "just get me the real stuff, in a format the team's tooling can read." That's this challenge, with made-up data.

## Plan It First

Before writing any code, sketch your plan as a quick Mermaid flowchart (`flowchart TD` or `flowchart LR` — plain text, no diagramming tool required). If you need a refresher on the syntax, see the primer from week 3. Include this diagram alongside your solution when you share it — it'll get compared against what you actually built during review, which is a good way to notice where your plan and your code quietly diverged.

Questions worth answering in your plan before you touch the keyboard:
- What does "read one page at a time" actually look like in code — where does the generator pause and resume?
- What are your two filter conditions, and what inputs do you need to evaluate each one (severity alone isn't enough — what else do you need to know "stale" or "recent")?
- When two records share an indicator, how do you decide which one wins? What do you need to compare?
- Where does dedup happen — inside `transform_record()`, or somewhere that can see more than one record at a time?

## Tiny worked trace

One record, traced through the pipeline (values abbreviated):

```
raw record (from iter_records):
  {"indicator": "143.233.228.238", "type": "ip", "severity": "high",
   "first_seen": "2026-09-25 00:00:00", "last_seen": "2026-10-07T00:00:00Z",
   "source": "VirusTotal"}

filter_record(record, max_age_days=30, now=2026-10-18):
  severity "high" is in {"high","critical"}          -> ok
  last_seen 2026-10-07 is 11 days before "now"        -> within 30 days, ok
  => True (record survives)

transform_record(record):
  first_seen "2026-09-25 00:00:00"  -> "2026-09-25T00:00:00Z"   (reformatted)
  last_seen  "2026-10-07T00:00:00Z" -> "2026-10-07T00:00:00Z"   (already normalized)
  => {"indicator": "143.233.228.238", "type": "ip", "severity": "high",
      "first_seen": "2026-09-25T00:00:00Z", "last_seen": "2026-10-07T00:00:00Z",
      "source": "VirusTotal"}

dedup step:
  if another record for "143.233.228.238" was already kept with an OLDER
  last_seen, this one replaces it; if an EQUAL-or-newer one is already
  kept, this one is dropped.

write_csv([...]) / write_json([...]):
  this record appears as one row in ioc_report.csv and one object in
  the array written to ioc_report.json
```

## Constraints

- Do not load all five pages into one big list before processing — `iter_records()` must be a generator (uses `yield`), reading page-by-page.
- `filter_record()` must take the "current time" as a parameter rather than calling `datetime.now()` internally — this is what makes it testable (and it's good practice generally: a function that silently depends on the wall clock is hard to test and hard to reason about).
- `transform_record()` must not mutate its input — return a new dict.
- Final output (both CSV and JSON) must contain exactly one record per unique `indicator` value.
- CSV and JSON outputs must contain the same records (just two representations of the same final list).

## Example usage / expected output

```
$ python week10_starter.py --input-glob "sample_data/ioc_feed_page_*.json" \
    --csv-out ioc_report.csv --json-out ioc_report.json

Read 168 raw records across 5 pages.
168 -> 51 after filtering (severity + staleness).
51 -> 48 after deduplication.
Wrote 48 records to ioc_report.csv and ioc_report.json.
```

(Your exact counts may differ slightly depending on how you define "stale" — that's expected; see Hint 2.)

## Hints (graduated — try to solve it before reading further down)

1. **Hint 1:** `iter_records()` doesn't need to avoid loading one page into memory — JSON pages are "small" by design. What it must avoid is loading *all the pages* (or an intermediate giant list of every record) at once. Loop over `page_paths`, `json.load()` one page, loop over *its* records and `yield` each one, then move to the next page.
2. **Hint 2:** For "stale," compare `last_seen` to a cutoff: `now - timedelta(days=max_age_days)`. You'll need `first_seen`/`last_seen` parsed into real `datetime` objects to compare them at all — notice that this means part of your "transform" logic (parsing timestamps) actually has to happen *before* your filter step can fully work, which is worth resolving explicitly in your plan rather than discovering mid-code.
3. **Hint 3:** For dedup, a dict keyed by `indicator` works well: walk your filtered+transformed records in order, and for each one, check `dedup_map.get(indicator)` — if nothing's there yet, or what's there has an older `last_seen`, store this one in its place. At the end, `dedup_map.values()` is your final list.

## Ethics & Legal

This is entirely synthetic, locally-generated sample data — no real indicators, no real victims, nothing to be careful about here beyond good hygiene. That said, if you ever do this exact pattern against a *real* threat-intel feed or vendor API at work: respect that feed's API rate limits and terms of use, and be mindful that some IOC feeds are shared under licenses that restrict redistribution — "I can analyze this" doesn't always mean "I can republish this."

## Using AI tools

Using AI tools (including Claude) to help you think through or debug this challenge is fine and expected — that's a normal part of how working engineers use these tools. The goal is that you understand the resulting code well enough to explain every line and extend it yourself; treat an AI assistant as a tutor you can quiz and push back on, not an answer vending machine. Writing the plan yourself first (before getting help) is the single best way to make sure that's actually happening.

## Portfolio note

A clean "paginated feed in, deduped multi-format report out" pipeline is exactly the kind of small tool that's easy to describe concretely in an interview or a performance review: "I built a script that ingested a paginated threat-intel feed, filtered and normalized it, and produced both CSV and JSON reports for downstream tooling." Keep this one — it's a strong, true-to-life example of the exact skill gap you said you wanted to close.

## Provided files

- `sample_data/ioc_feed_page_1.json` through `ioc_feed_page_5.json` — the synthetic paginated feed (168 records total, mixed timestamp formats and deliberate duplicates included).
- `week10_starter.py` — function signatures to fill in.
