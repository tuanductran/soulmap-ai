---
name: tooling-performance-review
description: Review and improve SoulMap's repo performance where it actually matters, such as lint speed, eval cost, packaging flow, subprocess-heavy tests, and shell-wrapper overhead. Relevant for slow lint, eval, packaging, or subprocess-heavy runs, where the cost should be measured before anything is rewritten.
---

# Tooling performance review

Use this skill when the task is about speeding up local workflows, CI checks, eval
runs, packaging, or Python tooling behavior in this repository.

## Do not use this skill for

- product behavior or response doctrine
- generic app-performance advice unrelated to this repo
- frontend rendering, API latency, or database tuning work the repo does not contain

## Mission

Improve performance where the repository really pays for it:

- repeated repo scans
- redundant subprocesses
- slow or overlapping checks
- packaging and build overhead
- eval runtime growth

## Sources to check first

- `../rules/performance-tooling.md`
- `../rules/python-tooling.md`
- `../rules/shell-scripting.md`
- `pyproject.toml`
- `docs/engineering/DEV.md`
- `docs/engineering/TESTER.md`
- `src/soulmap/devtools/`
- the nearest tests in `tests/`

## What to look for

- repeated full-repo work that could be shared
- wrappers or subprocesses layered on top of canonical commands
- test suites that can be narrowed during iteration without losing confidence
- build or eval steps that are duplicated in docs, scripts, and CI
- optimizations that would make the repo harder to understand than the time saved

## Workflow

1. Measure or locate the real slow path.
2. Confirm whether the problem is scan cost, subprocess cost, packaging cost, or test scope.
3. Prefer the smallest change that removes duplicate work.
4. Keep Python logic in `src/` and shell logic thin.
5. Update tests or docs if the canonical command flow changes.
6. Run the narrowest relevant checks, then confirm the broader workflow still passes.

## Validation ladder

- targeted `pytest`
- `uv run soulmap lint --skip-tests`
- targeted packaging or eval command
- full `uv run soulmap test -n auto -q` when shared behavior changed

## Definition of done

The repo should be faster in a meaningful way, while still being:

- clearer to maintain
- aligned with the canonical command flow
- fully typed and testable
- free of speculative complexity
