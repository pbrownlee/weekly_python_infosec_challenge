# Week 9 — Brute-Force Log Analyzer

**Tier 2: Beginner — Topic 2 of 4** · Weekly Python Security Challenge

## Problem statement

You're given a synthetic `auth.log`-style file (`week09_sample_auth.log`) full
of SSH login lines — some successful, most failed. Write a tool that:

1. Parses each line into structured fields (timestamp, status, user, source IP).
2. Groups the **failed** attempts by source IP.
3. Flags any IP that racks up at least `threshold` failed attempts within any
   rolling `window_seconds`-second span — a classic brute-force signature.
4. Prints a clear report of which IPs were flagged and why.

## Learning objectives

- Parsing semi-structured text with `re` (named groups, anchors) into clean dicts.
- Converting log timestamps into `datetime` objects you can actually compare and subtract.
- Grouping and windowing data over time — a "rolling window" check, not just a flat count.
- Structuring a small analysis pipeline: parse → group → detect → report.

## On the job

This is one of the most common first-pass triage tasks in security
operations: somebody hands you (or a SIEM hands you) a chunk of auth logs,
and the first question is almost always "is anyone hammering our login page
right now?" A rolling-window brute-force check like this is the backbone of
real detection rules — the same shape shows up in SIEM correlation rules,
fail2ban, and cloud provider anomaly alerts, just with more knobs.

## Plan It First

Before writing any code:

1. In plain language (a few sentences or a short bullet list), write down the
   steps your program needs to take, in order, and what each step consumes
   and produces. For example: "step 2 takes a list of raw lines and produces
   a list of dicts; step 3 takes that list of dicts and produces a dict of
   IP → flagged timestamps."
2. **Sketch a quick Mermaid flowchart** (`flowchart TD` or `flowchart LR` —
   plain text, no diagramming tool required) of the function calls and
   control flow you're planning, *before* you write the implementation.
   Refer back to **the Mermaid syntax primer from week 3** if you need a
   refresher on node/arrow syntax. Include this diagram alongside your
   solution when you share it in the challenge thread — it'll get compared
   against what you actually built during review, which is a good gut-check
   on whether your plan and your code agree.
3. Specifically think through: what happens when the window check runs on an
   IP with only 1 or 2 failed attempts (should never be flagged)? What
   happens with attempts that are failures but spread hours apart (should
   NOT be flagged, even if the raw count is high)? Your flowchart should show
   where that distinction actually gets decided.

## Worked trace example

Given these three failed attempts from the same IP:

```
02:30:11  203.0.113.50  Failed
02:30:19  203.0.113.50  Failed
02:30:27  203.0.113.50  Failed
```

With `window_seconds=60, threshold=3`: starting from the first timestamp
(02:30:11), all three attempts fall within 60 seconds of it, so the count
reaches 3 and the IP is flagged. If those same three attempts were instead
spaced an hour apart, the same *count* (3) would never be flagged, because no
single 60-second window ever contains more than one of them.

## Constraints

- Only parse the provided sample file format (SSH `sshd[...]:` lines); lines
  that don't match should be skipped, not crash the program.
- No network calls, no scanning — this is pure log parsing and analysis.
- Keep the rolling-window check correct for attempts that arrive in any
  order in the file (don't assume the file is already sorted by timestamp
  per IP, though it happens to be in the sample).

## Example usage

```
$ python week09_starter.py --logfile week09_sample_auth.log
Brute-force activity detected:
  203.0.113.50: 6 failed attempts, first at 2026-10-10 02:30:11
  198.51.100.23: 7 failed attempts, first at 2026-10-10 03:02:10
```

(Exact wording of your report is up to you — the required piece is that
every IP meeting the threshold-within-window condition shows up, and no
IP that doesn't meet it does.)

## Hints (graduated — try not to peek until you're stuck)

1. **Hint 1:** Get `parse_log_line()` solid first, with a couple of lines
   pasted into a throwaway script, before touching the windowing logic at all.
   Garbage in, garbage out — a buggy parser will make the windowing logic
   look broken when it isn't.
2. **Hint 2:** For the rolling window, it helps to first collect and *sort*
   each IP's failed timestamps, then for each timestamp count how many of
   that IP's other timestamps fall within `window_seconds` after it. The
   first timestamp where that count reaches `threshold` is your trigger.
3. **Hint 3:** Keep "parse the file," "detect brute force," and "format the
   report" as three completely separate functions, even though it's tempting
   to fold detection and reporting together. You'll thank yourself in two
   weeks when the ETL pipeline challenge asks for exactly this kind of
   separated pipeline shape.

## Ethics & legal reminder

Only analyze logs you're authorized to see — this week's sample file is
synthetic and safe to experiment with freely, but the same applies at work:
log access is itself often access-controlled, and "I was just testing a
detection script" is not a substitute for having permission to view the data
in the first place.

## Using AI tools

If you use an AI assistant (including Claude) to help you write code for
this challenge, treat it like a very fast pair programmer, not an oracle:
ask it to explain unfamiliar parts, question any code you don't fully
understand before using it, and make sure *you* could explain and trace
through every line it writes. The goal this week is building your own
ability to decompose and reason about a program — leaning on an assistant to
skip that thinking defeats the point of the exercise.

## Portfolio note

A clean brute-force detector with a readable report is a legitimate "here's
something I built" artifact for a security-engineering portfolio or
interview — it's a small, self-contained demonstration of a real detection
pattern.
