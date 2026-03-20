---
name: docs-and-api-writer
description: Write and update technical docs for SoulMap AI so README, API docs, developer guides, and tester guides stay aligned with the actual repo behavior.
---

# Docs And API Writer

Use this skill when writing or updating technical documentation in this repository.

Relevant files include:

- `README.md`
- `docs/API.md`
- `docs/DEV.md`
- `docs/TESTER.md`
- `docs/OPERATIONS.md`
- `docs/README.md`

## Do not use this skill for

- Reviewing or editing public-facing brand copy (landing pages, onboarding, FAQ) - use
  [`brand-copy-review`](../brand-copy-review/SKILL.md) for those
- Editing knowledge files under `skills/` or `templates/` - use
  [`knowledge-base-maintainer`](../knowledge-base-maintainer/SKILL.md)
- Reviewing prompt engineering or safety behavior - use
  [`ai-prompt-engineering-safety-review`](../ai-prompt-engineering-safety-review/SKILL.md)

## Mission

Keep the docs accurate, readable, and faithful to the implementation.

This skill should help when:

- a new module or workflow was added
- docs have drifted from code
- setup instructions are outdated
- CLI contracts need to be explained clearly

## Sources Of Truth

Always check:

- the relevant files under `modules/`
- `README.md`
- existing tests under `tests/`
- `AGENTS.md` when behavior or safety is involved

## What To Check

### Implementation Accuracy

Make sure docs describe what the repo actually does today.

### Contract Clarity

For CLI and API-like surfaces, document:

- entrypoints
- expected input
- expected output
- key constraints
- important failure cases

### Audience Fit

Match the document to its user:

- README for broad orientation
- API docs for integrators
- DEV docs for contributors
- TESTER docs for QA and regression checks

### Cross-Doc Consistency

Keep terminology and workflow descriptions consistent across files.

## Workflow

1. Read the target doc.
2. Read the relevant code and tests.
3. Identify stale or missing parts.
4. Update the doc with the smallest complete correction.
5. Preserve the established tone of the file.

## Expected Output

For review tasks, structure the result as:

### Findings

List gaps between docs and implementation.

### Updated Documentation

Provide the revised text or summary of the change.

### Notes

Mention any adjacent docs that may also need to stay in sync.

## Writing Rules

- Prefer concrete commands and examples.
- Do not document features the repo does not expose.
- Keep examples minimal but executable.
- Avoid marketing language in technical docs.

## Definition Of Done

The updated docs should be:

- accurate
- easy to follow
- consistent with code and tests
- useful to the intended reader
