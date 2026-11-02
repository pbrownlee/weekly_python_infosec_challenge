# Week 11 Challenge -- XOR Cipher & Key Recovery

**Tier 2: Beginner** (final challenge of this tier)

## Problem Statement

Single-byte XOR is one of the simplest ciphers there is -- and it's still
genuinely common in the wild, usually as a lightweight obfuscation layer
in malware configs, dropped payloads, or home-grown "encryption" that
someone mistook for real security. Your job this week:

1. Write a function that XOR-encrypts (and, because XOR is symmetric,
   also decrypts) a byte string against a single-byte key.
2. Write a scoring function that estimates how "English-like" a chunk of
   decrypted bytes looks.
3. Write a key-recovery function that, given *only* the ciphertext (no
   key), tries all 256 possible single-byte keys, scores each resulting
   plaintext guess, and returns the best one.

## Learning Objectives

- Bitwise XOR (`^`) on bytes, and why XOR is its own inverse.
- Basic frequency-analysis-style scoring of text.
- Brute-forcing a small keyspace (256 values is nothing -- this is a
  gentle, bounded introduction to the idea of brute-force cryptanalysis
  you'll see in harsher forms later).
- Working with Python `bytes` objects directly, not just `str`.

## On the Job

You'll run into single-byte (and, later, multi-byte repeating-key) XOR
constantly in malware analysis and CTF-style exercises: it's the
"someone wanted *some* obfuscation but didn't want to deal with real
crypto" cipher. Being able to recognize XOR'd data and recover the key
without being handed it is a small, concrete, genuinely useful skill --
and it's a good warm-up for the cryptographic reasoning you'll need more
of as the series gets harder.

## Plan It First

Before writing any code:

1. In plain English (or a numbered list), write out the steps
   `recover_key()` needs to take, in order. Be specific about what
   "try every key" actually means as a loop, and what you do with each
   attempt's result.
2. Sketch a quick Mermaid flowchart (`flowchart TD` or `flowchart LR` is
   enough -- plain text, no diagramming tool required) of the planned
   function calls and control flow, the same way you did starting in
   Week 3. If you need a refresher on the syntax, see "the Mermaid syntax
   primer from Week 3." Preview it by pasting into mermaid.live, or by
   dropping it in a ` ```mermaid ` fenced code block in a `.md` file --
   GitHub and VS Code's Markdown Preview both render it natively.
3. Include that diagram alongside your solution when you share it -- it
   gets compared against what you actually built during review.

## Tiny Worked Trace Example

XOR each byte of the plaintext against the key byte. Using the ASCII
values for `"HI"` and key `0x05`:

```
'H' = 0x48 = 01001000
key = 0x05 = 00000101
XOR         = 01001101 = 0x4D

'I' = 0x49 = 01001001
key = 0x05 = 00000101
XOR         = 01001100 = 0x4C
```

So `xor_byte(b"HI", 0x05)` should return `bytes([0x4D, 0x4C])`. Running
the *same* function again on that result with the *same* key gets you
back `b"HI"` -- that's the "XOR is its own inverse" property in action.

## Constraints

- Work on raw `bytes`, not `str` -- text should be encoded to bytes
  before encrypting (`"hello".encode()`) and the recovered plaintext
  will also be `bytes`.
- `recover_key()` must try the full keyspace (0-255) -- no shortcuts
  like assuming the key is a printable character.
- Only use the synthetic/sample text provided in this challenge (or your
  own made-up test sentences). Don't point this at anything you don't
  have the right to inspect -- see the ethics note below.

## Example Usage / Expected Output

```python
>>> from week11_starter import xor_byte, recover_key
>>> secret_key = 0x37
>>> plaintext = b"Security engineers should always validate their assumptions."
>>> ciphertext = xor_byte(plaintext, secret_key)
>>> ciphertext[:8]
b'\x1aO[[4FX['   # exact bytes will vary by key -- illustrative only

>>> recovered_key, recovered_plaintext, score = recover_key(ciphertext)
>>> recovered_key
55
>>> recovered_plaintext
b'Security engineers should always validate their assumptions.'
```

## Hints (graduated)

1. **Hint 1:** `xor_byte` can be written as a one-liner using a
   `bytes([... for b in data])` comprehension and the `^` operator on
   each byte against the key.
2. **Hint 2:** For `score_english`, you don't need real NLP, but a plain
   "what fraction of bytes are printable" count turns out to be too
   coarse -- it can tie across several wrong keys on longer text. Instead,
   weight letters by real English letter frequency (e.g. `e` and `t` are
   far more common than `q` or `z` -- a quick web search for "English
   letter frequency table" gives you the numbers), give a small bonus for
   spaces, and apply a heavy *penalty* for non-printable/control bytes.
   That combination reliably separates "this decrypted to English" from
   "this decrypted to noise," even when a wrong key happens to produce a
   few letters by chance.
3. **Hint 3:** `recover_key` is just: loop `key` from 0 to 255, call
   `xor_byte(ciphertext, key)`, score the result, and keep track of
   whichever `(key, result, score)` had the highest score seen so far.

## Ethics & Legal Reminder

Only run this against the sample/synthetic text you write yourself for
this exercise. Recovering a key and decrypting data you don't have
authorization to inspect -- even trivially "encrypted" data -- can cross
real legal lines outside a sandboxed learning exercise like this one.

## Using AI Tools

Feel free to use an AI assistant (including Claude) to look up unfamiliar
standard-library behavior or to explain an error message you don't
understand. But write your own decomposition and your own first-pass
implementation before asking an AI to review or improve it -- the goal
this week is you building the logic yourself, not an AI building it for
you.

## Portfolio Note

A small, self-contained "recover an unknown single-byte XOR key by
frequency analysis" script is a nice thing to describe in an interview or
write up as a short blog post -- it's a concrete, correct answer to "have
you done any hands-on cryptanalysis work?"
