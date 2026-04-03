---
name: code-quality-review
description: Review and improve Python code quality in SoulMap AI so typing, helper usage, exception handling, and repo tooling conventions stay consistent.
---

# Code quality review

Use this skill when reviewing or improving Python implementation quality in `src/`,
compatibility wrappers, `tests/`, or `scripts/`.

## Do not use this skill for

- product doctrine or response-safety review, use
  [`ai-prompt-engineering-safety-review`](../ai-prompt-engineering-safety-review/SKILL.md)
- eval suite design, use [`eval-suite-maintainer`](../eval-suite-maintainer/SKILL.md)
- packaging and release checks, use
  [`packaging-maintainer`](../packaging-maintainer/SKILL.md)

## Mission

Keep Python changes clear, typed, maintainable, and consistent with the repo's existing
tooling contract.

## Sources to check first

- `pyproject.toml`
- `../rules/python-tooling.md`
- `../rules/source-character-safety.md`
- `docs/engineering/DEV.md`
- the target Python files and nearby tests

## What to look for

- stale or duplicated helper logic
- weak typing or type drift against repo conventions
- broad exception handling or hidden failure paths
- dead branches, unused fields, or wrappers that add no value
- local code that should use shared helpers in
  `src/soulmap/runtime/io/cli_payload.py` or
  `src/soulmap/runtime/io/text_normalization.py`

## Workflow

1. Read the target Python files and the closest tests first.
2. Compare the implementation with `pyproject.toml` and `../rules/python-tooling.md`.
3. Identify concrete quality issues that affect clarity, correctness, or maintenance.
4. Make the smallest correct change that improves the code without widening scope.
5. Update tests when the observable contract changes.
6. Run the repo checks needed for the touched files.

## Expected output

### Findings

List the concrete code-quality issues first.

### Fixes

Summarize the changes that improved type safety, helper usage, or readability.

### Validation

State which checks were run and whether they passed.

## Definition of done

The updated code should be:

- simpler or clearer than before
- aligned with repo tooling rules
- free of obvious duplicated logic
- covered by the right tests for the changed behavior
