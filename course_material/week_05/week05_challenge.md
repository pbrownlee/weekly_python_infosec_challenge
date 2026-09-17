# Week 5 Challenge — Caesar Cipher Toolkit

**Tier 1: Novice — Topic 1 of 3**

Welcome to Tier 1. The level-up phase is done — from here on, challenges are
scoped like small real tools rather than syntax drills, and (starting this
week) they run through the same CI pipeline a professional project would use.

## Problem Statement

Build a small toolkit for the classic Caesar (shift) cipher. Your script
should be able to:

1. **Encode** a message with a given shift (0-25).
2. **Decode** a message with a given shift.
3. **Crack** a Caesar-encoded message with an *unknown* shift, by trying all
   26 possible shifts and automatically picking the one that produces the
   most English-like result.

This is a direct extension of week 1's CLI toolkit — same `argparse`
subcommand structure, new cipher logic.

## Learning Objectives

- Reuse and extend an `argparse` subcommand CLI structure from a previous week.
- Practice modular arithmetic (`% 26`) for wraparound in a shift cipher.
- Design a simple scoring heuristic and use it to pick the "best" result out
  of many candidates — a small taste of the same idea behind more advanced
  cryptanalysis you'll touch again in the XOR key-recovery challenge later
  in the series.
- Keep a growing CLI tool organized as more subcommands are added.

## On the Job

Frequency-based cryptanalysis and "try every key, score the plaintext"
brute-forcing are real techniques you'll encounter in CTFs, in analyzing
poorly-encoded malware config strings, and in legacy systems that still use
weak, historical ciphers. The specific cipher here is toy-grade, but the
*pattern* — generate all candidates, score each one automatically, return the
best — shows up constantly in security tooling.

## Plan It First

Before writing any code:

1. In plain text, write down the subcommands your CLI will need (`encode`,
   `decode`, `crack`) and what arguments each one takes.
2. Sketch a quick **Mermaid flowchart** (`flowchart TD` or `flowchart LR` —
   plain text, no diagramming tool required) of your planned function calls
   and control flow before you write any code. Use the Mermaid syntax primer
   from week 3 if you need a refresher on node/arrow syntax. Include this
   diagram alongside your solution when you share it in the challenge thread
   — it'll get compared against what you actually built during review.
3. Specifically think through: how does `crack` decide which of the 26
   candidate decodings is "best"? Write your scoring idea down in one or two
   sentences before coding it.

## Tiny Worked Trace Example

Encoding `"HAL"` with shift `1`:

| Step | Value |
|---|---|
| `'H'` → position 7 (0-indexed from `'A'`) | `(7 + 1) % 26 = 8` → `'I'` |
| `'A'` → position 0 | `(0 + 1) % 26 = 1` → `'B'` |
| `'L'` → position 11 | `(11 + 1) % 26 = 12` → `'M'` |

Result: `"IBM"`. (Yes, this is the famous joke — HAL 9000, shifted by one,
becomes IBM.) Decoding `"IBM"` with shift `1` should reverse this and return
`"HAL"`.

## Constraints

- Preserve case: `'h'` shifted stays lowercase, `'H'` stays uppercase.
- Leave non-alphabetic characters (spaces, punctuation, digits) unchanged —
  don't try to shift them.
- Shift values should wrap around correctly for any integer, including
  negative shifts and shifts greater than 26 (e.g., a shift of `27` should
  behave identically to a shift of `1`).
- `crack` must not take a shift argument from the user — it has to determine
  it automatically.

## Example Usage

```
$ python week05_starter.py encode --text "Attack at dawn" --shift 3
Dwwdfn dw gdzq

$ python week05_starter.py decode --text "Dwwdfn dw gdzq" --shift 3
Attack at dawn

$ python week05_starter.py crack --text "Wkh hdjoh kdv odqghg"
Best shift: 3
Decoded: The eagle has landed
```

## Hints (graduated — try to solve it before reading further)

1. **Hint 1:** For a single character, converting to a 0-25 index is
   `ord(char) - ord('A')` for uppercase (or `ord('a')` for lowercase). Convert
   back with `chr(index + ord('A'))`. Handle upper and lower case in the same
   function rather than writing two near-duplicate functions.
2. **Hint 2:** For `crack`, one simple scoring approach: count how many
   characters in a candidate decoding are common English letters (e/t/a/o/i/n
   are the most frequent in English text) or check how many *words* in the
   candidate appear in a small built-in list of common English words (`the`,
   `and`, `is`, `to`, ...). Higher score wins.
3. **Hint 3:** `crack` can be built entirely out of `caesar_decode`, called 26
   times in a loop with shifts `0` through `25` — you don't need any new
   cipher logic, only a scoring function and a loop that tracks the
   best-scoring candidate seen so far.

## Ethics & Legal Reminder

Everything here runs on strings you provide locally — there's no scanning,
no network activity, and nothing that touches systems you don't own. As
always in this series: any technique you practice here should only ever be
applied against systems and data you're authorized to test.

## Using AI Tools

You're welcome to use AI tools (including Claude) to help you learn, debug,
or understand concepts as you work through this challenge. The goal is for
*you* to understand and be able to explain every line you submit — treat AI
help the way you'd treat a textbook or Stack Overflow, not a substitute for
doing the thinking yourself.

## Portfolio Note

A working encode/decode/crack toolkit with a clean CLI is a nice small
addition to a portfolio repo — it demonstrates modular arithmetic, CLI
design, and a simple heuristic-scoring approach in under 100 lines.
