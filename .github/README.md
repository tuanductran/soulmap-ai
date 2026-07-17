# GitHub Repository Automation

This directory contains GitHub Actions workflows, Dependabot configuration, and
repository hosting metadata for SoulMap AI.

None of these files ship in the distributed package. They are local repository
operations surfaces only.

For the structural source of truth about this directory and its role, see
[docs/engineering/repo-contract.md](../docs/engineering/repo-contract.md).

## Workflows

### `ci.yml` : Continuous Integration

Runs on every pull request, every push to `main`, and on manual dispatch.

Uses a matrix strategy across Ubuntu, macOS, and Windows. All three platforms must
pass before a PR is considered green.

Stages (in order):

1. **Lint** : Ruff, Pyright, pymarkdown, actionlint (Ubuntu only)
2. **Knowledge audit** : `soulmap audit-knowledge`, verifies Markdown ownership
   and applies a duplicate-count guard
3. **Dead code detection** : `vulture`
4. **Dependency analysis** : `deptry`
5. **Tests** : `soulmap test` with parallel execution via pytest-xdist
6. **Coverage report** : term-missing report (Ubuntu only)
7. **Safety evals** : `tests/eval_regression/test_safety_evals.py`
8. **Response evals** : `soulmap eval-responses`
9. **Grouped routing evals** : `soulmap eval-groups`
10. **Markdown contract sync evals** : `soulmap eval-markdown-contracts`
11. **Build smoke** : `soulmap build` and `soulmap build --skill`

Produces two separate jobs in addition to the main lint matrix:

- **`knowledge-audit`** : runs independently on Ubuntu, uploads
  `knowledge-inventory.txt` as a CI artifact
- **`build`** : runs after `lint` passes, uploads `dist/soulmap-ai.zip` and
  `dist/soulmap-ai.skill` as CI artifacts

The `SOULMAP_REPO_ROOT` environment variable is set to the checkout workspace
in every job. Runtime tooling uses this to locate the repository root when
running outside the project directory.

### `autofix.yml` : Auto-formatter

Runs on every pull request.

Applies `soulmap format` to the branch and commits any resulting changes using
`autofix-ci/action`. Commit message: `style(ci): auto-apply repo formatting`.

This means PRs automatically stay formatted without contributor friction. The
committed style changes appear in the PR diff before merge.

### `release.yml` : Release

Runs on manual dispatch only (`workflow_dispatch`). Does not trigger automatically.

Steps:

1. Verify repo: lint, grouped evals, safety evals, response evals, Markdown
   contract sync evals
2. Configure git author as `github-actions[bot]`
3. Bump version and update `CHANGELOG.md` via `cz bump --yes`
4. Normalize `CHANGELOG.md` formatting via pymarkdown fix
5. Build `dist/soulmap-ai.zip` and `dist/soulmap-ai.skill`
6. Push the bump commit and version tag
7. Create a GitHub Release and upload both distribution artifacts

The release workflow is the only place a version tag is created. Tags follow the
format `v{version}` (e.g. `v0.6.0`).

### `codeql.yml` : CodeQL Security Analysis

Runs on pushes and pull requests to `main`, and on a weekly schedule (Mondays at
03:00 UTC).

Performs static security analysis on Python source using the `security-extended`
and `security-and-quality` query suites. Results appear in the GitHub Security tab.

## Other Files

### `dependabot.yml`

Configures Dependabot to check for dependency updates weekly:

- `uv` package ecosystem (Python dependencies via `pyproject.toml` and `uv.lock`)
- `github-actions` ecosystem (workflow action version pins)

### `FUNDING.yml`

Repository funding links displayed by GitHub. Not part of the product or tooling.

## Relationship to Local Hook Layer

The `.github/` workflows run in GitHub's CI environment. The local hook layer in
`.claude/hooks/` runs on a contributor's machine during Claude Code sessions. The
two layers are complementary, not duplicates.

The local hooks run fast checks on individual file edits (format, lint, test).
The CI workflows run the full validation suite on the complete repository.

For local hook behavior, see [../.claude/README.md](../.claude/README.md).
