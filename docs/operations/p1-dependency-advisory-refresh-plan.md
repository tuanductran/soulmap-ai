# P1 plan: Controlled dependency and advisory refresh

## Objective

Prepare one bounded P1 maintenance cycle for a real dependency, advisory, deprecation,
compatibility or lockfile trigger. The cycle preserves SoulMap's Python 3.11 baseline,
deterministic safety boundary and Markdown-first architecture. It does not restore the
removed web stack or authorize a new runtime dependency, platform adapter, Python version
expansion or release by default.

## Entry criteria

Start only when one of these is available:

| Trigger | Minimum evidence |
| --- | --- |
| Security advisory | Advisory URL, affected package/version and fixed-version assessment. |
| Deprecation | Reproduced warning plus upstream lifecycle policy. |
| Incompatibility or bugfix | Focused reproduction and upstream release notes. |
| Lockfile drift | `uv lock --check` output and an explanation of the drift. |
| Planned maintenance | Written purpose for one package group and a compatible maintenance window. |

A new version alone is not a trigger. The current Dependency Dashboard is only an
inventory; it is not evidence to refresh a package by itself.

## Scope guard

The P1 PR title uses `[P1] chore(deps): <bounded purpose>` and completes the P-level
metadata with `Safety boundary: preserved`. The PR changes one update group only:
security fix, compatibility fix, reproducibility fix, CI/release pin or Python tooling
maintenance. It must not combine a dependency update with skills, routing, detector,
guard, response-contract, platform or web changes.

## Execution sequence

1. Create an issue that records the trigger, affected surface and owner decision.
2. Branch from current `origin/main` as `chore/dependency-refresh-<purpose>`.
3. Capture `uv tree --depth 1`, `uv lock --check`, Python/uv versions and clean Git
   status before editing a manifest or pin.
4. Review official release notes, advisory, license/transitive impact and Python 3.11
   support. Record old/new versions and why the chosen version resolves the trigger.
5. Apply the smallest update command. Review the complete lockfile diff and reject
   unrelated churn without an explanation.
6. Run a focused reproduction/test first, then the complete dependency refresh gate.
7. Complete P-level PR metadata: trigger/source, compatibility, transitive changes,
   focused/full results and rollback. Do not tag, bump version or upload a release.
8. After merge, verify main CI/CodeQL and `uv lock --check`; update the compatibility
   research only if the maintained baseline actually changed.

## Required validation

Run the canonical gate from `dependency-refresh.md`, including format, Markdown checks,
lint, full parallel tests, knowledge audit, all evals, both builds, Library manifest,
artifact hash verification, Vulture, Deptry and `uv lock --check`. Preserve seed, worker
count, OS, Python version and lock state for any randomized/parallel failure; reproduce
serially before changing tests.

## Rollback

If focused or full validation fails, revert the maintenance commit and restore the prior
`uv.lock`; do not weaken a test, alter a safety boundary or merge partial evidence. If a
merged update later fails main CI, revert the single P1 commit and rerun the known-good
0.9.0 validation gate. Keep artifact release/tag creation separate from the refresh
unless a separately approved release decision exists.

## Definition of done

The P1 cycle is complete only when the issue has trigger evidence, the PR has all
P-level metadata, the full gate and GitHub CI pass, main CodeQL passes, the lockfile is
clean and the post-merge decision is recorded. No release is implied by completion.
