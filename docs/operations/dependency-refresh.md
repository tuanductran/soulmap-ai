# Dependency refresh and advisory review

This checklist is the operational boundary for Phase 12. It covers development-tool dependencies, the `uv.lock` baseline, CI/release pins and transitive package changes. It does not authorize a new runtime dependency, a Python-version expansion, a semantic safety classifier or a platform adapter. For the next bounded P1 cycle, use the implementation-ready [P1 dependency/advisory refresh plan](p1-dependency-advisory-refresh-plan.md) together with this checklist.

## Automation tooling

Two dependency-update bots are currently configured: `.github/dependabot.yml` (uv and
github-actions ecosystems, weekly) and `renovate.json` (repo root, `config:recommended`).
As of the last review, Dependabot is the actively used tool: it has open pull requests
for routine dev-dependency bumps, while Renovate's merged history is limited to a
github-actions pin that Dependabot's own `github-actions` ecosystem entry already
covers. This overlap has not caused a confirmed duplicate-PR conflict, but the two
tools are not tracking a documented division of labor. Do not add a third tool or
expand either config to resolve this; if you decide to keep only one, that decision
belongs to the repository owner, not to routine dependency-refresh work.

## Trigger policy

Start this process only when there is a concrete trigger: a security advisory, an upstream deprecation warning, a documented incompatibility, a meaningful bugfix release, lockfile drift, a CI/release failure or a deliberate maintenance window. A newly published package version alone is not proof that the lockfile is stale; `uv` checks project metadata and requires an explicit refresh when maintainers decide to upgrade.[1]

| Trigger | Required first action | Expected evidence |
| --- | --- | --- |
| Security advisory | Identify affected direct and transitive packages, affected versions and fixed versions | Advisory URL, impact assessment and mitigation decision |
| Deprecation warning | Reproduce the warning on the locked baseline | Warning output, upstream deprecation policy and compatibility plan |
| Incompatibility or bugfix | Build a focused reproducer or test case | Failing/passing reproduction and release-note link |
| Lockfile drift | Run `uv lock --check` and compare project metadata with `uv.lock` | Exact drift explanation and lock diff |
| Planned maintenance | Define one update group and its purpose | Scope statement before changing versions |

## Baseline capture

Create a branch from the latest `origin/main` and capture the repository state before changing dependencies. Do not refresh the lockfile in place on a release branch.

```bash
git fetch --prune origin main
git switch -c chore/dependency-refresh origin/main
uv tree --depth 1
uv lock --check
python --version
uv --version
git status --short --branch
```

Record the current Python floor (`>=3.11`), CI Python baseline (`3.11`), direct package versions, CI-only pins and the exact trigger. The authoritative package matrix is [`package-compatibility-research.md`](../engineering/package-compatibility-research.md).

## Source and impact review

For every package or pin under consideration, read the official release notes, compatibility policy and advisory record before editing `pyproject.toml`, `uv.lock` or workflow pins. Distinguish a security update from a routine version update; automation can open a pull request, but maintainers still review the changelog, release notes, compatibility and tests before merging.[2]

| Review question | Required answer |
| --- | --- |
| What changed? | Package, old version, new version and direct/transitive status |
| Why now? | Security, deprecation, incompatibility, bugfix, drift or planned maintenance |
| Is Python 3.11 supported? | Yes/no, with official source |
| Does the change affect runtime, dev tooling, CI or release? | Explicit surface and expected behavior |
| Are there transitive changes? | List relevant packages and license/security implications |
| Is a new tool proposed? | Document the repository contract or blocker it protects; otherwise do not add it |
| What is the rollback? | Revert commit, restore lockfile and rerun baseline gates |

## Update rules

Keep one maintenance purpose per pull request. Group updates only when they share a reason and can be validated together. Valid groups include security fixes, compatibility fixes, toolchain maintenance, reproducibility fixes and build/release fixes. Do not combine a dependency refresh with unrelated knowledge, routing, safety or platform-adapter changes.

Use the smallest update command that expresses the intended scope. Inspect the complete `uv.lock` diff and do not accept unrelated package churn without an explanation. Preserve the Python 3.11 support floor and do not add a scanner, replace a package or expand the version matrix merely because an alternative exists.

## Validation contract

Run focused tests for the changed package or workflow first. Then run the complete repository gate before review or release:

```bash
uv run soulmap format
uv run soulmap markdown-contract --root .
uv run soulmap check-links --root .
uv run soulmap check-case --root .
uv run soulmap lint
uv run soulmap test -n auto -q
uv run soulmap audit-knowledge
uv run soulmap eval-markdown-contracts
uv run soulmap eval-groups
uv run soulmap eval-responses
uv run soulmap build
uv run soulmap build --skill
uv run soulmap library-manifest
uv run python scripts/verify_artifact_hashes.py
uv run vulture
uv run deptry .
uv run pip-audit
uv lock --check
```

When a parallel or randomized test fails, preserve the pytest-randomly seed, xdist worker count, operating system, Python version and lock state. Use the emitted diagnostic command and then reproduce serially with `-n 0`; do not disable a test to hide order dependence. Treat pytest-timeout as a hang/deadlock signal, not a performance benchmark.

## Pull request evidence

The pull request description must state the trigger, scope, old/new versions, official sources, Python 3.11 compatibility, transitive changes, focused-test result, full-gate result and rollback plan. If a security advisory is involved, state whether the repository is affected and why the selected version resolves it. If no update is made, record the reason and the next review trigger.

A release-affecting update must also show successful standard and skill builds, Library manifest generation and artifact hash verification. Do not perform version bump, tag, changelog mutation or release upload before validation has passed.

## Post-merge follow-up

After merge, confirm the main-branch CI and CodeQL runs against the merge commit, verify the lockfile remains clean, and update [`ROADMAP.md`](../ROADMAP.md) or the compatibility matrix if the baseline changed. Keep platform adapters and live ChatGPT/Claude/Gemini/Poe acceptance work outside this Phase 12 process until their deployment prerequisites exist.

## References

[1]: https://docs.astral.sh/uv/concepts/projects/sync/ "uv locking and syncing"
[2]: https://docs.GitHub.com/en/code-security/concepts/supply-chain-security/dependabot-version-updates "GitHub Dependabot version updates"
