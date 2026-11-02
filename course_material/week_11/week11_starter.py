"""
Week 11 Starter -- XOR Cipher & Key Recovery
Topic 7 (Tier 2: Beginner)

Fill in each function below. Signatures (and docstrings with hints) are
given; the bodies are yours. Don't forget "Plan It First" in the
challenge -- write out your steps and sketch the Mermaid flowchart
before you start writing code here.
"""

import string


def xor_byte(data: bytes, key: int) -> bytes:
    """XOR every byte in `data` against a single-byte key (0-255).

    Because XOR is its own inverse, this same function both encrypts
    and decrypts: xor_byte(xor_byte(data, key), key) == data.

    Raises:
        ValueError: if key is not in range(0, 256).
    """
    raise NotImplementedError


def score_english(data: bytes) -> float:
    """Return a float score estimating how much `data` looks like
    plain English text. Higher = more English-like.

    Hint: a plain "fraction of printable bytes" count is too coarse --
    it can tie across several wrong keys on longer text. Instead, weight
    letters by real English letter frequency (e, t, a, o... are far more
    common than q, z), give a small bonus for spaces, and apply a heavy
    penalty for any non-printable/control byte (see the `string` module
    for `string.printable`). That combination reliably separates "this
    decrypted to English" from "this decrypted to noise."
    """
    raise NotImplementedError


def recover_key(ciphertext: bytes) -> tuple[int, bytes, float]:
    """Try every possible single-byte key (0-255), decrypt the
    ciphertext with each one using xor_byte(), score the result with
    score_english(), and return the (key, decrypted_bytes, score) for
    whichever key produced the best-scoring plaintext.
    """
    raise NotImplementedError


def main():
    """
    Demo:
      1. Pick a secret key and a plaintext message.
      2. Encrypt it with xor_byte().
      3. Pretend you don't know the key -- call recover_key() on just
         the ciphertext.
      4. Print the recovered key and decrypted message, and confirm it
         matches the original plaintext.
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
