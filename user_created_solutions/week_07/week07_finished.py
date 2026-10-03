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
import hashlib
import json
import logging
from pathlib import Path

# Setup logging globally
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

CHUNK_SIZE = 8192  # read files in chunks, not all at once


def compute_file_hash(filepath: Path) -> str:
    """Compute the SHA-256 hex digest of a file's contents.

    Read the file in CHUNK_SIZE-byte chunks (use hashlib's .update() in a loop)
    rather than calling .read() with no argument -- this is what makes the
    approach scale to files too large to comfortably hold in memory.
    """
    result_hash = ""
    processer = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while file_chunk := f.read(CHUNK_SIZE):
                processer.update(file_chunk)
        result_hash = processer.hexdigest()
    except (FileNotFoundError, PermissionError):
        logger.warning(f"Error: Unable to open and read file '{filepath}'")
    except OSError as e:
        logger.warning(f"System error reading '{filepath}': {e}")
    return result_hash


def collect_files(directory: Path) -> list[Path]:
    """Return a list of all files (not directories) under `directory`, recursively.

    Hint: pathlib.Path has a method for exactly this kind of recursive glob.
    """
    if directory.is_dir():
        files = directory.rglob("*")
        return [f for f in files if f.is_file()]
    else:
        raise NotADirectoryError(f"Expected a directory for: {directory}")


def build_baseline(directory: Path) -> dict[str, str]:
    """Walk `directory`, hash every file, and return a dict mapping the file's
    path RELATIVE TO `directory` (as a string, forward-slash form) to its hash.

    Using relative paths as keys (not absolute paths) is what makes the
    resulting baseline.json portable if the directory gets moved or copied.
    """
    baseline_shape = {}
    directory = directory.resolve()
    for f in collect_files(directory):
        rel_key = f.relative_to(directory).as_posix()
        baseline_shape[rel_key] = compute_file_hash(f)
    return baseline_shape


def save_baseline(baseline: dict[str, str], output_path: Path) -> None:
    """Write the baseline dict to `output_path` as JSON."""
    with open(output_path, "w") as f:
        json.dump(baseline, f, indent=2)


def load_baseline(baseline_path: Path) -> dict[str, str]:
    """Load a previously saved baseline JSON file into a dict.

    Should raise a clear, caught error (not let a raw traceback escape to the
    user) if the file doesn't exist -- see how main() is expected to handle this.
    """
    if baseline_path.exists() and baseline_path.is_file():
        with open(baseline_path, "r", encoding="utf-8") as f:
            baseline_file = json.load(f)
            return baseline_file
    else:
        raise FileNotFoundError


def verify_against_baseline(
    directory: Path, baseline: dict[str, str]
) -> dict[str, list[str]]:
    """Re-hash `directory` and compare against `baseline`.

    Return a dict with four keys: "unchanged", "modified", "added", "removed",
    each mapping to a list of relative file path strings.

    Think in terms of set operations on the keys of the two dicts (current
    hashes vs. baseline hashes) -- see Hint 3 in the challenge if you're stuck.
    """
    results_shape = {}
    # get a new baseline from the passed directory
    new_base = build_baseline(directory)
    # log added files
    results_shape["added"] = [keys for keys in (new_base.keys() - baseline.keys())]
    # log removed files
    results_shape["removed"] = [keys for keys in (baseline.keys() - new_base.keys())]
    # compare hashes for remaining files
    modified_list = []
    unchanged_list = []
    for key, old_hash in baseline.items():
        if key in new_base:
            if old_hash == new_base[key]:
                unchanged_list.append(key)
            else:
                modified_list.append(key)
    results_shape["modified"] = modified_list
    results_shape["unchanged"] = unchanged_list
    return results_shape


def print_report(report: dict[str, list[str]], char_string: str = "-") -> None:
    """Print a human-readable summary of the verify report."""
    body = []
    for label, key in (
        ("MODIFIED", "modified"),
        ("ADDED", "added"),
        ("REMOVED", "removed"),
    ):
        body += [f"{label}: {path}" for path in report[key]]

    title = "File Integrity Report"
    summary = (
        f"Unchanged: {len(report['unchanged'])} Modified: {len(report['modified'])} "
        f"Added: {len(report['added'])} Removed: {len(report['removed'])}"
    )

    sep = char_string * max(len(line) for line in [title, summary, *body])
    print("\n".join(["", title, sep, *body, sep, summary]))


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
        try:
            baseline = build_baseline(directory)
        except NotADirectoryError as e:
            logger.error(e)
            return
        try:
            save_baseline(baseline, Path(args.output))
        except (IsADirectoryError, PermissionError) as e:
            logger.error(f"Unable to open and save baseline file : {e}")
            return
        print(f"Baseline saved: {len(baseline)} files hashed -> {args.output}")

    elif args.mode == "verify":
        directory = Path(args.dir)
        try:
            baseline = load_baseline(Path(args.baseline))
        except FileNotFoundError:
            print(f"[!] Baseline file not found: {args.baseline}")
            print("    Run 'baseline' mode first to create one.")
            return
        try:
            report = verify_against_baseline(directory, baseline)
        except NotADirectoryError as e:
            logger.error(f"Unable to scan directory: {e}")
            return
        print_report(report)


if __name__ == "__main__":
    main()
