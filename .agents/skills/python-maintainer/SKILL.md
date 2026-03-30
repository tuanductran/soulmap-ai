---
name: python-maintainer
description: Maintain SoulMap's Python surfaces so src packages, tests, scripts, and pyproject-based tooling stay aligned, typed, and easy to validate.
---

# Python maintainer

Use this skill when the task is primarily about Python work across
`src/soulmap_runtime/`, `src/soulmap_devtools/`, `tests/`, `scripts/`, or
`pyproject.toml`.

## Do not use this skill for

- product doctrine or response behavior, use
  [`ai-prompt-engineering-safety-review`](../ai-prompt-engineering-safety-review/SKILL.md)
- framework writing in the shipped knowledge base, use
  [`framework-author`](../framework-author/SKILL.md)
- pure docs work with no Python contract change, use
  [`docs-and-api-writer`](../docs-and-api-writer/SKILL.md)

## Mission

Keep Python changes focused, typed, testable, and aligned with the repo's actual
tooling contract.

This skill is the entry point for Python work. Route into narrower skills only when
the task clearly centers on CLI behavior, test strategy, packaging, or detector logic.

## Sources to check first

- `pyproject.toml`
- `../rules/python-tooling.md`
- `docs/engineering/DEV.md`
- the target Python files
- the closest tests in `tests/`

## What to look for

- drift between `pyproject.toml`, shell scripts, and Python tooling entry points
- duplicated helper logic across `src/` and `scripts/`
- missing or stale regression tests after Python contract changes
- weak typing, noisy wrappers, or brittle subprocess behavior
- changes that should stay local instead of creating new abstractions too early

## Workflow

1. Read `pyproject.toml`, the target files, and the nearest tests before editing.
2. Decide whether the task is mostly code quality, CLI tooling, test strategy, packaging, or detector work.
3. Keep one clear responsibility per change. Prefer small typed edits over broad rewrites.
4. Update tests when behavior, tooling flow, or configuration contracts change.
5. Run the narrowest checks that match the touched files first.
6. Run broader repo checks when the change affects shared tooling or repo-wide contracts.

## Validation ladder

Start small, then widen only when the change touches shared surfaces:

- targeted `pytest`
- `python -m pyright ...`
- `python -m soulmap_devtools.cli.lint --skip-tests`
- full `python -m pytest -n auto -q`

## Related skills

- use [`code-quality-review`](../code-quality-review/SKILL.md) for implementation cleanup inside Python files
- use [`cli-tooling-maintainer`](../cli-tooling-maintainer/SKILL.md) for command surfaces and shell wrappers
- use [`testing-strategy-review`](../testing-strategy-review/SKILL.md) for regression coverage decisions
- use [`packaging-maintainer`](../packaging-maintainer/SKILL.md) when build metadata or shipped artifacts move
- use [`detector-engineer`](../detector-engineer/SKILL.md) when the change is detector-specific

## Definition of done

The changed Python surface should be:

- aligned with `pyproject.toml`
- covered by the right tests
- clean under Pyright and repo linting
- simpler to maintain than before
