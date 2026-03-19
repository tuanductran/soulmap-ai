---
name: release-readiness-review
description: Review whether SoulMap AI is ready to ship by checking docs, changelog, tests, packaging, and user-facing claims for release consistency.
---

# Release Readiness Review

Use this skill before shipping notable changes to the repository.

This skill is for launch and release hygiene, not feature ideation.

## Mission

Check whether the repo tells a consistent, shippable story across:

- code
- docs
- tests
- changelog
- packaging
- user-facing claims

## Primary Sources

Always inspect:

- `README.md`
- `CHANGELOG.md`
- `docs/DEV.md`
- `docs/TESTER.md`
- `docs/API.md`
- `docs/OPERATIONS.md`
- `templates/launch-readiness-checklist.md`
- relevant tests under `tests/`

## What To Check

### Docs Sync

Verify that newly added modules, workflows, or constraints are reflected in docs.

### Changelog Accuracy

Verify that `CHANGELOG.md` captures meaningful added, changed, or removed behavior.

### Test Coverage

Check whether important changes are protected by:

- unit or regression tests
- eval cases
- build or packaging checks

### Packaging Readiness

Confirm that the distribution artifact still matches what the repo claims to ship.

### Public Claims

Check whether README and public-facing docs make claims the implementation can support.

## Workflow

1. Inspect the changed files.
2. Compare them against docs and release notes.
3. Identify gaps that would confuse a user, tester, or maintainer.
4. Fix the highest-signal gaps first.
5. Leave a concise release-readiness summary.

## Expected Output

When reviewing, structure the result as:

### Findings

List shipping blockers or inconsistencies first.

### Fixes

Summarize what was updated to restore readiness.

### Residual Risks

Call out anything still unverified, untested, or intentionally deferred.

## Writing Rules

- Prefer concrete release risks over vague quality statements.
- Keep the focus on what affects shipping confidence.
- Do not turn the review into a feature roadmap.

## Definition Of Done

The repo should be:

- documented honestly
- changelog-consistent
- test-backed where it matters
- ready to package and hand off
