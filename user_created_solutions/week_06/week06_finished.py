"""
Week 6 Starter -- Password Strength Auditor
Weekly Python Security Challenge (Tier 1: Novice)

Fill in each function below. Docstrings describe the contract each
function must satisfy -- week06_test.py checks against exactly these
signatures and behaviors, so don't rename anything.
"""

import getpass
import re

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
    passed, len_string = True, f"OK ({len(password)} chars)"
    if len(password) < min_length:
        passed, len_string = (
            False,
            f"too short: {len(password)}, chars (minimum {MIN_LENGTH})",
        )
    return passed, len_string


def check_character_variety(password: str) -> tuple:
    """Check that `password` contains at least one lowercase letter,
    one uppercase letter, one digit, and one special (non-alphanumeric)
    character.

    Use the `re` module rather than four near-identical if-statements --
    consider looping over a list of (pattern, description) pairs.

    Returns a (passed: bool, message: str) tuple. On failure, the message
    should name which character class(es) are missing.
    """
    patterns = {
        r"[a-z]": "lowercase letter",
        r"[A-Z]": "uppercase letter",
        r"[^A-Za-z0-9]": "special character",
        r"[0-9]": "digit",
    }
    passed, char_var_string = True, "OK"
    missing = []
    for pattern, text in patterns.items():
        if not re.search(pattern, password):
            missing.append(text)
    if missing:
        char_var_string = "missing " + ", ".join(missing) + "."
        passed = False
        print(char_var_string)
    return passed, char_var_string


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
    passed, blockstring = True, "not found in blocklist"
    if blocklist is None:
        blocklist = DEFAULT_BLOCKLIST
    if password.lower() in {entry.lower() for entry in blocklist}:
        passed, blockstring = False, "password string is a commonly used weak password"
    return passed, blockstring


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
    result_shape = {}

    checks = [
        ("length", *check_length(password)),
        ("character_variety", *check_character_variety(password)),
        ("blocklist", *check_blocklist(password, blocklist)),
    ]

    results_list = [
        {"name": name, "passed": passed, "message": message}
        for name, passed, message in checks
    ]

    overall_pass = all(check["passed"] for check in results_list)

    result_shape["password_length"] = len(password)
    result_shape["overall_pass"] = overall_pass
    result_shape["checks"] = results_list

    return result_shape


def format_report(password_length: int, result: dict) -> str:
    """Turn the dict returned by calculate_strength_score() into a
    human-readable, multi-line report string suitable for printing.

    Should clearly show overall PASS/FAIL, plus one line per check
    showing that check's own pass/fail and message.
    """
    # NOTE: Changed 1st arg to int to send the length of the password directly
    # instead of the full password string
    # TODO: implement
    raise NotImplementedError


# NOTE: Implementing a more secure way to collect the password with getpass module
# def build_parser() -> argparse.ArgumentParser:
#     """Build the CLI parser. Single required --password argument."""
#     parser = argparse.ArgumentParser(
#         description="Audit a password against basic strength rules."
#     )
#     parser.add_argument(
#         "--password",
#         required=True,
#         help="Password to audit. (Consider: is passing a real password on "
#         "the command line -- visible in shell history and process "
#         "lists -- itself a bad habit? What would a production tool "
#         "do differently, e.g. reading from stdin instead?)",
#     )
#     return parser


def get_password() -> str:
    """Prompt the user for a password without echoing it to the terminal.

    Returns:
        The password string entered by the user.
    """
    return getpass.getpass(prompt="Enter the password you would like to check: ")


def main():
    password_string = get_password()
    result = calculate_strength_score(password_string)
    print(format_report(len(password_string), result))


if __name__ == "__main__":
    main()
