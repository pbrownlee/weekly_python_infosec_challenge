# Week 1 Challenge — CLI Security Utils Toolkit

**Tier:** Level-Up Phase (Week 1 of 4)

## Problem Statement

Build a single command-line tool, `sectools.py`, with two subcommands:

1. **`cipher`** — encodes or decodes text using a ROT-N shift cipher, where N is any shift amount (not just the classic ROT13). Letters wrap around the alphabet; case is preserved; non-letter characters (spaces, punctuation, digits) pass through unchanged.
2. **`checkpw`** — checks a password against a small set of strength rules (minimum length, contains a digit, contains an uppercase letter, contains a lowercase letter, contains a symbol) and prints a clear pass/fail report, rule by rule.

Both subcommands live in one program, invoked like `python sectools.py cipher ...` and `python sectools.py checkpw ...`.

## Learning Objectives

- **`argparse` subcommands** — using `argparse.ArgumentParser().add_subparsers()` to build one CLI entry point that branches into multiple independent modes, each with its own arguments.
- **The `re` module for pattern checks** — using `re.search()` with character-class patterns (`\d`, `[A-Z]`, `[a-z]`, a symbol class) instead of hand-rolled loops over characters.
- **Program structure** — splitting a program into small functions with single jobs (transform text, evaluate rules, format output, parse args, dispatch) plus one `main()` that ties them together, instead of one long script.

## On the Job

Security teams write small internal CLI utilities constantly — a quick cipher/encoding tool for CTF-style triage, a password-policy checker wired into an onboarding script, a log-scrubbing tool with a couple of modes. A single script that cleanly supports multiple operations via subcommands, rather than a pile of one-off scripts, is exactly the shape of tool you'd actually keep around and reuse.

## Plan It First

Do this on paper or in a comment block *before* you write any code:

1. Write down, in plain English, what one call to `cipher` needs as input (text, shift amount, encode-or-decode) and what it should print as output.
2. Design the core transform as its own function that takes text and a shift amount and returns new text — decide: should "decode" be a separate function, or just the same function called with a negated shift? Write down your answer and why.
3. Work out the character-shifting math for ONE letter by hand first (see the trace below) before worrying about looping over a whole string.
4. Decide how you'll preserve case and skip non-letters — what check do you run on each character before shifting it?
5. Separately, write down what one call to `checkpw` needs as input (a password string) and what it should print (one line per rule, pass or fail).
6. List the 5 password rules as plain English sentences first, then figure out which one is a length check (easy, no `re` needed) and which ones are pattern checks (need `re.search`).
7. Decide on your function boundaries: something that computes results per input (a dict of rule → True/False, or similar), and something separate that turns those results into printed output. Don't let "compute" and "print" be the same function.
8. Sketch your `argparse` structure last, once you know what data each subcommand needs — this tells you what arguments each subparser requires.

## Worked Trace Example

**Cipher, by hand, for shift = 3, encoding the single character `'H'`:**

| Step | Value |
|---|---|
| Input character | `'H'` |
| Is it a letter? | Yes → shift it |
| Alphabet position (A=0) | `'H'` is position 7 |
| Add shift | `7 + 3 = 10` |
| Wrap with modulo 26 | `10 % 26 = 10` |
| Convert back to letter | position 10 → `'K'` |
| Output character | `'K'` |

Do the same by hand for `'Z'` with shift = 3 — you should land back at the start of the alphabet (`'C'`) once you apply `% 26`. If your code doesn't wrap correctly, this is the case that will catch it.

For the full string `"Hi!"` with shift 3, you should get `"Kl!"` — note `'!'` passes through untouched and the lowercase `'i'` stays lowercase (`'l'`), not uppercase.

**Password check, by hand, for `"pass1"`:**

| Rule | Check | Result |
|---|---|---|
| Length ≥ 8 | `len("pass1")` is 5 | FAIL |
| Has digit | `re.search(r'\d', "pass1")` finds `'1'` | PASS |
| Has uppercase | no `[A-Z]` present | FAIL |
| Has lowercase | `'p'`, `'a'`, etc. present | PASS |
| Has symbol | none present | FAIL |

## Constraints

- Standard library only (`argparse`, `re` — no third-party packages this week).
- The cipher must handle both uppercase and lowercase letters correctly and independently.
- Shift values may be larger than 26 or negative — your modulo math should still produce a correct result (`shift % 26` handles this).
- `checkpw` should never crash on an empty string or a password with unicode characters — just report which rules fail.

## Example Usage

```
$ python sectools.py cipher "Hello, World!" --shift 3
Khoor, Zruog!

$ python sectools.py cipher "Khoor, Zruog!" --shift 3 --decode
Hello, World!

$ python sectools.py checkpw "pass1"
Password strength report:
  [FAIL] Length >= 8 characters
  [PASS] Contains a digit
  [FAIL] Contains an uppercase letter
  [PASS] Contains a lowercase letter
  [FAIL] Contains a symbol
Overall: WEAK (2/5 rules passed)
```

## Hints

<details>
<summary>Hint 1 — stuck on the cipher wrap-around</summary>

Convert the letter to its 0-25 alphabet position with `ord(char) - ord('A')` (or `'a'` for lowercase), do the shift and `% 26`, then convert back with `chr(position + ord('A'))`. Handle uppercase and lowercase as two separate cases so you use the right base letter each time.

</details>

<details>
<summary>Hint 2 — stuck on decode reusing encode</summary>

Decoding with shift N is identical to encoding with shift -N. You don't need a second transform function — just call your one shift function with a negated (or `%26`-normalized negative) shift when `--decode` is passed.

</details>

<details>
<summary>Hint 3 — stuck on argparse subcommands</summary>

`sub = parser.add_subparsers(dest="command", required=True)`, then `cipher_parser = sub.add_parser("cipher")` and add its arguments to `cipher_parser` specifically. In `main()`, branch on `args.command` to decide which function to call.

</details>

## Ethics & Legal Reminder

This week's tool only processes text and password strings you provide directly — there's no scanning or network activity involved, so there's nothing to restrict this week. As a standing rule for this whole program going forward: any exercise involving scanning, sniffing, or intrusion-style behavior must only ever be run against localhost, a sandbox this program provides, or synthetic sample data — never a real, unauthorized, third-party system or network.

## Using AI Tools

Attempt the challenge yourself first. Once you have a first attempt — even a rough or incomplete one — it's fair game to ask an AI tool to review your code for bugs, style, and security issues. If you get completely stuck *before* that, it's fine to ask an AI tool for a hint or a small starting example, but not for a full solution.
