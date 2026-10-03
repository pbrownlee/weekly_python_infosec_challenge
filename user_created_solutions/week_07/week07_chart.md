# Baseline / Verify Flow

Two modes: **baseline** (fingerprint a directory) and **verify** (diff a directory against a saved baseline).

Both modes pass through the same `scan()` step — walk (pathlib) + hash (hashlib) — so it appears
once, shared by both branches, rather than duplicated in each. The flow re-splits after it because
the result is *handled* differently (write it out vs. diff it), not because the scan differs.

Every verify check happens **after** the scan: `removed` needs the scan's key set, so it can't
run before the walk completes.

```mermaid
flowchart TD
    Start([Start]) --> Mode{Which mode?}

    Mode -->|baseline| B0["baseline(walkthrough_path)<br/>directory = arg"]
    Mode -->|verify| V0["verify(baseline_file, directory)"]
    V0 --> V1["Load baseline.json<br/>(directory + stored hashes)"]

    B0 --> Scan
    V1 --> Scan

    Scan["scan(directory) → {path/file: hash}<br/>walk files in directory (pathlib)<br/>compute hash of each file (hashlib)"]

    Scan --> Output{Which mode?}
    Output -->|baseline| B4["Write baseline.json<br/>{directory, files}"]
    B4 --> Done([Done])

    Output -->|verify| V2["Compare<br/>baseline keys vs scan keys"]

    V2 --> V9{"Baseline path<br/>absent from scan?"}
    V9 -->|Yes| V10["removed"]

    V2 --> V4{"Scanned path<br/>in baseline?"}
    V4 -->|Yes| V5{"Hash<br/>matches?"}
    V5 -->|Yes| V6["unchanged"]
    V5 -->|No| V7["modified"]
    V4 -->|No| V8["new"]

    V6 --> R["Report results"]
    V7 --> R
    V8 --> R
    V10 --> R
    R --> Done2([Done])
```

## Notes

- `scan()` is one shared step across both modes: walk + hash, returning `{path: hash}`. One
  function in code, one node in the diagram.
- Ordering in verify: load baseline → scan → compare → classify. `removed` consumes the scan's
  key set (`baseline_keys − scan_keys`), so it is downstream of the scan, not parallel to it.
- The mode is read twice — once to get the directory (arg vs. baseline.json) and once to decide
  what to do with the scan result. That second split is unavoidable: `baseline` writes the map
  out, `verify` diffs it.
- `removed` is a set difference over paths; the other three come from the per-file classification.

