# Week 4: Capstone - Mini Log Auditor CLI

**Tier 0 - Level-Up Phase (final week)**

## Problem Statement

Build a command-line tool that audits a directory of log files for
suspicious activity. This is the capstone of the level-up phase: it
combines `argparse` (Week 1), `pathlib` + `hashlib` (Week 2), and
`try`/`except` + `logging` (Week 3) into one cohesive program, plus one
new tool: `collections.Counter` for tallying results.

Given a directory of `.log` files, your tool should:

1. Find every `.log` file in the directory.
2. Scan each file's lines against a set of suspicious patterns (failed
   logins, SQL injection attempts, port scans, unauthorized access
   attempts) and tally how many times each pattern occurs.
3. Compute a SHA-256 hash of each file audited, as an integrity record.
4. Print a summary report: suspicious activity counts by category
   (most frequent first), and the hash of every file audited.
5. Handle a file that can't be read gracefully - log a warning and keep
   going, don't crash the whole audit over one bad file.

Sample data to test against is in `sample_logs/` (three files - two
with planted suspicious lines, one clean).

## Learning Objectives

- Structuring a program with several moving parts into small,
  single-purpose functions that call each other cleanly - the actual
  point of this capstone.
- `collections.Counter` for tallying and ranking counts
  (`Counter.most_common()`), instead of hand-rolling a dict with manual
  `+= 1` bookkeeping.
- Combining `argparse`, `pathlib`, `hashlib`, `re`, and `logging` in one
  program, reusing patterns you already built in Weeks 1-3 rather than
  re-deriving them.
- Practicing graceful per-item error handling in a loop: one bad file
  shouldn't take down the whole run.

## On the Job

This is close to a real internal tool: point it at a folder of logs
pulled from a host or exported from a SIEM, get back a triage summary
of what looks suspicious plus a hash of each file for chain-of-custody
purposes. Programs that "read a pile of files, extract signal, report
it" are one of the most common shapes of tool you'll build as a
security engineer - this capstone is your first full-sized version of
that shape.

## Plan It First

This is the week where planning actually pays off - you're combining
four prior weeks' worth of pieces into one program, and it's much
easier to lose track of which function calls which once you're mid-way
through writing code than before you've started.

1. Before writing anything, write one sentence per function in
   `week04_starter.py` describing what it does and what it needs from
   the function that calls it, and what it hands back.
2. Sketch a Mermaid flowchart (see the syntax primer from Week 3 if you
   need a refresher) of `main()`'s full call sequence: parse args ->
   validate directory -> audit -> print summary, including the
   per-file error-handling branch inside the audit step. Include this
   diagram alongside your solution - it'll get compared against what
   you actually built during review.
3. Only then start filling in functions - build and test one at a time
   (`hash_file` and `collect_log_files` first, since you already wrote
   working versions of both in Week 2), rather than writing the whole
   file top to bottom before running anything.

## Worked Trace Example

Take this single line from `sample_logs/authhost02.log`:

```
2026-01-15 09:10:02 ERROR Port scan detected: sequential connection attempts from 192.0.2.44
```

- `scan_log_file` reads this line and checks it against each pattern in
  `SUSPICIOUS_PATTERNS` in turn.
- `failed_login`'s pattern doesn't match (no "Failed login attempt for
  user" text).
- `sql_injection`'s pattern doesn't match.
- `port_scan`'s pattern - `re.compile(r"Port scan detected")` -
  matches. The file's Counter becomes `Counter({"port_scan": 1})` (plus
  whatever it already had from earlier lines).
- `unauthorized_access`'s pattern doesn't match this line.

After `scan_log_file` finishes the whole file, `audit_directory` adds
this file's Counter into the running `overall_counts` total with `+`.

## Constraints

- Reuse your own working `hash_file` and file-collection logic from
  Week 2 rather than rewriting them from scratch.
- A single unreadable file must not stop the audit of the rest of the
  directory - catch the specific exception, log it, continue.
- Don't hardcode the three sample filenames anywhere - `collect_log_files`
  must work for any directory of `.log` files.

## Example Usage / Expected Output

```
$ python week04_starter.py sample_logs/
Suspicious Activity Summary
----------------------------------------
failed_login          9
sql_injection          2
port_scan              1
unauthorized_access    1

File Integrity Record
----------------------------------------
<sha256 hash>  authhost02.log
<sha256 hash>  webserver01.log
<sha256 hash>  webserver02.log

3 files audited, 13 suspicious events found.
```

(Exact formatting is up to you - the counts above are the ones to match
against the provided sample data.)

## Hints (graduated)

1. Start by copying your working `hash_file` and file-collection code
   from Week 2 - don't reinvent those this week, just adapt them.
2. `Counter` objects support `+` directly: if you have a Counter per
   file, `overall = overall + file_counts` (or `overall.update(file_counts)`)
   accumulates them without a manual loop.
3. For the per-file error handling, the exception you're most likely to
   hit in practice while testing is `UnicodeDecodeError` or
   `OSError`/`PermissionError` - catch whichever your own testing
   actually surfaces, and say so in the log message.

## Optional Bonus (not required)

Write 2-3 of your own pytest tests for this tool - for example, a test
that `scan_log_file` correctly counts a small in-memory sample, or that
an unreadable file doesn't crash `audit_directory`. Not required to
complete the challenge, but good practice before CI/CD tests become
part of every week starting next tier.

## Using AI Tools

You're welcome to use AI tools (including Claude) to help you write
code for this challenge - to explain an error message, suggest a
refactor, or review your solution. The point of this series is that
*you* do the reasoning and *you* can explain why the code works, so use
AI as a second pair of eyes, not as a replacement for doing the
decomposition and tracing yourself.

## Ethics & Legal Reminder

The sample logs are synthetic data provided with this challenge. As
with every exercise in this series: never point a tool like this at
real logs, systems, or accounts you don't own or don't have explicit
written permission to access - even a read-only auditing tool should
only ever run against data or systems you're authorized to touch.

---

This wraps up the 4-week Level-Up Phase. Starting next week (Week 5,
Tier 1: Novice), a full CI/CD pipeline kicks in - every challenge ships
with its own pytest test file, a `requirements.txt`, and a GitHub
Actions workflow running pytest plus a `bandit` security scan on every
push.

*If this one takes longer than a week, no problem - just message me
anytime to push the schedule back and I'll pick up from wherever you
actually are.*
