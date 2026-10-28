"""
Week 9 Solution — Brute-Force Log Analyzer
Tier 2: Beginner

Parses an auth.log-style file, tracks failed logins per source IP using a
rolling time window, and flags IPs that look like they're brute-forcing
their way in.

Log line format (synthetic, modeled on OpenSSH's auth.log style):

    Oct 09 03:14:52 webhost01 sshd[1234]: Failed password for invalid user admin from 203.0.113.50 port 51234 ssh2
    Oct 09 03:15:01 webhost01 sshd[1234]: Accepted password for paul from 192.168.1.10 port 51300 ssh2

Usage:
    python week09_solution.py sample_auth.log
    python week09_solution.py sample_auth.log --window 60 --threshold 5
"""

import argparse
import re
from collections import defaultdict, deque
from datetime import datetime

# --- Regex for one auth.log line -------------------------------------------
# Groups: timestamp, status ("Failed"/"Accepted"), user, ip
LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+"
    r"\S+\s+sshd\[\d+\]:\s+"
    r"(?P<status>Failed|Accepted)\s+password\s+for\s+"
    r"(?:invalid user\s+)?(?P<user>\S+)\s+from\s+"
    r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+port\s+\d+\s+ssh2"
)

# The log doesn't carry a year, so we assume "this year" for parsing.
# This is a known simplification of a toy dataset — real auth.log entries
# on a long-running host can span a New Year boundary, which this naive
# approach would get wrong. Flagging it here rather than silently hiding it.
_YEAR = datetime.now().year


def parse_log_line(line):
    """Parse one auth.log line into a dict, or return None if it doesn't match.

    Returns:
        {"timestamp": datetime, "status": "Failed"|"Accepted", "user": str, "ip": str}
        or None for a line that isn't a recognizable SSH login attempt
        (header lines, unrelated services, blank lines, etc).
    """
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None

    raw_ts = match.group("timestamp")
    # "Oct 09 03:14:52" + assumed year -> real datetime for comparisons/math
    timestamp = datetime.strptime(f"{_YEAR} {raw_ts}", "%Y %b %d %H:%M:%S")

    return {
        "timestamp": timestamp,
        "status": match.group("status"),
        "user": match.group("user"),
        "ip": match.group("ip"),
    }


def load_log_entries(filepath):
    """Read the log file and return a list of parsed entries, skipping lines
    that don't match the expected format (rather than crashing on them)."""
    entries = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            entry = parse_log_line(line)
            if entry is not None:
                entries.append(entry)
    return entries


def detect_brute_force(entries, window_seconds=60, threshold=5):
    """Flag source IPs with >= `threshold` failed logins inside any
    `window_seconds`-wide rolling window.

    Approach: process entries in chronological order and keep a deque of
    recent (timestamp, user) pairs per IP. A deque lets us cheaply drop
    entries that have aged out of the window from the *left* (oldest
    first) without rescanning the whole history each time — that's the
    whole reason it's a deque and not a plain list.

    Returns:
        dict: {ip: {"failure_count": int, "first_seen": datetime,
                     "last_seen": datetime, "users_tried": set}}
        for every IP that tripped the threshold at least once. The counts
        reflect the *worst* window seen for that IP (the window is
        recomputed on every new failure, so a later, smaller window
        wouldn't accidentally shrink what's reported).
    """
    # Sort defensively — a real log file is usually already in time order,
    # but nothing enforces that, and the whole sliding-window logic assumes it.
    entries = sorted(entries, key=lambda e: e["timestamp"])

    recent_failures = defaultdict(deque)   # ip -> deque[(datetime, user)]
    flagged = {}

    for entry in entries:
        if entry["status"] != "Failed":
            # A success doesn't erase prior failures (a brute-forcer who
            # eventually guesses right is still a brute-forcer), so we
            # simply don't touch the window on a success.
            continue

        ip = entry["ip"]
        window = recent_failures[ip]
        window.append((entry["timestamp"], entry["user"]))

        # Prune anything older than `window_seconds` before the newest entry.
        cutoff = entry["timestamp"].timestamp() - window_seconds
        while window and window[0][0].timestamp() < cutoff:
            window.popleft()

        if len(window) >= threshold:
            existing = flagged.get(ip)
            if existing is None or len(window) >= existing["failure_count"]:
                flagged[ip] = {
                    "failure_count": len(window),
                    "first_seen": window[0][0],
                    "last_seen": window[-1][0],
                    "users_tried": {user for _, user in window},
                }

    return flagged


def generate_report(flagged):
    """Print a human-readable summary of flagged IPs, worst offender first."""
    if not flagged:
        print("No brute-force patterns detected.")
        return

    print(f"{'IP ADDRESS':<18}{'FAILURES':<10}{'FIRST SEEN':<22}{'LAST SEEN':<22}USERS TRIED")
    print("-" * 95)

    # Worst offender (most failures in-window) first.
    for ip, info in sorted(flagged.items(), key=lambda kv: kv[1]["failure_count"], reverse=True):
        users = ", ".join(sorted(info["users_tried"]))
        print(
            f"{ip:<18}{info['failure_count']:<10}"
            f"{str(info['first_seen']):<22}{str(info['last_seen']):<22}{users}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Detect brute-force SSH login attempts in an auth.log-style file."
    )
    parser.add_argument("logfile", help="Path to the auth.log-style file to analyze")
    parser.add_argument(
        "--window", type=int, default=60,
        help="Rolling window size in seconds (default: 60)",
    )
    parser.add_argument(
        "--threshold", type=int, default=5,
        help="Number of failures within the window that trips a flag (default: 5)",
    )
    args = parser.parse_args()

    entries = load_log_entries(args.logfile)
    flagged = detect_brute_force(entries, window_seconds=args.window, threshold=args.threshold)
    generate_report(flagged)


if __name__ == "__main__":
    main()
