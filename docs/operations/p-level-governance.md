# P-level pull request safety governance

P-level work is a prioritization label, not permission to widen SoulMap. A pull request
whose title begins with `[P0]`, `[P1]`, `[P2]` or `[P3]` is checked by the
`p-level-governance.yml` workflow before review. The check is deterministic: it verifies
that review metadata declares the task's safety boundary, evidence and rollback path.

## Scope

This policy applies only to P-level pull requests. Other repository changes keep the
existing branch, test, Markdown-contract and release rules. The check does not classify
content or replace human review. It protects the decision boundary stated in
`AGENTS.md`, the safety-enforcement matrix and the maintenance boundary.

## Required metadata

Put these values in the pull request body. The checker parses them exactly from these lines:

```markdown
- **Priority:** P1
- **Safety boundary:** preserved
- **Evidence:** Dependency advisory URL and full repository gate.
- **Rollback:** Revert the dependency refresh commit and restore the previous lockfile.
```

The priority must match the title prefix. `Safety boundary` is either `preserved` or
`changed`. Evidence cannot be `none`, `n/a` or `not applicable`. Rollback must say how
to revert the change.

## When a safety boundary changes

Use `changed` only for doctrine, routing, detector, guard, response-contract,
crisis/dependency, packaging or shipping-boundary changes. Add this section with an ADR
decision, positive regression, near-miss regression and safety-matrix disposition:

```markdown
## Safety change evidence
```

An ADR can state that no architecture reversal is required, but it must be explicit.

This does not override the protected-module policy. Crisis and dependency architecture
changes still require the ADR and full evaluation evidence required by the existing
repository contracts.

## P1 dependency/advisory refresh

P1 dependency work normally uses `preserved`. Its evidence names the trigger, official
source, Python 3.11 compatibility review and validation result. Follow
[`dependency-refresh.md`](dependency-refresh.md) for the complete operational process.

## Local simulation

The checker consumes a GitHub pull-request event payload. To simulate it locally, create
a minimal JSON event file and run:

```bash
uv run python scripts/check_p_level_pr.py --event-path /path/to/pull-request-event.json
```

## Non-goals

This governance check does not create a web surface, API, database, response generator,
semantic classifier, platform adapter or automatic dependency merge. It records the
evidence maintainers need before choosing a bounded change.
