#!/usr/bin/env python3
"""
Week 4 Solution — Capstone: Mini Log Auditor CLI

Combines everything from weeks 1-3:
  - argparse (week 1)          -> CLI structure
  - re (week 1)                -> suspicious-pattern matching
  - pathlib + hashlib (week 2) -> walking a directory, fingerprinting files
  - try/except + logging (week 3) -> resilient file handling, real diagnostics
  - collections.Counter (new this week) -> tallying findings

Usage:
    python week04_solution.py --dir sample_logs
    python week04_solution.py --dir sample_logs --verbose
"""

import argparse
import hashlib
import logging
from collections import Counter
from pathlib import Path
import re

logger = logging.getLogger("log_auditor")

# --------------------------------------------------------------------------
# Suspicious-pattern definitions.
#
# Each entry maps a human-readable label (used in the summary report) to a
# compiled regex. Keeping this as a single table -- rather than scattering
# `if "failed password" in line` checks through the code -- means adding a
# new detection rule later is a one-line change, not a new branch.
# --------------------------------------------------------------------------
PATTERNS = {
    "failed_login": re.compile(r"failed password", re.IGNORECASE),
    "invalid_user": re.compile(r"invalid user", re.IGNORECASE),
    "sql_injection_attempt": re.compile(r"(\bunion\s+select\b|'\s*or\s*'1'\s*=\s*'1)", re.IGNORECASE),
    "path_traversal_attempt": re.compile(r"\.\./\.\./"),
    "root_login_attempt": re.compile(r"session opened for user root", re.IGNORECASE),
}


def find_log_files(directory: Path) -> list[Path]:
    """Return every *.log file under `directory`, sorted for deterministic output.

    Using rglob (not glob) means log files in subfolders are picked up too --
    a real log directory is rarely perfectly flat.
    """
    return sorted(directory.rglob("*.log"))


def hash_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file, reading it in fixed-size chunks.

    Chunked reading (not path.read_bytes()) keeps this safe even if a log file
    is unexpectedly huge -- the whole file never has to sit in memory at once.
    """
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_file_for_patterns(path: Path) -> Counter:
    """Scan one log file line-by-line and return a Counter of pattern hits.

    Returns an empty Counter (not None, not an exception) if the file can't be
    read -- the error is logged, but one bad file should never crash the whole
    audit run. This is the "try/except + logging" lesson from week 3 applied
    for real: fail loudly in the log, but keep going.
    """
    hits = Counter()
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line_number, line in enumerate(f, start=1):
                for label, pattern in PATTERNS.items():
                    if pattern.search(line):
                        hits[label] += 1
                        logger.debug("%s:%d matched '%s'", path.name, line_number, label)
    except OSError as exc:
        logger.error("Could not read %s: %s", path, exc)
    return hits


def audit_directory(directory: Path) -> tuple[Counter, dict[str, str]]:
    """Run the full audit over a directory: hash every file, tally every hit.

    Returns (total_counts, file_hashes) so main() can print both the security
    summary and a simple integrity manifest.
    """
    total_counts = Counter()
    file_hashes: dict[str, str] = {}

    for log_file in find_log_files(directory):
        try:
            file_hashes[str(log_file)] = hash_file(log_file)
        except OSError as exc:
            logger.error("Could not hash %s: %s", log_file, exc)
            continue

        file_counts = scan_file_for_patterns(log_file)
        total_counts.update(file_counts)

        if file_counts:
            logger.info("%s: %s", log_file.name, dict(file_counts))
        else:
            logger.info("%s: no suspicious activity", log_file.name)

    return total_counts, file_hashes


def print_summary(total_counts: Counter, file_hashes: dict[str, str]) -> None:
    """Print the final human-readable report."""
    print("\n=== Suspicious Activity Summary ===")
    if not total_counts:
        print("No suspicious activity detected.")
    else:
        # most_common() with no argument sorts every label by count, descending --
        # exactly the "what should I look at first" ordering a report needs.
        for label, count in total_counts.most_common():
            print(f"  {label:<25} {count}")

    print(f"\n=== Files Audited ({len(file_hashes)}) ===")
    for path_str, digest in file_hashes.items():
        print(f"  {path_str}\n    sha256: {digest}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mini Log Auditor -- scan a directory of log files for suspicious activity."
    )
    parser.add_argument("--dir", required=True, type=Path, help="Directory of *.log files to audit")
    parser.add_argument("--verbose", action="store_true", help="Show per-line debug detail")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    if not args.dir.is_dir():
        logger.error("%s is not a directory", args.dir)
        raise SystemExit(1)

    total_counts, file_hashes = audit_directory(args.dir)
    print_summary(total_counts, file_hashes)


if __name__ == "__main__":
    main()
