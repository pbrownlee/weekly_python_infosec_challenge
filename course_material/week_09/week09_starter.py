"""
Week 9 Starter — Brute-Force Log Analyzer  (Tier 2: Beginner, Topic 5)

Parse an auth.log-style file, detect repeated failed logins from the same IP
within a rolling time window, and flag likely brute-force sources.

Fill in the TODOs. Function signatures, argparse flags, and return shapes
below are fixed -- keep them exactly as given so next week's reference
solution (and this week's CI tests) line up with what you build.
"""

import argparse
import re

# Example line this must handle:
# "2026-10-10 02:30:11 sshd[1021]: Failed password for invalid user admin from 203.0.113.50 port 44210 ssh2"
# "2026-10-10 02:14:01 sshd[1021]: Accepted password for paul from 10.0.0.5 port 51200 ssh2"
LOG_LINE_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"sshd\[\d+\]: (?P<status>Accepted|Failed) password for "
    r"(?:invalid user )?(?P<user>\S+) from (?P<ip>\d{1,3}(?:\.\d{1,3}){3}) port \d+ ssh2$"
)

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def parse_log_line(line):
    """
    Parse a single auth.log-style line.

    Returns a dict: {"timestamp": datetime, "status": "Accepted"|"Failed",
    "user": str, "ip": str}
    Returns None if the line doesn't match the expected format (don't raise --
    real log files always have a few lines that don't match; skip them).
    """
    # TODO: use LOG_LINE_PATTERN.match(line) and build the dict,
    # converting match.group("timestamp") to a datetime with TIMESTAMP_FORMAT.
    raise NotImplementedError


def load_log_entries(filepath):
    """
    Read `filepath` line by line and return a list of parsed entries
    (the dicts from parse_log_line), skipping any line that fails to parse.
    """
    # TODO: open the file, parse_log_line() each line, collect the non-None results.
    raise NotImplementedError


def find_brute_force_ips(entries, window_seconds=60, threshold=5):
    """
    Given a list of parsed log entries, find IPs with at least `threshold`
    FAILED login attempts occurring within any `window_seconds`-second span.

    Returns a dict: {ip: [timestamp, timestamp, ...]} containing, for each
    flagged IP, the sorted timestamps of the failed attempts that triggered
    the flag. IPs that never reach the threshold are not included.

    Hint: group failed attempts by IP first, sort each IP's timestamps, then
    slide a window across them -- for each attempt, count how many other
    attempts from the same IP fall within `window_seconds` after it.
    """
    # TODO
    raise NotImplementedError


def generate_report(flagged_ips):
    """
    Build a human-readable report string summarizing the flagged IPs.
    If flagged_ips is empty, return a one-line "no brute-force activity
    detected" message instead.
    """
    # TODO
    raise NotImplementedError


def main():
    parser = argparse.ArgumentParser(
        description="Detect brute-force login attempts in an auth.log-style file."
    )
    parser.add_argument(
        "--logfile", required=True, help="Path to the log file to analyze"
    )
    parser.add_argument(
        "--window", type=int, default=60, help="Rolling window in seconds (default: 60)"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=5,
        help="Minimum failed attempts within window to flag (default: 5)",
    )
    args = parser.parse_args()

    entries = load_log_entries(args.logfile)
    flagged = find_brute_force_ips(
        entries, window_seconds=args.window, threshold=args.threshold
    )
    print(generate_report(flagged))


if __name__ == "__main__":
    main()
