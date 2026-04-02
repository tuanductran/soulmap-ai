---
name: eval-audit-review
description: Audit SoulMap AI evals so datasets, assertions, source markers, and golden responses stay source-backed, failure-oriented, and hard to game.
---

# Eval audit review

Use this skill when the task is to inspect or improve the trustworthiness of SoulMap's
eval system rather than only adding one more case.

## Do not use this skill for

- routine edits to `evals/datasets/` as the main task, use
  [`eval-suite-maintainer`](../eval-suite-maintainer/SKILL.md)
- broad release consistency review, use
  [`release-readiness-review`](../release-readiness-review/SKILL.md)
- Python-only cleanup with no eval question, use
  [`python-maintainer`](../python-maintainer/SKILL.md)

## Mission

Keep evals honest, source-backed, and useful against real failure modes instead of
optimizing for easy green runs.

## Sources to check first

- `evals/README.md`
- `evals/datasets/`
- `tests/contract/`
- `tests/eval_regression/`
- `src/soulmap/devtools/evals/`
- the source Markdown or Python files each eval claims to protect

## What to look for

- evals that pass because assertions are too loose
- cases with no clear source backing in `AGENTS.md`, `skills/`, or `templates/`
- wording checks that drift from runtime examples
- evaluator logic that is brittle, fuzzy, or easy to satisfy accidentally
- important failure modes that appear in code or docs but are not represented in datasets

## Workflow

1. Identify the failure mode or product contract the eval is supposed to protect.
2. Check whether the current dataset, harness, and source files all describe the same thing.
3. Tighten assertions only where the behavior is actually important.
4. Prefer a few sharp cases over many noisy ones.
5. Add or update `source_markers` when confidence needs to be explicit.
6. Run the matching eval commands, then the closest pytest contracts.

## Expected output

### Findings

List the eval weaknesses first, especially loose assertions, stale source links, or blind spots.

### Fixes

Summarize the dataset, harness, or contract changes that improved audit quality.

### Validation

State which eval and pytest commands were run.

## Definition of done

The audited eval surface should be:

- harder to game accidentally
- clearly tied back to real source files or runtime behavior
- focused on meaningful failure modes
- validated with the exact commands maintainers actually use
