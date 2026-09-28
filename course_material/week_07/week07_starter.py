"""
Week 7 Starter — File Integrity Checker
Tier 1: Novice (Topic 3)

Two modes:
  baseline  -- hash every file in a directory, save results to a JSON file
  verify    -- re-hash the directory and compare against a saved baseline

Fill in the function bodies below. Functions are fully decomposed for you
this week (Tier 1) -- your job is the logic inside each one, not the overall
shape of the program.
"""

import argparse
from pathlib import Path

CHUNK_SIZE = 8192  # read files in chunks, not all at once


def compute_file_hash(filepath: Path) -> str:
    """Compute the SHA-256 hex digest of a file's contents.

    Read the file in CHUNK_SIZE-byte chunks (use hashlib's .update() in a loop)
    rather than calling .read() with no argument -- this is what makes the
    approach scale to files too large to comfortably hold in memory.
    """
    # TODO: implement
    raise NotImplementedError


def collect_files(directory: Path) -> list[Path]:
    """Return a list of all files (not directories) under `directory`, recursively.

    Hint: pathlib.Path has a method for exactly this kind of recursive glob.
    """
    # TODO: implement
    raise NotImplementedError


def build_baseline(directory: Path) -> dict[str, str]:
    """Walk `directory`, hash every file, and return a dict mapping the file's
    path RELATIVE TO `directory` (as a string, forward-slash form) to its hash.

    Using relative paths as keys (not absolute paths) is what makes the
    resulting baseline.json portable if the directory gets moved or copied.
    """
    # TODO: implement
    raise NotImplementedError


def save_baseline(baseline: dict[str, str], output_path: Path) -> None:
    """Write the baseline dict to `output_path` as JSON."""
    # TODO: implement
    raise NotImplementedError


def load_baseline(baseline_path: Path) -> dict[str, str]:
    """Load a previously saved baseline JSON file into a dict.

    Should raise a clear, caught error (not let a raw traceback escape to the
    user) if the file doesn't exist -- see how main() is expected to handle this.
    """
    # TODO: implement
    raise NotImplementedError


def verify_against_baseline(
    directory: Path, baseline: dict[str, str]
) -> dict[str, list[str]]:
    """Re-hash `directory` and compare against `baseline`.

    Return a dict with four keys: "unchanged", "modified", "added", "removed",
    each mapping to a list of relative file path strings.

    Think in terms of set operations on the keys of the two dicts (current
    hashes vs. baseline hashes) -- see Hint 3 in the challenge if you're stuck.
    """
    # TODO: implement
    raise NotImplementedError


def print_report(report: dict[str, list[str]]) -> None:
    """Print a human-readable summary of the verify report."""
    # TODO: implement
    raise NotImplementedError


def main() -> None:
    parser = argparse.ArgumentParser(description="File Integrity Checker")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    baseline_parser = subparsers.add_parser(
        "baseline", help="Create a baseline of file hashes"
    )
    baseline_parser.add_argument("--dir", required=True, help="Directory to scan")
    baseline_parser.add_argument(
        "--output", required=True, help="Path to save baseline JSON"
    )

    verify_parser = subparsers.add_parser(
        "verify", help="Verify a directory against a baseline"
    )
    verify_parser.add_argument("--dir", required=True, help="Directory to scan")
    verify_parser.add_argument(
        "--baseline", required=True, help="Path to baseline JSON to compare against"
    )

    args = parser.parse_args()

    if args.mode == "baseline":
        directory = Path(args.dir)
        baseline = build_baseline(directory)
        save_baseline(baseline, Path(args.output))
        print(f"Baseline saved: {len(baseline)} files hashed -> {args.output}")

    elif args.mode == "verify":
        directory = Path(args.dir)
        try:
            baseline = load_baseline(Path(args.baseline))
        except FileNotFoundError:
            print(f"[!] Baseline file not found: {args.baseline}")
            print("    Run 'baseline' mode first to create one.")
            return
        report = verify_against_baseline(directory, baseline)
        print_report(report)


if __name__ == "__main__":
    main()
