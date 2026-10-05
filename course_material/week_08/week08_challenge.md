# Week 8 — Local Port Scanner

**Tier 2: Beginner · Topic 4 of 4**

## Problem Statement

Build a command-line port scanner that checks whether ports in a given range
are open on a target host. In real engagements this target would be a host
you're authorized to test; for this exercise, you'll point it only at
`127.0.0.1` (localhost) or another local address you control.

Your tool should:

1. Accept a target host and a port range (e.g. `--host 127.0.0.1 --start 1 --end 1024`).
2. Attempt a TCP connection to each port with a short timeout.
3. Use a thread pool to scan multiple ports concurrently instead of one at a
   time (a sequential scan of 1024 ports, each with even a 0.5s timeout on
   closed ports, would take far too long).
4. Report which ports are open, in ascending order, with a summary count.

## Learning Objectives

- The `socket` module: creating a TCP socket, setting a connect timeout, and
  reading `connect_ex()`'s return value to tell "open" from "closed/filtered"
  without exceptions for the common case.
- `concurrent.futures.ThreadPoolExecutor` for I/O-bound concurrency — why
  threads (not multiprocessing) are the right tool when a task spends most
  of its time waiting on the network, not burning CPU.
- Structuring a scanner as small composable pieces: "scan one port," "scan a
  range," "format results" — so each piece is independently testable.

## On the Job

This is close to a real first step in a security assessment or an internal
asset-inventory sweep: before you can reason about what's exposed on a host,
you need to know what's listening. Production scanners (nmap and friends) do
far more — service fingerprinting, OS detection, UDP support — but the core
loop ("try to connect, note what answers, do it concurrently so it finishes
in reasonable time") is exactly what you're building here, and it's a
pattern you'll reach for any time you need to probe many independent targets
quickly.

## Plan It First

Before writing any code:

1. In plain language (a few sentences or a short list), write down the steps
   your program needs to take, in order, from "user runs the command" to
   "summary printed to screen."
2. Then sketch a quick Mermaid flowchart (`flowchart TD` or `flowchart LR` —
   plain text, no diagramming tool required) of your planned function calls
   and control flow before writing any code. Use the Mermaid syntax primer
   from Week 3 if you need a refresher on node/arrow syntax. Include this
   diagram alongside your solution when you share it in the challenge
   thread — it'll get compared against what you actually built during
   review, so it's worth it being an honest plan rather than a diagram drawn
   after the fact.
3. Specifically think through: where does the thread pool fit relative to
   the loop over ports? Does `scan_port` need to know anything about
   concurrency at all, or can it stay a plain, single-port function that
   something else calls many times in parallel? (Hint: the second one is
   much easier to test.)

## Tiny Worked Trace

Suppose `--host 127.0.0.1 --start 20 --end 23` and only port 22 has anything
listening (e.g. your machine's SSH daemon, or a test server you started).

- `scan_port(127.0.0.1, 20, timeout=0.5)` → connection refused → `False`/closed
- `scan_port(127.0.0.1, 21, timeout=0.5)` → connection refused → closed
- `scan_port(127.0.0.1, 22, timeout=0.5)` → connection succeeds → open
- `scan_port(127.0.0.1, 23, timeout=0.5)` → connection refused → closed

All four calls get submitted to the thread pool roughly at once rather than
run back-to-back, so the whole range comes back in roughly one timeout
period, not four. The final report lists: `Open ports: [22]` out of 4
scanned.

## Constraints

- Only scan `127.0.0.1`, `localhost`, or another host/IP you own or have
  explicit authorization to test. **Never point this at a host you don't
  control** — unauthorized port scanning can violate computer-abuse laws and
  acceptable-use policies even when no harm is intended.
- Use a short, configurable timeout per connection attempt (e.g. default
  0.5–1 second) so a scan of a few hundred ports finishes in a reasonable
  time.
- Handle the case where the host can't be resolved or is unreachable at all,
  without crashing with an unhandled traceback.

## Example Usage / Expected Output

```
$ python week08_starter.py --host 127.0.0.1 --start 1 --end 1024 --workers 100

Scanning 127.0.0.1 ports 1-1024 with 100 workers...
Open ports: [22, 80, 631]
Scanned 1024 ports in 0.84s — 3 open, 1021 closed/filtered
```

## Hints

1. `socket.socket(socket.AF_INET, socket.SOCK_STREAM)` plus
   `sock.settimeout(timeout)` plus `sock.connect_ex((host, port))` is the
   core trick — `connect_ex` returns `0` on success instead of raising, which
   keeps your per-port logic simple (no `try`/`except` needed for the normal
   "closed" case). Don't forget to close the socket either way.
2. `ThreadPoolExecutor.map()` or `.submit()` + `as_completed()` both work;
   `map()` is simpler to read if you don't need per-task error handling,
   `submit()`/`as_completed()` gives you more control if a scan might raise.
3. Keep `scan_port()` free of any threading concerns — it should just take a
   host/port/timeout and return a result. Let a separate function own the
   "run this across many ports concurrently" responsibility. If you find
   yourself passing a `ThreadPoolExecutor` into `scan_port()`, that's a sign
   the responsibilities have blurred together.

## Using AI Tools

If you use an AI assistant (including Claude) to help you write this
challenge's code, that's fine — treat it like a pairing partner, not an
autopilot. Make sure you understand every line it gives you well enough to
explain it, trace through it by hand, and modify it without the assistant's
help. The goal of this series is what's in your head at the end of the week,
not just a working script.

## Portfolio Note

A working, tested port scanner with clean thread-pool usage is a reasonable
thing to point to in a portfolio or interview as "I understand concurrent
I/O in Python," which comes up constantly in security tooling (scanners,
bulk API lookups, log collectors).
