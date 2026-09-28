# Week 7 Challenge — File Integrity Checker

**Tier 1: Novice — Topic 3 of 3**

## Problem Statement

Build a command-line tool that detects unauthorized or unexpected changes to files in a directory, using cryptographic hashes rather than timestamps (which are trivial to fake).

The tool has two modes:

- **`baseline`** — walk a directory, compute the SHA-256 hash of every file, and save the results (filename → hash) to a JSON file. This is your "known good" snapshot.
- **`verify`** — walk the same directory again, recompute hashes, and compare against a previously saved baseline. Report which files are **unchanged**, **modified** (hash differs), **added** (present now, not in baseline), or **removed** (in baseline, missing now).

This is the core mechanism behind real file integrity monitoring (FIM) tools like Tripwire, AIDE, and the file-integrity modules inside EDR products — you're building a small, honest version of something that shows up in actual security tooling.

## Learning Objectives

- Use `pathlib.Path` to walk a directory tree and work with paths in a platform-independent way (builds directly on Week 2's Multi-File Hash Auditor).
- Use `hashlib` to compute SHA-256 digests of file contents, read in chunks (not loaded all at once) so it scales to larger files.
- Serialize and deserialize state with `json` so a baseline can persist between runs — this is your first taste of a tool that has "memory" across separate invocations.
- Structure a CLI with two distinct modes (via `argparse` subparsers) that share underlying logic but do different things with it.

## On the Job

This is close to a real task you'd be handed as a security engineer: "we need to know if anyone tampers with files in `/etc/` (or a config directory, or a set of binaries) between deploys." Commercial FIM tools do this at scale with more bells and whistles (real-time watching, alerting, whitelisting), but the core logic — hash now, compare to hash then — is exactly what you're building this week. Week 10's Filesystem Integrity Monitor (Tier 3) will revisit this idea with real-time `watchdog`-based event detection instead of periodic baseline/verify runs, so what you build this week is also laying groundwork for later.

## Plan It First

Before writing any code:

1. Write out, in plain English or a short numbered list, the steps for `baseline` mode and the steps for `verify` mode separately. Where do they overlap? (Hint: both need to "walk the directory and hash every file" — that's a strong signal it should be its own function, called from both modes.)
2. Sketch a **Mermaid flowchart** (`flowchart TD` or `flowchart LR` is fine — plain text, no diagramming tool required) of your planned function calls and control flow. Cover both the `baseline` path and the `verify` path, including the decision point where a file's status gets classified as unchanged/modified/added/removed. If you haven't written one since Week 3, the syntax primer is below as a refresher.
3. Bring this diagram along when you share your solution — it gets compared against what you actually built during review, so it's worth it being honest about your real plan rather than redrawn after the fact to match the finished code.

### Mermaid syntax refresher (first introduced Week 3)

Quick recap since a couple weeks have passed:
- Opening line: `flowchart TD` (top-down) or `flowchart LR` (left-right).
- `A[Rectangle]` = a step or action. `B{Diamond}` = a decision point.
- Plain arrow: `A --> B`. Labeled decision arrow: `B -->|yes| C`, `B -->|no| D`.
- Preview it by pasting into mermaid.live, or drop it in a fenced ` ```mermaid ` code block in a `.md` file — GitHub and VS Code's Markdown Preview both render it natively.

From next week onward this refresher won't be repeated — just a pointer back to Week 3 if you need it again.

## Worked Trace Example

Say `sample_dir/` contains two files: `a.txt` (contents: `"hello"`) and `b.txt` (contents: `"world"`).

**Baseline run:**
1. `collect_files("sample_dir")` → `[Path("sample_dir/a.txt"), Path("sample_dir/b.txt")]`
2. `compute_file_hash(a.txt)` → SHA-256 of `"hello"` → `2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824`
3. `compute_file_hash(b.txt)` → SHA-256 of `"world"` → `486ea46224d1bb4fb680f34f7c9ad96a8f24ec88be73ea8e5a6c65260e9cb8a7`
4. `build_baseline` assembles `{"a.txt": "2cf24d...", "b.txt": "486ea4..."}`
5. `save_baseline(...)` writes that dict to `baseline.json`.

**Now imagine `a.txt` gets edited to say `"hello!"` and a new file `c.txt` is added, before you run `verify`:**
1. `collect_files` now finds `a.txt`, `b.txt`, `c.txt`.
2. Recompute hashes: `a.txt` now hashes differently than baseline; `b.txt` hashes the same; `c.txt` has no baseline entry at all.
3. `verify_against_baseline` compares the two dicts key-by-key and produces something like:
   ```
   {"unchanged": ["b.txt"], "modified": ["a.txt"], "added": ["c.txt"], "removed": []}
   ```
4. `print_report(...)` turns that into a readable summary.

## Constraints

- Use only the standard library (`argparse`, `pathlib`, `hashlib`, `json`) — no third-party dependencies needed this week.
- Hash files by reading in fixed-size chunks (e.g. 8192 bytes at a time), not `f.read()` all at once — this matters for files too large to comfortably fit in memory, even though your test files will be small.
- Store the baseline as JSON, using **relative** paths (relative to the directory being scanned) as keys, so the baseline file is portable if the directory gets moved.
- Handle a missing baseline file gracefully in `verify` mode (clear error message, not a raw traceback).

## Example Usage

```
$ python week07_starter.py baseline --dir sample_dir --output baseline.json
Baseline saved: 2 files hashed -> baseline.json

$ python week07_starter.py verify --dir sample_dir --baseline baseline.json
File Integrity Report
----------------------------------------
  MODIFIED : a.txt
  ADDED    : c.txt
----------------------------------------
Unchanged: 1, Modified: 1, Added: 1, Removed: 0
```

## Hints (graduated — try not to skip straight to hint 3)

1. Start with just `compute_file_hash(filepath)` and get it right in isolation (test it against a file with known content and confirm the hash against a hash you compute independently, e.g. with `sha256sum` on the command line) before building anything else on top of it.
2. `build_baseline()` and the "recompute hashes now" step in `verify` are the same operation — don't write it twice. Have `verify` call the same file-walking/hashing function that `baseline` uses.
3. For the comparison step, think in terms of set operations on the *keys* of the two dicts: `set(current) - set(baseline)` gives you added files, `set(baseline) - set(current)` gives you removed files, and the intersection is where you need to actually compare hash values to split into unchanged vs. modified.

## Using AI Tools

If you use an AI assistant (including Claude) to help you write this week's solution, that's fine — treat it like you would a senior teammate's code review or a Stack Overflow answer: useful for unblocking yourself, but the goal is that *you* understand every line well enough to explain it, trace through it by hand, and modify it without the AI's help. Don't paste in the challenge and take the first full solution it gives you; work through the decomposition yourself first, and use AI help for the parts you're genuinely stuck on.

## Ethics & Legal Reminder

Only run this against directories you own or have explicit permission to scan (your own sample/test directory is fine — don't point this at system directories you don't fully understand, or anyone else's files, without permission).

## Portfolio Note

A working baseline/verify file integrity tool is a legitimate, demonstrable artifact — it's a smaller-scale version of a real security control. Worth keeping in your portfolio repo with a short README explaining the baseline/verify workflow.
