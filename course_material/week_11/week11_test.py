"""
Week 11 tests -- XOR Cipher & Key Recovery

Run with: pytest -q
(CI-safe: everything here is pure in-memory byte manipulation, no
network, no filesystem, no real hosts.)
"""

from week11_starter import xor_byte, score_english, recover_key


def test_xor_byte_matches_hand_trace():
    # From the challenge's worked example: "HI" XORed with key 0x05
    assert xor_byte(b"HI", 0x05) == bytes([0x4D, 0x4C])


def test_xor_byte_is_its_own_inverse():
    key = 0x2A
    original = b"Attack at dawn, the eagle has landed."
    ciphertext = xor_byte(original, key)
    assert ciphertext != original
    assert xor_byte(ciphertext, key) == original


def test_score_english_ranks_real_text_higher_than_noise():
    plain = b"the quick brown fox jumps over the lazy dog"
    noise = bytes([5, 200, 1, 254, 9, 180, 3, 240, 7, 199])
    assert score_english(plain) > score_english(noise)


def test_recover_key_finds_the_right_key():
    key = 0x37
    plaintext = (
        b"Security engineers should always validate their assumptions "
        b"before trusting output."
    )
    ciphertext = xor_byte(plaintext, key)

    recovered_key, recovered_plaintext, _score = recover_key(ciphertext)

    assert recovered_key == key
    assert recovered_plaintext == plaintext


def test_recover_key_handles_a_different_key_and_message():
    key = 0x10
    plaintext = b"short message, still works ok right here"
    ciphertext = xor_byte(plaintext, key)

    recovered_key, recovered_plaintext, _score = recover_key(ciphertext)

    assert recovered_key == key
    assert recovered_plaintext == plaintext
