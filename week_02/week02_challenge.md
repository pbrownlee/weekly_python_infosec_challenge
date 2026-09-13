# Week 2 — Multi-File Hash Auditor

**Tier:** 0 — Level-Up Phase (week 2 of 4)

## Problem Statement

Build a small command-line tool that walks a directory of files, computes the
SHA-256 hash of each one, and prints a clean report of filename → hash. This
is the "file integrity" building block that a lot of real security tooling
is built on top of — you'll extend it into a full baseline/verify integrity
checker in Tier 1 (Novice), so it's worth structuring cleanly now.

## Learning Objectives

- Use `pathlib.Path` to walk a directory tree and work with file paths in a
  modern, cross-platform way (instead of raw string concatenation).
- Use `hashlib` to compute a SHA-256 digest of a file's contents, reading it
  safely in chunks rather than loading the whole file into memory at once.
- Practice structuring a program around a clear three-stage shape: *collect
  files* → *hash one file* → *report results* — each stage its own function.

## On the Job

Verifying that files haven't been tampered with — a config file, a binary,
a log archive — by comparing hashes against a known-good baseline is a
routine security engineering task: malware persistence checks, verifying
downloaded artifacts, confirming a "gold image" hasn't drifted, or proving
a piece of evidence wasn't altered during an investigation. The three-stage
shape you'll build here (collect → hash → report) is the same shape you'll
reuse and extend in a few weeks for a real baseline/verify integrity tool.

## Plan It First

Before writing any code, answer these in a few sentences or bullet points
(plain text is fine — the Mermaid flowchart habit starts next week, once
there's a bit more control flow worth diagramming):

- What does "walking a directory" actually need to handle? Files directly
  inside the folder, sure — but what about subfolders? What about a path
  that turns out to be a directory, not a file?
- What's the one piece of information you need out of hashing a single
  file, and what's the one piece of information you need out of the
  directory walk? Keeping those two concerns in separate functions is the
  point of this exercise.
- What should happen if a file can't be read (permissions, a broken
  symlink)? Should the whole program crash, or should that one file be
  skipped with a message?

## Worked Trace Example

Say a folder `samples/` contains two files:

```
samples/
  notes.txt      (contents: "hello")
  report.csv     (contents: "a,b,c")
```

Walking the directory should produce a list of two `Path` objects. Hashing
`notes.txt` means reading its bytes (`b"hello"`), feeding them into a
`hashlib.sha256()` object, and calling `.hexdigest()` — for the exact bytes
`b"hello"` this always produces the same fixed 64-character hex string,
which you can verify against `echo -n "hello" | sha256sum` at a terminal.
The report stage takes the `{filename: hash}` pairs collected from both
files and prints them in a consistent, readable format, e.g.:

```
notes.txt   2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
report.csv  <hash for "a,b,c">
```

## Constraints

- Use `pathlib` for all path handling — no raw string path concatenation
  (`+` or manual `/` joining) or `os.path`.
- Use `hashlib.sha256()`, reading the file in fixed-size chunks (e.g. 8192
  bytes at a time) in a loop rather than calling `.read()` with no
  argument. This matters for real security tools, which often hash files
  far larger than available memory.
- The tool should accept a directory path as a command-line argument
  (`argparse` again, like last week — just a single positional argument
  is enough this time).
- Handle the case of an empty directory and a directory containing
  subfolders without crashing.

## Sample Data

No special data generator needed this week — just create a small test
folder yourself, e.g.:

```
mkdir -p sample_files
echo "hello" > sample_files/notes.txt
echo "a,b,c" > sample_files/report.csv
mkdir sample_files/subdir
echo "nested" > sample_files/subdir/nested.txt
```

Then run your tool against `sample_files/`.

## Example Usage / Expected Output

```
$ python week02_starter.py sample_files
notes.txt              2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
report.csv             <hash>
subdir/nested.txt      <hash>

3 file(s) hashed.
```

(Exact formatting is up to you — the important part is a clear, readable
mapping from file path to hash, including files found in subfolders.)

## Hints (graduated — try not to peek until you're stuck)

1. `Path(directory).rglob("*")` walks a directory recursively and yields
   both files and subdirectories — you'll need to filter to just the
   files (`.is_file()`).
2. Opening a file in binary mode (`"rb"`) matters — hashing needs raw
   bytes, not a decoded text string, and some files (anything non-text)
   would fail to decode as text anyway.
3. A `hashlib.sha256()` object has an `.update(chunk)` method you can call
   repeatedly as you read chunks in a loop, then `.hexdigest()` once at
   the end to get the final result — you don't need to read the whole
   file into one variable first.

## Ethics & Legal Reminder

Only run this tool against files you own or have explicit permission to
inspect — your own test folder, sample files you created, or files your
employer has authorized you to audit. Never point a hashing/scanning tool
at systems, shares, or files that aren't yours without authorization, even
just to "see what happens."

## Using AI Tools

You're welcome to use AI assistants (including Claude) to help you
understand a concept, look up a standard-library function, or debug an
error message. But write the actual solution code yourself — the goal of
this series is to build the muscle of solving these problems, not to end
up with AI-generated code you couldn't explain or defend in a code review.
