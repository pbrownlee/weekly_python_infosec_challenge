# Week 1 Explanation — CLI Security Utils Toolkit

## (a) How you'd get there — the thought process

**First question to ask:** "What are the truly separate pieces of work here, and where does each one begin and end?" This challenge bundles two unrelated features (a cipher and a password checker) behind one CLI. The temptation when a program has two modes is to write one long `if/else` block with all the logic inline. Resist that — the first decomposition question is always "what are the *nouns* (the data) and what are the *verbs* (the operations on that data)?" Here the nouns are "a piece of text with a shift" and "a password," and the verbs are "shift it" and "check it." That maps cleanly onto two independent functions (`rot_n_shift`, `check_password`) that don't know or care about argparse at all — they just take plain values in and return plain values out. That separation is what makes each one independently testable and traceable.

**Why argparse subparsers over a single `--mode` flag?** A single `--mode cipher|checkpw` flag works, but then every subsequent `--shift`, `--text`, `--password` argument is "required only sometimes," which argparse can't express cleanly and which produces confusing help text. Subparsers (`add_subparsers`) let each subcommand own its own arguments and its own `--help`, which is exactly how real CLI tools like `git` or `aws` are structured. Choosing subparsers here isn't just style — it's a preview of the "new external service" CLIs later in the series (topic 11's boto3 tool, for instance) which will also read as a dispatch table of subcommands.

**Where a naive first attempt snags — the cipher:** The obvious first attempt at ROT-N is `chr(ord(ch) + shift)`. Try it by hand on `'z'` with `shift=3`: `ord('z')` is 122, `+3` is 125, and `chr(125)` is `'}'` — not a letter at all. The bug only shows up at the *edges* of the alphabet, which is exactly the kind of thing that passes a quick eyeball test on "abc" and then breaks in front of Paul later on "xyz." The fix is to re-base to 0 before shifting (`ord(ch) - base`), apply `% 26` to wrap around, and only then add the base back. This is a good moment to build the habit of asking "what's the smallest input that would expose an off-by-the-edges bug?" before calling something done.

**Where a naive first attempt snags — decode:** The tempting-but-wrong approach is to write a second, separate "un-shift" function with its own loop. That's needless duplication, and duplication is where bugs creep in when one copy gets fixed and the other doesn't. The cleaner realization: decoding by `shift` is identical to encoding by `-shift`. That only works, though, if you trust Python's modulo to behave with negative numbers — worth explicitly checking rather than assuming, since some other languages (C, Java) would hand you a negative remainder here and silently produce wrong output. Python's `%` always returns a result with the same sign as the divisor, so `-3 % 26 == 23`, and the wraparound "just works."

**Where a naive first attempt snags — password rules:** A common first cut only checks length, because length is the first thing that comes to mind. The prompt says "character-class variety," which means going back to re-read the requirement and translating each rule into its own `re.search` check, one rule per line, rather than trying to cram everything into one giant regex. Cramming it into one regex would technically work but would produce a single pass/fail with no way to tell the user *which* rule failed — and a password checker that can't say why it failed isn't very useful. Building a list of failure messages (rather than a single `True`/`False`) is what makes the tool actually helpful to whoever runs it.

## (b) Hand-traced example

**Cipher, encoding `"Hi!"` with `shift=3`:**

| step | ch | is alpha? | base | ord(ch)-base | +shift, %26 | output char | result_chars so far |
|---|---|---|---|---|---|---|---|
| 1 | `H` | yes | `ord('A')=65` | `72-65=7` | `(7+3)%26=10` | `chr(65+10)='K'` | `['K']` |
| 2 | `i` | yes | `ord('a')=97` | `105-97=8` | `(8+3)%26=11` | `chr(97+11)='l'` | `['K','l']` |
| 3 | `!` | no | — | — | — | `'!'` unchanged | `['K','l','!']` |

`"".join(...)` → `"Kl!"`.

**Decoding `"Kl!"` with `shift=3`** calls `rot_n_shift("Kl!", -3)`:

| step | ch | ord(ch)-base | `+(-3), %26` | output char |
|---|---|---|---|---|
| 1 | `K` | `75-65=10` | `(10-3)%26=7` | `chr(65+7)='H'` |
| 2 | `l` | `108-97=11` | `(11-3)%26=8` | `chr(97+8)='i'` |
| 3 | `!` | — | — | `'!'` |

Result: `"Hi!"` — round-trips correctly, including the punctuation pass-through.

**Password check on `"abc123"`:**

`check_password("abc123")` builds `failures = []` and evaluates each rule in order:

1. `len("abc123") = 6 < 8` → append `"Must be at least 8 characters long."`
2. `re.search(r"[A-Z]", "abc123")` → `None` → append the uppercase message.
3. `re.search(r"[a-z]", "abc123")` → matches `'a'` → no failure.
4. `re.search(r"[0-9]", "abc123")` → matches `'1'` → no failure.
5. `re.search(r"[!@#...]", "abc123")` → `None` → append the special-character message.
6. `"abc123".lower() in COMMON_PASSWORD_BLOCKLIST` → `False` → no failure.

Final `failures` list has 3 entries, so `run_checkpw` prints `FAIL:` followed by those three bullet lines — matching the actual run above.

## (c) Key new library/pattern, and common mistakes to avoid

**argparse subparsers**: `parser.add_subparsers(dest="command", required=True)` creates a namespace where `args.command` tells you which subcommand was invoked. Each subparser (`add_parser(...)`) gets its own arguments and its own auto-generated `--help`. Attaching `set_defaults(func=run_cipher)` to each subparser is a clean dispatch trick: `main()` just calls `args.func(args)` instead of writing its own `if args.command == "cipher": ...` chain. Common mistake: forgetting `required=True` on `add_subparsers` — on older Python versions this lets the program run with *no* subcommand at all and then crash later with a confusing `AttributeError` instead of a clean usage error.

**`re` module**: `re.search` finds a match *anywhere* in the string, while `re.match` only anchors at the *start* — a very common source of "why didn't my check work" bugs when someone reaches for `match` out of habit and the character they're checking for isn't the very first one. Character classes like `[A-Z]` are cheap, readable ways to ask "does at least one of these exist" — resist the urge to write one enormous regex that tries to enforce everything at once; separate `re.search` calls per rule are more readable and, critically, let you report *which* rule failed.

**General structuring habit**: keeping `rot_n_shift` and `check_password` free of any `print()` calls or argparse knowledge means you could unit-test them directly with plain function calls and assertions, with no CLI involved at all — a preview of the pytest habit that week 3 introduces on purpose.

*(No Mermaid flowchart section this week — that habit phases in starting with week 3's solution, once "Plan It First" itself starts asking for one.)*
