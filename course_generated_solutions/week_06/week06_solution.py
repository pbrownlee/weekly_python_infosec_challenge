"""
Week 6 Solution — Password Strength Auditor
Tier 1: Novice (Topic 2)

Scores a password against a set of rules (length, character-class variety,
a blocklist of common weak passwords) and gives clear pass/fail feedback.

Usage:
    python week06_solution.py --password "Sup3r$ecret!"
    python week06_solution.py --password "password123" --blocklist blocklist.txt
"""

import argparse
import re
from pathlib import Path

# A small built-in blocklist so the tool works with zero setup.
# A bigger, file-based list can be supplied with --blocklist.
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
    "abc123",
    "monkey",
    "dragon",
    "football",
    "111111",
    "123123",
}

MIN_LENGTH = 12  # NIST-ish modern guidance leans toward length over complexity rules


def load_blocklist(path: str | None) -> set[str]:
    """Return the set of blocked passwords, merging the file (if given) with the default list.

    Lowercased on load so blocklist checks are case-insensitive — 'Password1' should
    be caught just as easily as 'password1'.
    """
    blocklist = {p.lower() for p in DEFAULT_BLOCKLIST}
    if path:
        file_path = Path(path)
        if not file_path.exists():
            print(
                f"[!] Blocklist file not found: {path} (continuing with built-in list only)"
            )
            return blocklist
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                word = line.strip().lower()
                if word:
                    blocklist.add(word)
    return blocklist


def check_length(password: str, min_length: int = MIN_LENGTH) -> tuple[bool, str]:
    """Check password meets the minimum length. Returns (passed, message)."""
    if len(password) >= min_length:
        return True, f"Length OK ({len(password)} >= {min_length})"
    return False, f"Too short ({len(password)} chars, need at least {min_length})"


def check_character_variety(password: str) -> dict[str, bool]:
    """Return which character classes are present in the password.

    Using re.search with character-class patterns rather than manually looping
    character-by-character — it's more readable and less error-prone than
    hand-rolling the check with isupper()/isdigit() etc. in a loop, though
    that hand-rolled version works too and is worth knowing as the fallback.
    """
    return {
        "lowercase": bool(re.search(r"[a-z]", password)),
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "digit": bool(re.search(r"\d", password)),
        "symbol": bool(re.search(r"[^\w\s]", password)),
    }


def check_against_blocklist(password: str, blocklist: set[str]) -> bool:
    """Return True if the password (lowercased) is NOT in the blocklist."""
    return password.lower() not in blocklist


def score_password(password: str, blocklist: set[str]) -> tuple[int, list[str]]:
    """Score a password from 0-5 and collect human-readable feedback lines.

    Scoring (simple, additive — easy to explain to a reviewer):
      +1 length OK
      +1 per character class present (lowercase/uppercase/digit/symbol), capped so
         the 4 classes contribute at most 3 points (variety matters, but shouldn't
         dominate a score more than length does)
      Automatic score = 0 if the password is on the blocklist, no matter what else
         passes — a blocklisted password is unsafe regardless of length/variety.
    """
    feedback = []

    if not check_against_blocklist(password, blocklist):
        feedback.append(
            "FAIL: password appears in the blocklist of common/weak passwords"
        )
        return 0, feedback

    score = 0

    length_ok, length_msg = check_length(password)
    feedback.append(("PASS: " if length_ok else "WARN: ") + length_msg)
    if length_ok:
        score += 1

    variety = check_character_variety(password)
    classes_present = sum(variety.values())
    missing = [name for name, present in variety.items() if not present]
    if missing:
        feedback.append(f"WARN: missing character classes: {', '.join(missing)}")
    else:
        feedback.append("PASS: contains lowercase, uppercase, digit, and symbol")
    # cap variety's contribution at 3 points even though there are 4 classes
    score += min(classes_present, 3)

    feedback.append("PASS: not found in blocklist")

    return score, feedback


def classify_strength(score: int) -> str:
    """Map a 0-5 score to a strength label."""
    if score <= 1:
        return "WEAK"
    if score <= 3:
        return "MODERATE"
    return "STRONG"


def audit_password(password: str, blocklist: set[str]) -> None:
    """Run the full audit on one password and print a report."""
    score, feedback = score_password(password, blocklist)
    strength = classify_strength(score)

    print("\nPassword strength audit")
    print(f"{'-' * 30}")
    for line in feedback:
        print(f"  {line}")
    print(f"{'-' * 30}")
    print(f"Score: {score}/5  ->  {strength}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Password Strength Auditor")
    parser.add_argument("--password", required=True, help="Password to audit")
    parser.add_argument(
        "--blocklist",
        required=False,
        default=None,
        help="Optional path to a newline-delimited file of extra blocked passwords",
    )
    args = parser.parse_args()

    blocklist = load_blocklist(args.blocklist)
    audit_password(args.password, blocklist)


if __name__ == "__main__":
    main()
