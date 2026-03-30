---
name: bug-hunt-review
description: Find real bugs and silent regressions in SoulMap AI across Python, shell, workflows, and repo contracts, with findings-first review and fix-focused follow-through.
---

# Bug hunt review

Use this skill when the main goal is to uncover defects, weak assumptions, false-pass
checks, or production-risk regressions before they spread.

## Do not use this skill for

- broad architecture planning with no concrete failure surface, use
  [`research-and-gap-analysis`](../research-and-gap-analysis/SKILL.md)
- isolated code cleanup with no bug risk question, use
  [`code-quality-review`](../code-quality-review/SKILL.md)
- product doctrine or response-safety policy review alone, use
  [`ai-prompt-engineering-safety-review`](../ai-prompt-engineering-safety-review/SKILL.md)

## Mission

Surface the highest-signal defects first, especially the ones that can pass casual
inspection, green CI, or narrow local checks.

## Sources to check first

- the changed files and their nearest tests
- `tests/`
- `evals/`
- `docs/engineering/TESTER.md`
- `../rules/evals-and-testing.md`
- `../rules/repo-workflow.md`

## What to look for

- pass-green examples that still produce weak or misleading behavior
- shell or workflow checks that can fail silently
- docs, evals, and runtime surfaces that no longer describe the same contract
- regressions hidden by over-broad mocks or weak test assertions
- hooks, scripts, or CI jobs that no longer match the current command flow

## Workflow

1. Start from the highest-risk behavior or workflow surface.
2. Reproduce or narrow the defect before proposing cleanup.
3. List findings first, ordered by practical severity.
4. Fix only the defects you can justify with concrete behavior, not speculative polish.
5. Add or tighten the smallest regression protection that would catch the issue again.
6. Run the narrowest checks first, then the broader repo checks when the bug touched shared behavior.

## Expected output

### Findings

List the concrete defects first, with file references and why they matter.

### Fixes

Summarize the changes that removed the defect or closed the false-pass path.

### Validation

State which tests, evals, or workflow commands were run.

## Definition of done

The reviewed surface should be:

- free of the concrete defect that triggered the review
- protected against the same failure repeating quietly
- consistent across runtime, docs, and evals when the bug crossed those layers
- validated with commands that exercise the actual risk
