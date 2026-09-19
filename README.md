# Weekly Python Security Challenge

A 20-week, self-paced curriculum for building practical Python skills as a working security engineer — one challenge a week, delivered on a fixed schedule, ramping from fundamentals through advanced security scripting.

## Why this exists

The goal isn't re-learning Python syntax — it's bridging from "I know the fundamentals" to "I can build a complete, structured program I'd be comfortable pointing to as evidence of skill." Concretely, that means deliberate practice at:

- **Problem decomposition** — planning a program's structure *before* writing code, instead of losing track of logic paths halfway through.
- **Combining pieces into one cohesive tool** — most weeks stack a few standard-library modules together into something that reads like a real internal tool, not a toy script.
- **Standard-library and third-party literacy** — `argparse`, `pathlib`, `hashlib`, `re`, `logging`, `csv`/`json`, `socket`, `requests`, `boto3`, and others, introduced as they're needed rather than all at once.
- **Testing as a habit** — pytest is taught hands-on in week 3, then becomes a required part of every week from week 5 onward via CI.

Every week (1-19) follows the same "Plan It First" discipline: write one sentence per function before touching code, and — from week 3 onward — sketch a quick Mermaid flowchart of the planned control flow before writing any. The point is catching design problems on paper instead of mid-refactor.

## How a week works

Each `course_material/week_NN/` folder (zero-padded, e.g. `week_04`) holds that week's challenge materials as delivered:

- `weekNN_challenge.md` — the brief: problem statement, learning objectives, "Plan It First" planning steps, a worked trace example, constraints, expected output, and graduated hints.
- `weekNN_starter.py` — the starting point to build from. Scaffolding fades as the tiers advance: fully decomposed functions in the early weeks, down to just the entry point/CLI shape by the advanced tier.
- `weekNN_test.py` — pytest tests (a couple of pre-written ones in week 3 to learn from; from week 5 on, a full CI-safe suite exercising the week's functions).
- Any sample data the week needs (e.g. `sample_logs/`).
- Starting week 5: `requirements.txt` and `.github/workflows/ci.yml`, so every push runs pytest plus a `bandit` security scan, both scoped to `user_created_solutions/` — my own code, not the starter scaffolding or reference solutions.

## Where the actual solutions live

Two top-level folders separate the reference material from personal work, so it's always clear which is which:

- **`course_generated_solutions/`** — the reference solution and reasoning walkthrough generated for each week, one `week_NN/` subfolder per week (`week_NN/weekNN_solution.py` + `week_NN/weekNN_explanation.md`). These arrive one week behind — the solution for week *N* is delivered alongside week *N+1*'s challenge — so review happens after a real attempt, not before.
- **`user_created_solutions/`** — my own finished code for each week, one `week_NN/` subfolder per week (`week_NN/weekNN_finished.py`), plus whatever else I wrote myself while working through it: my pytest tests (`weekNN_test.py`), my Mermaid planning charts (`weekNN_chart.md`), and any planning notes (e.g. `weekNN_logic.txt`). This is the "did I actually solve it" record, kept separate from both the starter code and the reference answer.

## Curriculum map

**Tier 0 — Level-Up Phase (weeks 1-4).** Not new syntax — practical structure, standard-library reps, and (week 3 specifically) a hands-on introduction to pytest.

| Week | Challenge | New skills |
|---|---|---|
| 1 | CLI Security Utils Toolkit | `argparse` subcommands, `re`, program structure |
| 2 | Multi-File Hash Auditor | `pathlib`, `hashlib`, multi-function structuring |
| 3 | Fix the Bugs (and Prove It with pytest) | tracebacks, systematic debugging, `logging`, pytest fundamentals, Mermaid flowcharts |
| 4 | Capstone: Mini Log Auditor CLI | combining weeks 1-3, `collections.Counter` |

**Tier 1 — Novice (weeks 5-7).** CI/CD (pytest + bandit via GitHub Actions) begins here.

| Week | Challenge |
|---|---|
| 5 | Caesar Cipher Toolkit |
| 6 | Password Strength Auditor |
| 7 | File Integrity Checker |

**Tier 2 — Beginner (weeks 8-11).**

| Week | Challenge |
|---|---|
| 8 | Local Port Scanner |
| 9 | Brute-Force Log Analyzer |
| 10 | IOC Feed ETL Pipeline — built around the actual read → filter → transform → write pattern of daily security-engineering work |
| 11 | XOR Cipher & Key Recovery |

**Tier 3 — Intermediate (weeks 12-15).**

| Week | Challenge |
|---|---|
| 12 | HTTP Security Header Auditor |
| 13 | Simple Network Traffic Analyzer |
| 14 | File System Integrity Monitor |
| 15 | Cloud Security Posture Auditor — `boto3` against a real (free-tier, read-only) AWS account |

**Tier 4 — Advanced (weeks 16-19).** The final tier — difficulty ramps to the hardest, most custom-logic-heavy builds of the series.

| Week | Challenge |
|---|---|
| 16 | AI-Assisted Alert Triage Tool — calling a real LLM API and safely parsing structured output |
| 17 | Mini Intrusion Detection Rule Engine |
| 18 | Local Web App Vulnerability Scanner (against a provided local sandbox app only) |
| 19 | Honeypot Logger — the final, most involved build of the series |

**Week 20** wraps up the series: week 19's solution, a completion summary, and a set of self-directed follow-up project ideas for after the schedule ends.

## Ground rules

- Weekly delivery is calendar-driven and doesn't assume the previous week is finished — if a challenge runs long, the fix is to say so and push the schedule back, not to rush it.
- Using AI tools (including Claude) to help write code is fine and expected — the point is doing the reasoning and being able to explain why the code works, not typing every character unassisted.
- Every challenge that touches live systems stays scoped to synthetic data, localhost, or infrastructure Paul owns himself (a personal free-tier AWS account for the `boto3` week; a provided local sandbox app for the vuln-scanner week) — nothing here ever points at a real or third-party target.

## Working through this yourself

Feel free to clone this repo and work through the challenges on your own — the briefs, starter code, sample data, and tests don't depend on anything personal to me.

1. Clone the repo and open a week's folder (`course_material/week_01/`, `course_material/week_02/`, …).
2. Read that week's `weekNN_challenge.md` first, in full, before touching code — it has the problem statement, the "Plan It First" planning steps, a worked example, and graduated hints if you get stuck.
3. Build your solution against `weekNN_starter.py`, then run `pytest -v weekNN_test.py` (from week 5 on, `pip install -r requirements.txt` first) until it's green.
4. Only after you have your own working solution, compare it against `course_generated_solutions/week_NN/weekNN_solution.py` and its `weekNN_explanation.md` — reading the reference first defeats the point.
5. From week 5 on, if you fork the repo, `.github/workflows/ci.yml` will run pytest plus a `bandit` scan against `user_created_solutions/` automatically on every push. If you put your own solutions somewhere else, update both commands in that workflow file to point at your folder instead — otherwise CI will run against an empty (or wrong) path.

One caveat: the weekly *delivery* — a new challenge landing on a fixed schedule, paired with a reasoning walkthrough on the previous one — is driven by a private scheduled Claude task tailored to my own skill gaps (diagnosed up front, then referenced throughout). Cloning the repo gets you everything already generated, growing by one week at a time, but not that personal delivery mechanism itself. If you want the same "one challenge a week, automatically" experience, the more direct path is setting up something equivalent yourself; otherwise the material published here stands on its own as a self-paced syllabus you can work through at whatever pace suits you.

## Using pre-commit

On top of the CI checks that run on GitHub after a push, this repo uses [pre-commit](https://pre-commit.com/) to catch the same lint/format issues locally, before a commit is even made:

1. `pip install -r requirements.txt` (already includes `pre-commit` and `ruff`).
2. `pre-commit install` — one-time setup per clone, wires the hooks into `.git/hooks/pre-commit`.

From then on, every `git commit` automatically runs `ruff check --fix` and `ruff format` (config in `.pre-commit-config.yaml`) against the files being committed. If a hook finds something fixable, it fixes it in place and stops the commit so the fix can be reviewed and re-staged — re-run `git commit` to complete it.

Pre-commit and CI serve different roles and both stay in place: pre-commit is a local convenience that auto-fixes and can be bypassed (`git commit --no-verify`), while `.github/workflows/ci.yml` re-runs `ruff check`/`ruff format --check` (no auto-fix) plus pytest and bandit as the actual enforcement gate — so a skipped or missing local hook still gets caught before anything merges.

## Progress

Tier 0 (Level-Up Phase) is complete — weeks 1 through 4 done. Tier 1 (Novice) starts next, bringing the CI/CD pipeline online.

---

*The curriculum itself — challenge briefs, starter code, tests, and reference solutions — is generated week by week through prompting with Claude, originally scoped around a diagnostic of my own Python skill gaps as a security engineer.*
