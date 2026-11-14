# Contributing

## Setup

```bash
uv python install 3.11
bash scripts/bootstrap_venv.sh
```

Activating `.venv` is optional when you use `uv run ...`. This repo standardizes on
Python 3.11 for local development and CI.

## Format and lint

```bash
uv run soulmap format
uv run soulmap lint
uv run soulmap markdown-contract --root .
uv run soulmap check-links --root .
uv run soulmap check-case --root .
uv run soulmap check-api-docs --root .
uv run soulmap test
```

The shell bootstrap helper sets up the local environment; formatting, linting, and tests
use the canonical `uv run soulmap ...` commands on every platform.

## Brand Consistency

Before merging, confirm that any changes to positioning, safety, or templates remain
consistent across:

- [README.md](README.md)
- [SKILL.md](SKILL.md), the single shipped Skill entrypoint
- [skills/brand/](skills/brand/)
- [templates/README.md](templates/README.md) (internal-only, not shipped)
- [skills/brand/message-hierarchy.md](skills/brand/message-hierarchy.md)
- [skills/brand/surfaces-and-scope.md](skills/brand/surfaces-and-scope.md)
- [skills/brand/brand-positioning.md](skills/brand/brand-positioning.md)
- [templates/brand-copy.md](templates/brand-copy.md)
- [templates/onboarding-copy.md](templates/onboarding-copy.md)
- [templates/demo-scenarios.md](templates/demo-scenarios.md)
- [templates/launch-readiness-checklist.md](templates/launch-readiness-checklist.md)

## Markdown contract

This repo enforces a small set of Markdown constraints to keep AI tooling and formatters
from breaking structure.

See [docs/engineering/content-contract.md](docs/engineering/content-contract.md).

Ordered lists should stay sequential (`1. 2. 3.`), not normalized to repeated `1.`.

## Git hooks (optional)

If you use git for this repo:

```bash
lefthook install
lefthook run pre-commit
```

`lefthook` installs both the `pre-commit` and `commit-msg` hooks. Use
`uv run soulmap check-links --root . --check-external`
separately when a change edits public URLs and you want live external URL validation.
This repo intentionally does not run a heavy `pre-push` hook. Before pushing, run
`uv run soulmap lint --skip-tests` and
`uv run soulmap test -n auto -q` yourself.

## Versioning

- `pyproject.toml` (`[project].version`) is the canonical project version.
- Do not add or maintain an `Unreleased` section manually. The Release Prep workflow
  runs `uv run cz bump --yes`; Commitizen generates the versioned changelog entry
  from Conventional Commits and updates the project version.
- Edit `CHANGELOG.md` manually only for explicit historical corrections or changes
  to changelog-generation configuration.
- Release versioning follows these intended compatibility levels:
  - Patch: wording fixes and non-breaking detector tweaks.
  - Minor: new frameworks, new detectors, or expanded policies.
  - Major: behavioral breaking changes in safety rules or response structure.
  Let the release workflow perform the actual version bump.

## Skill entrypoint contract

SoulMap has exactly one shipped Skill entrypoint: the root [SKILL.md](SKILL.md).

The `skills/` tree contains supporting canonical knowledge. Do not add nested
`SKILL.md` files there; a nested file would be interpreted as another Claude Skill
and would violate the distribution contract.

Developer-maintenance Skills under `.claude/skills/` are repository tooling and are
not shipped in the SoulMap artifact.

When editing canonical knowledge under `skills/`, preserve the Markdown-first rule:
knowledge lives in Markdown; Python routes, loads, normalizes, validates, and enforces
that knowledge.

## Build contract

After adding or editing any shipped `.md` under `skills/`, rebuild the distribution
artifacts and verify the single-entrypoint contract.

```bash
uv run soulmap build
uv run soulmap dev
uv run soulmap library-manifest
```

- `build` creates both `dist/soulmap-ai.zip` and `dist/soulmap-ai.skill`.
- `dev` verifies both archives against the package contract and refreshes the
  extracted inspection trees under `.soulmap/`.
- `library-manifest` generates the separate Library manifest artifact.

Both archives must preserve exactly one root-level `SKILL.md` entrypoint. The
`.skill` archive additionally preserves `.claude-plugin/`; the standard ZIP does
not. Treat any mismatch as a packaging failure before release.
