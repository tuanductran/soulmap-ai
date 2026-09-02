---
name: testing-strategy-review
description: Review and improve SoulMap AI test strategy so pytest coverage, eval coverage, and smoke checks match the real repo risks. Relevant for judging whether coverage matches real risk, and for deciding what a new test should actually protect.
---

# Testing strategy review

Use this skill when deciding what tests to add, tighten, or remove after changes to
code, docs contracts, local workflow layers, or eval surfaces.

## Do not use this skill for

- editing `evals/datasets/groups.json` or response-eval cases as the main task, use
  [`eval-suite-maintainer`](../eval-suite-maintainer/SKILL.md)
- release-wide consistency review, use
  [`release-readiness-review`](../release-readiness-review/SKILL.md)
- isolated code cleanup with no test-strategy question, use
  [`code-quality-review`](../code-quality-review/SKILL.md)

## Mission

Keep test coverage targeted, honest, and proportional to the repo's real contracts.

For this repo, prefer Python-focused tests over doc or workflow policing tests.

## Sources to check first

- `../rules/evals-and-testing.md`
- `docs/engineering/TESTER.md`
- `tests/`
- `evals/`
- the changed implementation or docs files

## What to look for

- behavior changes with no matching regression test
- docs or workflow contracts that should be protected by evals, smoke checks, or
  review instead of broad pytest policing
- duplicated tests that do not protect meaningful behavior
- eval-only claims that are missing source markers or coverage links
- stale tests asserting an old contract
- pytest files that only police Markdown, docs, README wording, local AI workflow
  structure, or other non-executable surfaces

## Workflow

1. Read the changed files and identify the real contract that moved.
2. Decide whether the right protection is a unit test, eval case, smoke check, or
   explicit review step.
3. Default to Python runtime tests. Avoid new pytest files for non-Python surfaces
   unless executable behavior would otherwise be unprotected.
4. Add the smallest high-signal coverage that would catch the regression again.
5. Remove or update stale assertions that no longer match the real contract.
6. Run the narrowest checks first, then the broader suite when needed.

## Expected output

### Findings

List the coverage gaps or stale tests first.

### Fixes

Summarize what test strategy was added, tightened, or cleaned up.

### Validation

State which test commands or eval commands were run.

## Definition of done

The changed surface should be:

- protected by the right kind of test
- free of stale contract assertions
- consistent with docs and eval claims
- validated with the commands that matter for that layer
