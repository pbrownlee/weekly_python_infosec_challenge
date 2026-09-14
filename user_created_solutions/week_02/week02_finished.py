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
    files = directory.rglob("*")
    return [f for f in files if f.is_file()]


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
    result_hash = ""
    processer = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while file_chunk := f.read(CHUNK_SIZE):
                processer.update(file_chunk)
        result_hash = processer.hexdigest()
    except FileNotFoundError:
        print(f"Error: Unable to open and read file '{filepath}'")
    except PermissionError:
        print(f"Error: Insufficent permissions reading '{filepath}'")
    except OSError as e:
        print(f"System error reading '{filepath}': {e}")
    except Exception as e: # noqa: BLE001 -- deliberate fault-isolation boundary: one file in a batch, always logged, never swallowed
        print(f"General error reading '{filepath}': {e}")
    return result_hash


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
    format_string = "Printing Hash values for each file: \n"
    none_count = 0
    for f, hash_result in file_hashes.items():
        if hash_result:
            format_string += f"{f.relative_to(base_directory)} - {hash_result} \n"
        else:
            format_string += f"{f.relative_to(base_directory)} - NONE: encountered issue processing file \n"
            none_count += 1
    format_string += "\n"
    format_string += f"Total file(s) hashed: {len(file_hashes.keys())} \n"
    format_string += f"Total file(s) with issues: {none_count} \n"
    return format_string


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
    parser = argparse.ArgumentParser(
        description="Walk a directory of files, compute the SHA-256 hash of each one, and print "
        "a report of filename -> hash."
    )
    parser.add_argument(
        "directory", type=str, help="The directory to look for files to hash"
    )
    args = parser.parse_args()

    start_path = Path(args.directory)

    # checks to see if start_path is an actual directory
    if start_path.exists() and start_path.is_dir():
        # get a list inventory of all the files
        valid_files = collect_files(start_path)
        # then find the hash values of those files
        file_hash_collection = {}
        for f in valid_files:
            file_hash_collection[f] = hash_file(f)
        # then make a report based on the results
        result_report = build_report(file_hash_collection, start_path)
        print(result_report)
    else:
        print(f"Error: directory '{start_path}' is not a valid directory")


if __name__ == "__main__":
    main()
