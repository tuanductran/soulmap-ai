---
name: docs-and-api-writer
description: Write and update technical docs for SoulMap AI so README, API docs, developer guides, and tester guides stay aligned with the actual repo behavior. Relevant for updating README, API docs, developer or tester guides, and for fixing documentation that has drifted from the implementation.
---

# Docs and API writer

Use this skill when writing or updating technical documentation in this repository.

Relevant files include:

- `README.md`
- `docs/engineering/API.md`
- `docs/engineering/DEV.md`
- `docs/engineering/TESTER.md`
- `docs/operations/OPERATIONS.md`
- `docs/README.md`

## Do not use this skill for

- Reviewing or editing public-facing brand copy (landing pages, onboarding, FAQ), use
  [`brand-copy-review`](../brand-copy-review/SKILL.md) for those
- Editing knowledge files under `skills/` (shipped) or `templates/` (internal-only), use
  [`knowledge-base-maintainer`](../knowledge-base-maintainer/SKILL.md)
- Reviewing prompt engineering or safety behavior, use
  [`ai-prompt-engineering-safety-review`](../ai-prompt-engineering-safety-review/SKILL.md)

## Mission

Keep the docs accurate, readable, and faithful to the implementation.

This skill should help when:

- a new module or workflow was added
- docs have drifted from code
- setup instructions are outdated
- CLI contracts need to be explained clearly

## Sources of truth

Always check:

- the relevant files under `src/`
- `README.md`
- existing tests under `tests/`
- `SOULMAP.md` when behavior or safety is involved
- `../rules/language-and-grammar.md` for repo-local grammar and style

## What to check

### Implementation accuracy

Make sure docs describe what the repo actually does today.

### Contract clarity

For CLI and API-like surfaces, document:

- entrypoints
- expected input
- expected output
- key constraints
- important failure cases

### Audience fit

Match the document to its user:

- README for broad orientation
- API docs for integrators
- DEV docs for contributors
- TESTER docs for QA and regression checks

### Cross-doc consistency

Keep terminology and workflow descriptions consistent across files.

## Workflow

1. Read the target doc.
2. Read the relevant code and tests.
3. Identify stale or missing parts.
4. Update the doc with the smallest complete correction.
5. Preserve the established tone of the file.

## Expected output

For review tasks, structure the result as:

### Findings

List gaps between docs and implementation.

### Updated documentation

Provide the revised text or summary of the change.

### Notes

Mention any adjacent docs that may also need to stay in sync.

## Writing rules

- Prefer concrete commands and examples.
- Follow `../rules/language-and-grammar.md` for sentence case, active voice,
  plain wording, and list discipline.
- Do not document features the repo does not expose.
- Keep examples minimal but executable.
- Avoid marketing language in technical docs.

## Definition of done

The updated docs should be:

- accurate
- easy to follow
- consistent with code and tests
- useful to the intended reader
