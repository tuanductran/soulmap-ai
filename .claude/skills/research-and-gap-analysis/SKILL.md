---
name: research-and-gap-analysis
description: Analyze the SoulMap AI repository to identify missing pieces, inconsistencies, and next highest-value improvements without inventing work the repo does not need.
---

# Research And Gap Analysis

Use this skill when you want a structured analysis of what is missing, incomplete, or
out of sync in the repository.

## Do not use this skill for

- Pre-release shipping checks - use
  [`release-readiness-review`](../release-readiness-review/SKILL.md) for those
- Fixing gaps you find - use the appropriate skill for the specific task
- Writing or updating docs - use
  [`docs-and-api-writer`](../docs-and-api-writer/SKILL.md)

## Mission

Find the highest-value gaps in the project and describe them clearly.

This is useful for:

- repo audits
- pre-release gap checks
- planning the next implementation pass
- identifying missing docs, tests, or brand alignment

## What To Analyze

### Code Vs Docs

Check for drift between implementation and documentation.

### Docs Vs Brand

Check whether public and internal docs still reflect the SoulMap brand posture.

### Tests Vs Risk

Check whether the riskiest behaviors are protected by tests.

### Surface Completeness

Check whether the repo has the supporting assets needed for the story it tells.

Examples:

- docs
- changelog
- packaging
- evals
- release guidance

## Sources To Check First

Always start with these before forming any opinion about what is missing:

- `AGENTS.md` - primary behavioral and safety contract
- `docs/repo-contract.md` - structural source of truth for all repo surfaces
- `docs/safety-enforcement-matrix.md` - evidence map for safety claims
- `docs/maintenance-boundary.md` - scope-control document
- `skills/` and `templates/` - shipped knowledge base
- `modules/` - implementation; compare against docs and tests
- `tests/` - check for coverage gaps against the riskiest behaviors
- `CHANGELOG.md` - what has changed recently

## Workflow

1. Scan the repo structure.
2. Read the central docs and policies first.
3. Inspect the highest-risk code and test surfaces.
4. Group missing pieces by severity and type.
5. Recommend the smallest high-value next steps.

## Expected Output

### Findings

List the most important gaps first.

### Why It Matters

Explain the impact briefly.

### Suggested Next Steps

Offer concise, practical follow-ups grounded in the repo's actual needs.

## Writing Rules

- Prefer concrete gaps over vague quality commentary.
- Do not pad the analysis with generic best practices.
- Distinguish clearly between current gaps and optional improvements.

## Definition Of Done

The analysis should leave the team with:

- a clear picture of what is missing
- sensible prioritization
- grounded next steps instead of generic advice
