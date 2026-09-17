#!/usr/bin/env python3
"""
Week 5 Starter — Caesar Cipher Toolkit

Fill in the TODO functions below. The CLI plumbing (argparse subcommands) is
already wired up for you, since you built the same pattern in week 1 -- the
new work this week is the cipher logic and the brute-force scoring.

Usage (once implemented):
    python week05_starter.py encode --text "Attack at dawn" --shift 3
    python week05_starter.py decode --text "Dwwdfn dw gdzq" --shift 3
    python week05_starter.py crack --text "Wkh hdjoh kdv odqghg"
"""

import argparse

# A small set of very common English words, useful for scoring how
# "English-like" a candidate decoding is. Feel free to extend this list.
COMMON_WORDS = {
    "the", "and", "is", "to", "of", "a", "in", "that", "it", "for",
    "on", "with", "as", "was", "at", "by", "an", "be", "this", "have",
}


def shift_char(char: str, shift: int) -> str:
    """Shift a single character by `shift` positions in the alphabet.

    Must preserve case. Non-alphabetic characters (spaces, punctuation,
    digits) should be returned unchanged. Shift should wrap around correctly
    for any integer shift, including negative values and values > 26.

    Examples (once implemented):
        shift_char('H', 1)  -> 'I'
        shift_char('z', 1)  -> 'a'
        shift_char('!', 5)  -> '!'
    """
    # TODO: implement
    raise NotImplementedError


def caesar_encode(text: str, shift: int) -> str:
    """Encode `text` by shifting every letter forward by `shift` positions.

    Should build on shift_char() rather than duplicating its logic.
    """
    # TODO: implement
    raise NotImplementedError


def caesar_decode(text: str, shift: int) -> str:
    """Decode `text` that was encoded with `shift`.

    Think about how this relates to caesar_encode() -- can you express
    decoding in terms of encoding with a different shift value, instead of
    writing separate logic?
    """
    # TODO: implement
    raise NotImplementedError


def score_text(text: str) -> float:
    """Return a numeric score estimating how 'English-like' `text` is.

    Higher score = more likely to be real English. One reasonable approach:
    split the text into lowercase words and count how many appear in
    COMMON_WORDS. There's no single "correct" scoring function here -- the
    point is to have *some* reliable way to compare 26 candidates and pick
    the best one. Write down your approach during "Plan It First" before
    implementing it.
    """
    # TODO: implement
    raise NotImplementedError


def brute_force_crack(text: str) -> tuple[int, str]:
    """Try all 26 possible shifts and return the (shift, decoded_text) pair
    that scores highest according to score_text().

    Should be built entirely out of caesar_decode() and score_text() called
    in a loop -- no new cipher logic needed here.
    """
    # TODO: implement
    raise NotImplementedError


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Caesar Cipher Toolkit")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    encode_parser = subparsers.add_parser("encode", help="Encode text with a given shift")
    encode_parser.add_argument("--text", required=True, help="Text to encode")
    encode_parser.add_argument("--shift", required=True, type=int, help="Shift amount")

    decode_parser = subparsers.add_parser("decode", help="Decode text with a given shift")
    decode_parser.add_argument("--text", required=True, help="Text to decode")
    decode_parser.add_argument("--shift", required=True, type=int, help="Shift amount")

    crack_parser = subparsers.add_parser("crack", help="Auto-detect shift and decode")
    crack_parser.add_argument("--text", required=True, help="Ciphertext to crack")

    return parser


def main() -> None:
    args = build_arg_parser().parse_args()

    if args.mode == "encode":
        print(caesar_encode(args.text, args.shift))
    elif args.mode == "decode":
        print(caesar_decode(args.text, args.shift))
    elif args.mode == "crack":
        shift, decoded = brute_force_crack(args.text)
        print(f"Best shift: {shift}")
        print(f"Decoded: {decoded}")


if __name__ == "__main__":
    main()
