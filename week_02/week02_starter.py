#!/usr/bin/env python3
"""
Week 2 STARTER — Multi-File Hash Auditor
==========================================

Walk a directory of files, compute the SHA-256 hash of each one, and print
a report of filename -> hash.

Fill in the TODOs below. The function breakdown is given for you this
week — your job is the implementation, not the structure. Run this file
against a test folder you create yourself (see the "Sample Data" section
of week02_challenge.md).

Usage:
    python week02_starter.py <directory>
"""

import argparse
import hashlib
from pathlib import Path

CHUNK_SIZE = 8192  # bytes to read at a time -- keeps memory usage flat
                    # even for very large files.


def collect_files(directory: Path) -> list[Path]:
    """
    Return a list of all FILES (not directories) found anywhere under
    `directory`, including files in subfolders.

    TODO:
      - Use directory.rglob("*") (or an equivalent pathlib approach) to
        walk the tree.
      - Filter out anything that isn't a file (e.g. subdirectories
        themselves should not appear in the returned list).
    """
    raise NotImplementedError


def hash_file(filepath: Path) -> str:
    """
    Compute and return the SHA-256 hex digest of the file at `filepath`.

    TODO:
      - Open the file in binary mode ("rb").
      - Read it in CHUNK_SIZE-byte chunks in a loop (do not use a bare
        .read() with no argument -- the point is to avoid loading huge
        files entirely into memory).
      - Feed each chunk into a hashlib.sha256() object via .update().
      - Return the final .hexdigest() once the whole file has been read.
    """
    raise NotImplementedError


def build_report(file_hashes: dict[Path, str], base_directory: Path) -> str:
    """
    Given a dict mapping file Path -> hex digest, return a single
    formatted string report ready to print, plus a final summary line
    with the total file count.

    TODO:
      - For readability, consider printing each file's path RELATIVE to
        `base_directory` (see Path.relative_to) rather than the full
        absolute path.
      - Include a final line like "N file(s) hashed."
    """
    raise NotImplementedError


def main() -> None:
    """
    Entry point: parse the directory argument, collect files, hash each
    one, and print the report.

    TODO:
      - Set up argparse with a single positional "directory" argument.
      - Call collect_files(), then hash_file() for each result, building
        up a {path: digest} dict.
      - Call build_report() and print it.
      - Think about what should happen if the given directory doesn't
        exist, or exists but is empty -- handle both without crashing
        with an ugly traceback.
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
