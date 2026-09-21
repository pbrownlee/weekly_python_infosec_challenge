# Week 6 Challenge -- Password Strength Auditor

**Tier:** 1 -- Novice
**Builds on:** L1 (argparse + the `re` module)

## Problem statement

Write a small CLI tool that audits a password against a set of basic
strength rules and gives clear, specific pass/fail feedback -- not just
"weak" or "strong," but *which* rules it failed and why. Specifically,
check:

1. **Minimum length** (configurable, default 12 characters).
2. **Character-class variety** -- at least one lowercase letter, one
   uppercase letter, one digit, and one special (non-alphanumeric)
   character.
3. **Blocklist membership** -- reject passwords that appear (case-
   insensitively) in a small list of common weak passwords.

The tool should report overall pass/fail plus a per-rule breakdown.

## Learning objectives

- Reinforce the `re` module for pattern matching (from L1), this time
  applied to several related checks instead of one.
- Practice structuring a set of independent "rule check" functions that
  each return a consistent result shape, then aggregating those results
  into a single report -- a very common pattern for any kind of
  validation or compliance tool.
- Deliberately practice avoiding the mutable-default-argument pitfall
  (see the Week 3 "Fix the Bugs" challenge) in a function that takes an
  optional blocklist.

## On the job

Security engineers write exactly this kind of tool constantly: password
policy checkers for compliance audits, pre-commit hooks that reject weak
secrets, onboarding flows that give users real-time feedback instead of a
bare "invalid password" -- the shape (a handful of independent rule
checks, aggregated into one report) generalizes far beyond passwords.

## Plan It First

Before writing any code:

1. In plain text (or bullet points), write down the order you'll tackle
   this in and how the pieces fit together. What does each check
   function need as input, and what should it hand back? What does the
   *aggregation* step need to look like in order for the final report to
   be easy to print?
2. Sketch a quick Mermaid flowchart (`flowchart TD` or `flowchart LR` is
   fine, plain text, no tool required) of the planned function calls and
   control flow -- see the Mermaid syntax primer from Week 3 if you need
   a refresher on the node/arrow syntax. Include this diagram alongside
   your solution when you share it in the challenge thread; it'll get
   compared against what you actually built during review.

## Tiny worked trace example

Given the password `"password"` with default settings, you'd expect a
report roughly like:

```
Password audit: FAIL
  [FAIL] length: too short? no, actually 8 < 12 -> FAIL (too short: 8 chars, minimum 12)
  [FAIL] character_variety: missing uppercase, digit, special character
  [FAIL] blocklist: "password" is a commonly used weak password
```

Given `"Tr0ub4dor&3xtra!"`:

```
Password audit: PASS
  [PASS] length: OK (16 chars)
  [PASS] character_variety: OK
  [PASS] blocklist: not found in blocklist
```

(Exact wording is up to you -- the important part is that every failing
rule says *why* it failed.)

## Constraints

- Handle an empty-string password gracefully (it should fail every
  relevant check, not crash).
- Blocklist comparison must be case-insensitive.
- No need to hit a real breached-password API (like Have I Been Pwned) --
  a small local/hardcoded list is the point of this exercise.
- Don't log or write the plaintext password to disk anywhere; treat it as
  sensitive for the lifetime of the program only.

## Example usage

```
$ python week06_starter.py --password "Summer2023!"
Password audit: FAIL
  [FAIL] length: too short: 11 chars (minimum 12)
  [PASS] character_variety: OK
  [PASS] blocklist: not found in blocklist
```

(Exact formatting is up to you -- run it yourself once implemented to see
the output shape you chose.)

## Hints (graduated -- try not to skip ahead)

1. Start with `check_length()` alone. Get it returning a `(passed, message)`
   tuple and test it against an obviously-too-short and an obviously-long-
   enough password before touching anything else.
2. For `check_character_variety()`, use `re.search()` with patterns like
   `[a-z]`, `[A-Z]`, `[0-9]`, and `[^A-Za-z0-9]` for "special character."
   Consider looping over a list of `(pattern, description)` pairs instead
   of writing four nearly-identical `if` blocks.
3. Before writing `calculate_strength_score()`, write down the exact shape
   of the dict it will return (what keys, what each value looks like).
   Do this on paper/in a comment first -- `format_report()` depends on
   that shape being stable, and deciding it up front avoids reshaping it
   twice.

## Ethics & legal reminder

Only test this tool against passwords you own, passwords you've made up
for testing, or ones you have explicit permission to evaluate. Never run
it against a real user's live credentials or a production authentication
system without proper authorization -- and even in this sandboxed
exercise, treat plaintext passwords as sensitive: don't log them, print
them to a shared terminal, or write them to a file.

## Using AI tools

It's fine to use AI assistants (including Claude) to help you understand
a concept or debug an error message. The goal of this series is your own
skill growth, though, so make sure you understand and could explain every
line you submit -- not just that it runs.

## Portfolio note

A password-policy auditor is a completely reasonable small artifact to
show in a portfolio or talk through in an interview -- frame it as a
compliance/security utility, and be ready to explain the specific rules
you chose and why.
