"""
Week 4 Challenge: Capstone - Mini Log Auditor CLI
Tier 0 - Level-Up Phase

Combines everything from Weeks 1-3 (argparse, re, pathlib, hashlib,
try/except, logging) into one command-line tool. See week04_challenge.md
for the full brief. Fill in each function below - the docstrings tell
you exactly what's expected. Don't skip "Plan It First" before you
start writing code.

Usage (once finished):
    python week04_starter.py sample_logs/
"""

import argparse
import hashlib
import logging
import re
from collections import Counter
from pathlib import Path

# Suspicious line patterns to scan for. Each maps a short category name
# to a compiled regex. Feel free to add more categories if you want to
# extend the tool, but these four are enough to complete the challenge
# against the provided sample_logs/ data.
SUSPICIOUS_PATTERNS = {
    "failed_login": re.compile(
        r"Failed login attempt for user '(?P<user>[^']+)' from (?P<ip>\S+)"
    ),
    "sql_injection": re.compile(r"Possible SQL injection detected"),
    "port_scan": re.compile(r"Port scan detected"),
    "unauthorized_access": re.compile(r"Unauthorized access attempt"),
}

# Setup logging globally
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def collect_log_files(directory: Path) -> list[Path]:
    """Return a sorted list of every file under `directory` (recursively)
    whose name ends in '.log'.

    This is the same "collect" stage you built in Week 2 - reuse that
    pattern (pathlib globbing + is_file()), just filtered to *.log.
    """
    files = directory.rglob("*.log")
    found_files = []

    while True:
        try:
            found_files.append(next(files))
        except StopIteration:
            break
        except (PermissionError, OSError) as e:
            logger.warning(f"Access error: {e}")
            continue
    return found_files


def hash_file(filepath: Path, chunk_size: int = 8192) -> str:
    """Compute the SHA-256 hex digest of a single file, reading it in
    chunks. This is a direct reuse of Week 2's hash_file() - copy your
    working version over.
    """
    result_hash = ""
    processer = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while file_chunk := f.read(chunk_size):
                processer.update(file_chunk)
        result_hash = processer.hexdigest()
    except (FileNotFoundError, PermissionError):
        logger.warning(f"Error: Unable to open and read file '{filepath}'")
    except OSError as e:
        logger.warning(f"System error reading '{filepath}': {e}")
    return result_hash


def scan_log_file(filepath: Path) -> Counter:
    """Read `filepath` line by line and check each line against every
    pattern in SUSPICIOUS_PATTERNS. Return a Counter mapping category
    name -> number of matching lines in this file.

    If the file can't be read (bad encoding, permissions, etc.), don't
    let the whole program crash: catch the SPECIFIC exception that
    reading a file can raise, log a warning with `logging.warning(...)`
    naming the file and the problem, and return an empty Counter for
    this file so the rest of the audit can continue.

    Hint: `Counter()` starts at zero for any key you increment, so
    `counts[category_name] += 1` works with no setup.
    """
    results_count = Counter()
    try:
        with open(filepath, "r") as f:
            for line in f:
                for find_type, pattern in SUSPICIOUS_PATTERNS.items():
                    if re.search(pattern, line):
                        results_count[find_type] += 1
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        logger.warning(f"Error: Unable to open and read file '{filepath}'")
    except OSError as e:
        logger.warning(f"System error reading '{filepath}': {e}")
    return results_count


def audit_directory(directory: Path) -> tuple[Counter, dict[Path, str]]:
    """Run the full audit over every log file in `directory`:
      - collect the files (collect_log_files)
      - for each one, compute its hash (hash_file) and scan it
        (scan_log_file)
      - combine every file's Counter into one overall Counter (two
        Counters can be added together with `+`)

    Return a tuple: (overall_counts, file_hashes), where file_hashes
    maps filepath -> hex digest for every file that was audited.
    """
    hash_lib = {}
    overall_counts = Counter()
    log_file_list = collect_log_files(directory)
    for log in log_file_list:
        hash_lib[log] = hash_file(log)
        overall_counts.update(scan_log_file(log))
    return overall_counts, hash_lib


def print_summary(
    directory: Path, overall_counts: Counter, file_hashes: dict[Path, str]
) -> None:
    """Print a readable report with two sections:

      1. Suspicious activity summary - each category from
         overall_counts and its count, ordered from most to least
         frequent (Counter.most_common() gives you this order for free).
      2. File integrity record - every audited file's path (relative to
         `directory`) and its SHA-256 hash, for the record.

    Also print a one-line total (files audited, total suspicious events
    found) at the end.
    """
    SEP_LINES = "-" * 40
    sus_string = "Suspicious Activity Summary\n" + SEP_LINES
    print(sus_string)
    for item in overall_counts.most_common():
        print(f"{item[0]}", f"{item[1]}")
    file_string = "\nFile Integrity Record\n" + SEP_LINES
    print(file_string)
    for k, v in file_hashes.items():
        print(f"{v}  {k.relative_to(directory)}")
    summary_string = f"\n{len(file_hashes)} files audited, {sum(overall_counts.values())} suspicious events found."
    print(summary_string)


def main() -> None:
    """Wire everything together:
    1. Configure logging with logging.basicConfig(...) - INFO level
       is fine, a simple format string is fine.
    2. Parse one required positional CLI argument: the directory to
       audit (use argparse, type=Path).
    3. Validate the directory exists (args.directory.is_dir()) -
       if not, use parser.error(...) like Week 2 did.
    4. Call audit_directory(), then print_summary() with the results.
    5. Wrap steps 3-4 in a try/except for anything unexpected, so a
       surprise error prints one clean line instead of a raw
       traceback. (This is a last-resort safety net - it should
       rarely actually trigger if scan_log_file already handles
       per-file errors.)
    """
    # setup logging - see above for defined logger (satisfes ruff)

    # Argparse the required directory path
    parser = argparse.ArgumentParser(
        description="a command-line tool that audits a directory of log files for suspicious activity."
    )
    parser.add_argument("directory", type=Path, help="Directroy to check for log files")
    args = parser.parse_args()

    try:
        # Check if the dir path is a directory
        if not args.directory.exists() or not args.directory.is_dir():
            parser.error("Directory name provided not valid")

        # Send valid directory to directory processing function and get results
        counts, hashes = audit_directory(args.directory)

        # print the results returned from the audit
        print_summary(args.directory, counts, hashes)

    except Exception as e:  # noqa: BLE001
        logger.warning(f"Caught unknown exception: {e}")


if __name__ == "__main__":
    main()
