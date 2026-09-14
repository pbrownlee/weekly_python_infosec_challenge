#!/usr/bin/env python3
"""
Week 1 SOLUTION — CLI Security Utils Toolkit
=============================================

A small command-line tool with two subcommands:

  cipher    ROT-N shift-cipher encode/decode
  checkpw   Password-rule strength check (built with the `re` module)

Usage examples:
    python week01_solution.py cipher --mode encode --shift 3 --text "Attack at dawn"
    python week01_solution.py cipher --mode decode --shift 3 --text "Dwwdfn dw gdzq"
    python week01_solution.py checkpw --password "Str0ng!Pass"

New skills demonstrated: argparse subcommands, the `re` module, and
organizing a program into small single-purpose functions plus main().
"""

import argparse
import re


# ---------------------------------------------------------------------------
# Cipher logic
# ---------------------------------------------------------------------------

def rot_n_shift(text: str, shift: int) -> str:
    """
    Shift every alphabetic character in `text` by `shift` positions,
    wrapping around the 26-letter alphabet. Case is preserved.
    Non-alphabetic characters (spaces, punctuation, digits) pass through
    unchanged.

    A negative `shift` naturally decodes what a positive `shift` encoded,
    because Python's % operator always returns a non-negative result for
    a positive modulus, even when the left-hand side is negative.
    """
    result_chars = []
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            shifted = (ord(ch) - base + shift) % 26
            result_chars.append(chr(base + shifted))
        else:
            result_chars.append(ch)
    return "".join(result_chars)


def run_cipher(args: argparse.Namespace) -> None:
    """Dispatch the `cipher` subcommand: encode or decode based on args.mode."""
    if args.mode == "encode":
        output = rot_n_shift(args.text, args.shift)
    else:  # "decode"
        output = rot_n_shift(args.text, -args.shift)
    print(output)


# ---------------------------------------------------------------------------
# Password rule check
# ---------------------------------------------------------------------------

# Small illustrative blocklist. In a real tool this would be a much larger
# file of known-bad/breached passwords.
COMMON_PASSWORD_BLOCKLIST = {"password", "12345678", "qwerty123", "letmein"}

MIN_LENGTH = 8


def check_password(password: str) -> list[str]:
    """
    Check `password` against a small set of strength rules.
    Returns a list of human-readable failure messages.
    An empty list means the password passed every rule.
    """
    failures = []

    if len(password) < MIN_LENGTH:
        failures.append(f"Must be at least {MIN_LENGTH} characters long.")

    if not re.search(r"[A-Z]", password):
        failures.append("Must contain at least one uppercase letter.")

    if not re.search(r"[a-z]", password):
        failures.append("Must contain at least one lowercase letter.")

    if not re.search(r"[0-9]", password):
        failures.append("Must contain at least one digit.")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password):
        failures.append("Must contain at least one special character.")

    if password.lower() in COMMON_PASSWORD_BLOCKLIST:
        failures.append("Must not be a commonly used/breached password.")

    return failures


def run_checkpw(args: argparse.Namespace) -> None:
    """Dispatch the `checkpw` subcommand: run the checks and print a report."""
    failures = check_password(args.password)
    if not failures:
        print("PASS: password meets all strength rules.")
    else:
        print("FAIL: password does not meet the following rules:")
        for msg in failures:
            print(f"  - {msg}")


# ---------------------------------------------------------------------------
# Argument parsing / program structure
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the top-level parser with 'cipher' and 'checkpw' subcommands."""
    parser = argparse.ArgumentParser(
        prog="week01_solution.py",
        description="CLI Security Utils Toolkit: ROT-N cipher + password checker.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    cipher_parser = subparsers.add_parser("cipher", help="ROT-N shift cipher")
    cipher_parser.add_argument(
        "--mode", choices=["encode", "decode"], required=True,
        help="Whether to encode or decode --text.",
    )
    cipher_parser.add_argument(
        "--shift", type=int, required=True,
        help="Number of alphabet positions to shift.",
    )
    cipher_parser.add_argument(
        "--text", required=True,
        help="The text to encode or decode.",
    )
    cipher_parser.set_defaults(func=run_cipher)

    checkpw_parser = subparsers.add_parser("checkpw", help="Password rule check")
    checkpw_parser.add_argument(
        "--password", required=True,
        help="The password to check against the strength rules.",
    )
    checkpw_parser.set_defaults(func=run_checkpw)

    return parser


def main() -> None:
    """Entry point: parse arguments and dispatch to the right subcommand."""
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
