"""
Week 1 — CLI Security Utils Toolkit (starter)

Two subcommands:
    cipher   - ROT-N shift cipher, encode or decode
    checkpw  - password strength rule check

Fill in the TODO sections. The function boundaries are already laid out
for you this week — later weeks will ask you to design more of this
structure yourself, so pay attention to *why* the program is split up
this way, not just *what* goes in each blank.

Run examples (once implemented):
    python week01_starter.py cipher "Hello, World!" --shift 3
    python week01_starter.py cipher "Khoor, Zruog!" --shift 3 --decode
    python week01_starter.py checkpw "pass1"
"""

import argparse
import re


# ---------------------------------------------------------------------------
# Cipher logic
# ---------------------------------------------------------------------------

def shift_char(char: str, shift: int) -> str:
    """
    Shift a single character by `shift` positions in the alphabet.

    Letters wrap around (A -> B -> ... -> Z -> A) and preserve case.
    Non-letter characters (spaces, punctuation, digits, etc.) are
    returned unchanged.

    Work out the math for one uppercase letter and one lowercase
    letter by hand before writing this (see the challenge's worked
    trace example).
    """
    # TODO: implement
    raise NotImplementedError


def rot_n_transform(text: str, shift: int) -> str:
    """
    Apply shift_char() to every character in `text` and return the
    resulting string.

    This function does NOT need to know anything about encode vs.
    decode — that distinction is handled by the sign of `shift`
    before this function is ever called.
    """
    # TODO: implement (hint: build a list of shifted characters,
    # then "".join() them)
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Password rule checking
# ---------------------------------------------------------------------------

MIN_PASSWORD_LENGTH = 8

# A symbol, for our purposes, is any non-alphanumeric, non-whitespace
# character. Feel free to adjust this pattern if you want to be stricter.
SYMBOL_PATTERN = re.compile(r"[^\w\s]")


def check_password_rules(password: str) -> dict:
    """
    Evaluate `password` against the strength rules and return a dict
    mapping a human-readable rule description to True (passed) or
    False (failed).

    Expected keys (exact strings, so the report formatter and any
    tests can rely on them):
        "Length >= 8 characters"
        "Contains a digit"
        "Contains an uppercase letter"
        "Contains a lowercase letter"
        "Contains a symbol"

    Use re.search() for the pattern-based rules (digit, uppercase,
    lowercase, symbol) — this is the point of this week's re practice,
    not a plain character-by-character loop.
    """
    # TODO: implement
    raise NotImplementedError


def format_password_report(results: dict) -> str:
    """
    Turn the dict returned by check_password_rules() into the
    printable report shown in the challenge's example usage, e.g.:

        Password strength report:
          [FAIL] Length >= 8 characters
          [PASS] Contains a digit
          ...
        Overall: WEAK (2/5 rules passed)

    Overall label suggestion: "STRONG" if all rules pass, "WEAK"
    otherwise — but feel free to add a "MODERATE" tier if you want to
    go a bit further than the minimum.

    Notice this function only *formats* — it does not compute
    anything about the password itself. Keeping "compute" and
    "print/format" separate is deliberate; it's a structuring habit
    worth keeping as programs get bigger.
    """
    # TODO: implement
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Subcommand handlers (each one takes the parsed argparse Namespace)
# ---------------------------------------------------------------------------

def run_cipher(args: argparse.Namespace) -> None:
    """
    Handle the `cipher` subcommand: figure out the effective shift
    (negate it if --decode was passed), run the transform, and print
    the result.
    """
    # TODO: implement
    raise NotImplementedError


def run_checkpw(args: argparse.Namespace) -> None:
    """
    Handle the `checkpw` subcommand: run the rule checks and print
    the formatted report.
    """
    # TODO: implement
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Argument parsing and entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """
    Build and return the top-level ArgumentParser, with two
    subparsers: "cipher" and "checkpw".

    cipher subcommand needs:
        text            (positional, the text to transform)
        --shift         (required int, the shift amount)
        --decode        (flag, store_true — if present, decode instead
                          of encode)

    checkpw subcommand needs:
        password        (positional, the password to check)
    """
    parser = argparse.ArgumentParser(
        description="CLI security utils: ROT-N cipher and password strength check."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # TODO: build the "cipher" subparser and add its arguments

    # TODO: build the "checkpw" subparser and add its arguments

    return parser


def main() -> None:
    """
    Parse arguments and dispatch to the right subcommand handler.
    """
    parser = build_parser()
    args = parser.parse_args()

    # TODO: dispatch on args.command to run_cipher() or run_checkpw()
    raise NotImplementedError


if __name__ == "__main__":
    main()
