"""
week07_solution.py — File Integrity Checker

Reference solution for Week 7 (Tier 1: Novice, Topic 3).

Two modes:
    baseline  — walk a directory, SHA-256 every file, save a manifest (JSON).
    verify    — walk the same directory again, recompute hashes, and diff
                against the saved manifest: report unchanged / modified /
                added / removed files.

Usage:
    python week07_solution.py baseline --dir ./sample_files --out baseline.json
    python week07_solution.py verify   --dir ./sample_files --baseline baseline.json
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path


def collect_files(directory: Path) -> list[Path]:
    """Return a sorted list of all regular files under `directory` (recursive).

    Sorting isn't strictly required, but it makes output deterministic,
    which matters a lot once you start writing tests (and your own sanity
    when comparing two runs by eye).
    """
    return sorted(p for p in directory.rglob("*") if p.is_file())


def hash_file(path: Path, chunk_size: int = 8192) -> str:
    """Compute the SHA-256 hex digest of a single file.

    Files are read in fixed-size chunks rather than with `path.read_bytes()`
    so that a multi-GB file doesn't get loaded into memory all at once.
    This is the same "don't assume it fits in RAM" instinct you'll lean on
    again in Week 10's ETL pipeline.
    """
    sha256 = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def build_manifest(directory: Path) -> dict[str, str]:
    """Return {relative_path_str: sha256_hex} for every file under `directory`."""
    manifest = {}
    for path in collect_files(directory):
        rel = str(path.relative_to(directory))
        manifest[rel] = hash_file(path)
    return manifest


def save_manifest(manifest: dict[str, str], out_path: Path) -> None:
    out_path.write_text(json.dumps(manifest, indent=2, sort_keys=True))


def load_manifest(baseline_path: Path) -> dict[str, str]:
    return json.loads(baseline_path.read_text())


def diff_manifests(old: dict[str, str], new: dict[str, str]) -> dict[str, list[str]]:
    """Compare two {path: hash} manifests and bucket the results.

    Using sets of keys (not a nested loop) is the natural fit here: set
    difference/intersection directly expresses "added", "removed", and
    "in both, now check if the hash changed" — exactly the three questions
    we actually have.
    """
    old_paths = set(old.keys())
    new_paths = set(new.keys())

    added = sorted(new_paths - old_paths)
    removed = sorted(old_paths - new_paths)
    common = old_paths & new_paths
    modified = sorted(p for p in common if old[p] != new[p])
    unchanged = sorted(p for p in common if old[p] == new[p])

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
    }


def print_report(results: dict[str, list[str]]) -> None:
    print("=== File Integrity Report ===")
    print(f"Unchanged: {len(results['unchanged'])}")
    print(f"Modified:  {len(results['modified'])}")
    for p in results["modified"]:
        print(f"  [MODIFIED] {p}")
    print(f"Added:     {len(results['added'])}")
    for p in results["added"]:
        print(f"  [ADDED]    {p}")
    print(f"Removed:   {len(results['removed'])}")
    for p in results["removed"]:
        print(f"  [REMOVED]  {p}")


def run_baseline(args: argparse.Namespace) -> None:
    directory = Path(args.dir)
    if not directory.is_dir():
        print(f"Error: {directory} is not a directory", file=sys.stderr)
        sys.exit(1)

    manifest = build_manifest(directory)
    save_manifest(manifest, Path(args.out))
    print(f"Baseline written: {args.out} ({len(manifest)} files)")


def run_verify(args: argparse.Namespace) -> None:
    directory = Path(args.dir)
    baseline_path = Path(args.baseline)
    if not directory.is_dir():
        print(f"Error: {directory} is not a directory", file=sys.stderr)
        sys.exit(1)
    if not baseline_path.is_file():
        print(f"Error: baseline file {baseline_path} not found", file=sys.stderr)
        sys.exit(1)

    old_manifest = load_manifest(baseline_path)
    new_manifest = build_manifest(directory)
    results = diff_manifests(old_manifest, new_manifest)
    print_report(results)

    # Non-zero exit code when something changed — lets this plug into a
    # cron job / CI step that should "fail" on drift.
    if results["modified"] or results["added"] or results["removed"]:
        sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="SHA-256 file integrity checker")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    baseline_parser = subparsers.add_parser("baseline", help="Record file hashes")
    baseline_parser.add_argument("--dir", required=True, help="Directory to scan")
    baseline_parser.add_argument(
        "--out", default="baseline.json", help="Output manifest path"
    )
    baseline_parser.set_defaults(func=run_baseline)

    verify_parser = subparsers.add_parser("verify", help="Compare against a baseline")
    verify_parser.add_argument("--dir", required=True, help="Directory to scan")
    verify_parser.add_argument(
        "--baseline", default="baseline.json", help="Manifest to compare against"
    )
    verify_parser.set_defaults(func=run_verify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
