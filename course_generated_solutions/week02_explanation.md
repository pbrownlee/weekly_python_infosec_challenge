# Week 2 Explanation: Multi-File Hash Auditor

## (a) How you'd get there - the thought process

The challenge description already hands you the three stages ("collect
files," "hash one file," "report results"), so the first real question
isn't "what functions do I need" - it's **"what does each stage pass to
the next one?"** That's the decision that shapes everything else:

- `collect_files()` needs to hand `hash_file()` something it can open.
  That rules out returning plain filename strings if you want to support
  files in subfolders - you'd have to keep rebuilding full paths by hand.
  This is exactly why `pathlib.Path` objects are the right choice over
  strings: a `Path` already knows how to join itself with a directory,
  open itself, and tell you its name.

- `hash_file()` needs to hand `report_results()` something identifiable.
  A hash by itself is useless in a report - you need to know *which
  file* it belongs to. So the natural shape connecting collection to
  reporting is a mapping: `{filepath: hash}`.

That's the "why a dict over an obvious alternative" moment: a first
instinct might be to build a list of hashes in the same order as the
file list, then zip them together later. That works, but it's fragile -
if the two lists ever get out of sync (say you skip a file that raises
a `PermissionError`), you get silently mismatched hash/filename pairs
with no error. Building `{filepath: hash}` as you go means the
association can never come apart.

**Where a naive first attempt snags:** the obvious way to hash a file is
`hashlib.sha256(filepath.read_bytes()).hexdigest()` - one line, reads
great. It's also exactly the kind of thing to catch yourself on: if you
already know (from the docstring guidance and from general practice)
that hashing tools have to handle files that don't comfortably fit in
memory, you should notice that `read_bytes()` loads the *entire* file
before hashing a single byte. The fix is the chunked read-loop pattern -
`for chunk in iter(lambda: f.read(chunk_size), b"")` - which processes
the file incrementally. For the tiny sample files in this challenge
both approaches produce identical hashes, so you wouldn't catch this by
testing output correctness alone; you catch it by asking "would this
still work if the file were 4 GB?" before you call it done.

## (b) Hand-traced example

Suppose the target directory contains two files:

```
samples/
  notes.txt      (contents: b"hello")
  sub/config.txt (contents: b"world")
```

**Step 1 - `collect_files(Path("samples"))`:**
`rglob("*")` walks recursively and returns everything; the `is_file()`
filter drops the `sub` directory itself. Sorted, we get:

```python
[Path("samples/notes.txt"), Path("samples/sub/config.txt")]
```

**Step 2 - `audit_directory` calls `hash_file()` on each:**

For `samples/notes.txt`:
- `sha256 = hashlib.sha256()` -> empty hasher
- loop reads one chunk: `b"hello"` (smaller than 8192, so it's the only
  chunk) -> `sha256.update(b"hello")`
- next `f.read()` returns `b""` -> loop stops
- `sha256.hexdigest()` -> `"2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"`
  (the well-known SHA-256 of "hello")

Same process for `sub/config.txt` with `b"world"`, producing the
SHA-256 of "world".

After the dict comprehension, `results` looks like:

```python
{
    Path("samples/notes.txt"):     "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
    Path("samples/sub/config.txt"): "<sha256 of world>",
}
```

**Step 3 - `report_results()`** iterates that dict and prints each
`digest  relative/path` pair, then a total count of `2`.

## (c) Key new library/pattern, and common mistakes

**New skills this week:** `pathlib.Path` for filesystem traversal
(`rglob`, `is_file`, `relative_to`, `open`) and `hashlib` for computing
digests, plus the habit of structuring a small tool as
collect -> process-one -> report instead of one long function.

**Common mistakes to avoid:**
- Hashing with `read_bytes()` on large files (loads everything into
  memory at once - see the trace above).
- Forgetting `sorted()` on the file list - directory iteration order is
  not guaranteed, which makes output (and any tests comparing it)
  non-deterministic.
- Using `os.walk` and hand-joining path strings with `+` or `os.path.join`
  everywhere - `pathlib` does this more safely and readably.
- Mixing up `Path.name` (just the filename) with the full path when
  building the report - you want `relative_to(directory)` here so the
  report reads cleanly regardless of how deep a file is nested.
