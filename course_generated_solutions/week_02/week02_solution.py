"""
Week 2 Solution: Multi-File Hash Auditor
Tier 0 - Level-Up Phase

Walks a directory of sample files, computes the SHA-256 hash of each one,
and prints a report. Structured as three clear stages:
  1. collect_files()  - find what needs hashing
  2. hash_file()      - do the work for one file
  3. report_results() - present what we found

Usage:
    python week02_solution.py <directory>
"""

import argparse
import hashlib
from pathlib import Path


def collect_files(directory: Path) -> list[Path]:
    """Return a sorted list of every file (not directory) under `directory`,
    including files in subdirectories.

    Using pathlib's rglob("*") instead of os.walk keeps this one line and
    gives us Path objects (rather than raw strings) for free, which is
    what hash_file() and report_results() both expect.
    """
    return sorted(p for p in directory.rglob("*") if p.is_file())


def hash_file(filepath: Path, chunk_size: int = 8192) -> str:
    """Compute the SHA-256 hex digest of a single file.

    We read the file in fixed-size chunks rather than calling
    filepath.read_bytes() and hashing the whole thing at once. For the
    small sample files in this challenge it wouldn't matter, but this is
    the pattern you want muscle memory for: it's what keeps a hash
    auditor from falling over on a multi-gigabyte log file or disk image
    in real work.
    """
    sha256 = hashlib.sha256()
    with filepath.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def audit_directory(directory: Path) -> dict[Path, str]:
    """Collect every file under `directory` and hash each one.

    Returns a dict mapping filepath -> hex digest. A dict (rather than a
    list of tuples) is the natural choice here because callers will
    almost always want to look up "what's the hash for this file" or
    iterate key/value pairs - both of which a dict gives you directly.
    """
    files = collect_files(directory)
    return {filepath: hash_file(filepath) for filepath in files}


def report_results(directory: Path, results: dict[Path, str]) -> None:
    """Print a simple, readable report of filename -> hash."""
    print(f"SHA-256 Hash Report for: {directory}")
    print("-" * 70)
    for filepath, digest in results.items():
        rel = filepath.relative_to(directory)
        print(f"{digest}  {rel}")
    print("-" * 70)
    print(f"Total files hashed: {len(results)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute SHA-256 hashes for every file in a directory."
    )
    parser.add_argument("directory", type=Path, help="Directory of files to hash")
    args = parser.parse_args()

    if not args.directory.is_dir():
        parser.error(f"{args.directory} is not a directory")

    results = audit_directory(args.directory)
    report_results(args.directory, results)


if __name__ == "__main__":
    main()
