"""
Week 6 Starter -- Password Strength Auditor
Weekly Python Security Challenge (Tier 1: Novice)

Fill in each function below. Docstrings describe the contract each
function must satisfy -- week06_test.py checks against exactly these
signatures and behaviors, so don't rename anything.
"""

import argparse

# A small, deliberately-not-exhaustive blocklist of common weak passwords.
# Feel free to extend it.
DEFAULT_BLOCKLIST = {
    "password",
    "password1",
    "123456",
    "12345678",
    "qwerty",
    "letmein",
    "admin",
    "welcome",
    "iloveyou",
    "111111",
}

MIN_LENGTH = 12


def check_length(password: str, min_length: int = MIN_LENGTH) -> tuple:
    """Check whether `password` meets the minimum length requirement.

    Returns a (passed: bool, message: str) tuple, e.g.:
        (True, "Length OK (14 chars)")
        (False, "Too short: 6 chars (minimum 12)")
    """
    # TODO: implement
    raise NotImplementedError


def check_character_variety(password: str) -> tuple:
    """Check that `password` contains at least one lowercase letter,
    one uppercase letter, one digit, and one special (non-alphanumeric)
    character.

    Use the `re` module rather than four near-identical if-statements --
    consider looping over a list of (pattern, description) pairs.

    Returns a (passed: bool, message: str) tuple. On failure, the message
    should name which character class(es) are missing.
    """
    # TODO: implement
    raise NotImplementedError


def check_blocklist(password: str, blocklist: set | None = None) -> tuple:
    """Check `password` (case-insensitively) against `blocklist`
    (defaults to DEFAULT_BLOCKLIST when not provided).

    Returns a (passed: bool, message: str) tuple.

    NOTE: don't give this function a mutable default argument directly
    (i.e. don't write `blocklist: set = DEFAULT_BLOCKLIST` or, worse,
    `blocklist: set = set()` in the signature). Pass None and substitute
    DEFAULT_BLOCKLIST *inside* the function body instead. If that
    reasoning isn't immediately obvious, revisit the Week 3
    "Fix the Bugs" challenge.
    """
    # TODO: implement
    raise NotImplementedError


def calculate_strength_score(password: str, blocklist: set | None = None) -> dict:
    """Run all three checks above and aggregate the results.

    Returns a dict shaped like:
        {
            "password_length": len(password),
            "overall_pass": bool,          # True only if ALL checks pass
            "checks": [
                {"name": "length", "passed": bool, "message": str},
                {"name": "character_variety", "passed": bool, "message": str},
                {"name": "blocklist", "passed": bool, "message": str},
            ],
        }

    Decide on this exact shape before writing the function body --
    format_report() below depends on it staying stable.
    """
    # TODO: implement
    raise NotImplementedError


def format_report(password: str, result: dict) -> str:
    """Turn the dict returned by calculate_strength_score() into a
    human-readable, multi-line report string suitable for printing.

    Should clearly show overall PASS/FAIL, plus one line per check
    showing that check's own pass/fail and message.
    """
    # TODO: implement
    raise NotImplementedError


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser. Single required --password argument."""
    parser = argparse.ArgumentParser(
        description="Audit a password against basic strength rules."
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Password to audit. (Consider: is passing a real password on "
        "the command line -- visible in shell history and process "
        "lists -- itself a bad habit? What would a production tool "
        "do differently, e.g. reading from stdin instead?)",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    result = calculate_strength_score(args.password)
    print(format_report(args.password, result))


if __name__ == "__main__":
    main()
