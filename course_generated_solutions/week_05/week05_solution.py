"""
Week 5 Solution -- Caesar Cipher Toolkit
Weekly Python Security Challenge (Tier 1: Novice)

Topic: classic shift-cipher encode/decode, plus a brute-force decoder
that recovers the shift automatically via English letter-frequency
scoring.

Builds on L1's argparse-subcommand pattern and habit of splitting a CLI
tool into small, single-purpose functions plus a thin main().
"""

import argparse
from collections import Counter

ALPHABET_SIZE = 26

# Standard relative frequency of each letter in English text (%).
# Used as the reference distribution the brute-force scorer compares
# candidate plaintexts against.
ENGLISH_LETTER_FREQ = {
    "a": 8.2,
    "b": 1.5,
    "c": 2.8,
    "d": 4.3,
    "e": 12.7,
    "f": 2.2,
    "g": 2.0,
    "h": 6.1,
    "i": 7.0,
    "j": 0.15,
    "k": 0.77,
    "l": 4.0,
    "m": 2.4,
    "n": 6.7,
    "o": 7.5,
    "p": 1.9,
    "q": 0.095,
    "r": 6.0,
    "s": 6.3,
    "t": 9.1,
    "u": 2.8,
    "v": 0.98,
    "w": 2.4,
    "x": 0.15,
    "y": 2.0,
    "z": 0.074,
}


def shift_char(ch: str, shift: int) -> str:
    """Shift a single character by `shift` positions in the alphabet.

    Preserves case. Non-alphabetic characters (spaces, punctuation,
    digits) are returned unchanged -- this is the detail a naive first
    attempt tends to skip, and it corrupts anything but pure letter
    strings if you forget it.
    """
    if ch.isupper():
        base = ord("A")
    elif ch.islower():
        base = ord("a")
    else:
        return ch
    offset = (ord(ch) - base + shift) % ALPHABET_SIZE
    return chr(base + offset)


def caesar_shift(text: str, shift: int) -> str:
    """Apply a Caesar shift of `shift` positions to every letter in `text`."""
    return "".join(shift_char(ch, shift) for ch in text)


def encode(text: str, shift: int) -> str:
    """Encode plaintext with a Caesar shift."""
    return caesar_shift(text, shift)


def decode(text: str, shift: int) -> str:
    """Decode ciphertext that was encoded with the given Caesar shift.

    Decoding is just encoding with the shift negated -- there's no
    separate cipher logic to write (and no separate place for a bug
    to hide).
    """
    return caesar_shift(text, -shift)


def score_english(text: str) -> float:
    """Score how 'English-like' a text is, using a chi-squared style
    comparison against expected English letter frequencies.

    A true chi-squared statistic is smallest for a good match (0 would
    be a perfect match). We return the *negated* value so that, at the
    call site, "higher score = more English-like" -- which lets
    brute_force_decode() just pick the max() without having to remember
    which direction is "good" for chi-squared specifically.
    """
    letters_only = [ch.lower() for ch in text if ch.isalpha()]
    n = len(letters_only)
    if n == 0:
        return float("-inf")

    counts = Counter(letters_only)
    chi_squared = 0.0
    for letter, expected_pct in ENGLISH_LETTER_FREQ.items():
        observed = counts.get(letter, 0)
        expected = expected_pct / 100.0 * n
        if expected > 0:
            chi_squared += (observed - expected) ** 2 / expected

    return -chi_squared


def brute_force_decode(ciphertext: str):
    """Try all 26 possible shifts and return the most English-like result.

    Returns (best_shift, best_plaintext, all_candidates), where
    all_candidates is a list of (shift, plaintext, score) tuples sorted
    best-first, so a caller can also inspect the runner-up guesses.
    """
    candidates = []
    for shift in range(ALPHABET_SIZE):
        plaintext = decode(ciphertext, shift)
        score = score_english(plaintext)
        candidates.append((shift, plaintext, score))

    candidates.sort(key=lambda c: c[2], reverse=True)
    best_shift, best_plaintext, _ = candidates[0]
    return best_shift, best_plaintext, candidates


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser with encode / decode / brute-force subcommands."""
    parser = argparse.ArgumentParser(
        description="Caesar cipher toolkit: encode, decode, or crack a shift cipher."
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    encode_parser = subparsers.add_parser("encode", help="Encode text with a shift")
    encode_parser.add_argument("text", help="Text to encode")
    encode_parser.add_argument("shift", type=int, help="Shift amount (any integer)")

    decode_parser = subparsers.add_parser(
        "decode", help="Decode text with a known shift"
    )
    decode_parser.add_argument("text", help="Text to decode")
    decode_parser.add_argument("shift", type=int, help="Shift amount used to encode")

    brute_parser = subparsers.add_parser(
        "brute-force", help="Recover the shift and plaintext without knowing the key"
    )
    brute_parser.add_argument("text", help="Ciphertext to crack")
    brute_parser.add_argument(
        "--show-all",
        action="store_true",
        help="Show all 26 candidate shifts, not just the best guess",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.mode == "encode":
        print(encode(args.text, args.shift))
    elif args.mode == "decode":
        print(decode(args.text, args.shift))
    elif args.mode == "brute-force":
        best_shift, best_plaintext, candidates = brute_force_decode(args.text)
        print(f"Best guess -> shift={best_shift}: {best_plaintext}")
        if args.show_all:
            print("\nAll candidates (best first):")
            for shift, plaintext, score in candidates:
                print(f"  shift={shift:2d}  score={score:8.2f}  {plaintext}")


if __name__ == "__main__":
    main()
