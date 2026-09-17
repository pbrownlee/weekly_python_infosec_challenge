"""
Week 5 Tests — Caesar Cipher Toolkit

Run with: pytest -v week05_test.py

These tests exercise the function signatures in week05_starter.py. They will
fail with NotImplementedError until you fill in the TODOs -- that's expected.
Implement each function, then re-run pytest to watch them pass.
"""

import pytest
from week05_finished import (
    brute_force_crack,
    caesar_decode,
    caesar_encode,
    score_text,
    shift_char,
)


def test_shift_char_basic_uppercase():
    assert shift_char("H", 1) == "I"


def test_shift_char_wraps_lowercase():
    assert shift_char("z", 1) == "a"


def test_shift_char_preserves_non_alpha():
    assert shift_char("!", 5) == "!"
    assert shift_char(" ", 5) == " "


def test_shift_char_handles_shift_over_26():
    # A shift of 27 should behave exactly like a shift of 1.
    assert shift_char("A", 27) == shift_char("A", 1)


def test_caesar_encode_preserves_case_and_punctuation():
    assert caesar_encode("Attack at dawn!", 3) == "Dwwdfn dw gdzq!"


def test_caesar_decode_reverses_encode():
    original = "The Eagle Has Landed"
    for shift in [0, 1, 3, 13, 25]:
        encoded = caesar_encode(original, shift)
        assert caesar_decode(encoded, shift) == original


@pytest.mark.parametrize("shift", [0, 1, 5, 13, 25])
def test_encode_decode_round_trip_various_shifts(shift):
    original = "Meet me at midnight"
    assert caesar_decode(caesar_encode(original, shift), shift) == original


def test_score_text_prefers_real_english():
    high_score_text = "the quick fox is in the box"
    low_score_text = "xqe qzikc rud aj ah xqe wnl"
    assert score_text(high_score_text) > score_text(low_score_text)


def test_brute_force_crack_recovers_shift_and_text():
    original = "the eagle has landed"
    encoded = caesar_encode(original, 3)
    shift, decoded = brute_force_crack(encoded)
    assert shift == 3
    assert decoded == original
