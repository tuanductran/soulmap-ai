# Developer Guide

## Overview

This repository is content-first (Markdown knowledge base) with a canonical Python
runtime in `src/soulmap/runtime/`, canonical maintainer tooling in
`src/soulmap/devtools/`.

Use [`repo-contract.md`](repo-contract.md) as the structural source of truth when
working across multiple layers of the repo.

## Setup

### macOS/Linux (bash)

```bash
uv python install 3.11
bash scripts/bootstrap_venv.sh
```

This bootstrap flow also installs the local Git hooks for:

- `lefthook`
- `commit-msg`

This repo uses `uv.lock` as the canonical locked dependency set. To sync the project
directly from the lock file:

```bash
uv sync --locked --python 3.11
```

`uv sync` installs the project in editable mode for local development, so contributor
workflows stay aligned with `pyproject.toml` and `uv.lock`. Activating `.venv` is
optional when you use `uv run ...`.

### Windows (PowerShell)

```powershell
uv python install 3.11
uv run soulmap bootstrap
```

The Windows bootstrap flow also installs the local `lefthook` and `commit-msg`
hooks and syncs dependencies from `uv.lock` on Python 3.11.

## Day-to-day commands

Cross-platform (recommended):

```bash
uv run soulmap format
uv run soulmap markdown-contract --root .
uv run soulmap check-links --root .
uv run soulmap check-case --root .
uv run soulmap lint
uv run soulmap eval-groups
uv run soulmap eval-responses
uv run soulmap build
uv run soulmap build --skill
uv run python tests/eval_regression/test_safety_evals.py
```

Bash scripts (macOS/Linux):

```bash
bash scripts/format.sh
bash scripts/lint.sh
bash scripts/build-skill.sh
```

These shell scripts are convenience wrappers. The Python commands under
`src/soulmap/devtools/cli/` remain the source of truth for bootstrap, formatting,
linting, evals, and build behavior.

## Markdown QA

Use these commands when you want focused Markdown checks without running the full lint
stack:

```bash
uv run soulmap markdown-contract --root .
uv run soulmap check-links --root .
uv run soulmap check-case --root .
```

The contract check guards repo Markdown structure and portability. The local Markdown
link checker validates in-repo files, images, and heading anchors without network
access. The case checker enforces a small SoulMap-specific canonical term table such as
`SoulMap`, `SoulMap AI`, `GitHub`, `Claude`, `Codex`, `Pyright`, `Hypothesis`,
`Ruff`, `lefthook`, and `Markdown`.

`uv run soulmap lint` runs all three checks as part of the standard
quality gate.

For live external URL validation, use the link checker in opt-in mode:

```bash
uv run soulmap check-links --root . --check-external
```

This keeps normal local lint deterministic. External checks use `HEAD` first, fall
back to `GET` when needed, and treat common anti-bot or rate-limit responses such as
`403` and `429` as warnings unless you also pass `--fail-on-warning`.

## What gets generated

- `dist/soulmap-ai.zip`: standard knowledge archive without `.claude-plugin/`.
- `dist/soulmap-ai.skill`: skill package with `.claude-plugin/` preserved.
- `dist/soulmap-ai-library.json`: versioned Library manifest with release metadata and
  SHA-256 digests when `uv run soulmap library-manifest` is used.

For the catalog and manual distribution boundary, see [`operations/LIBRARY.md`](../operations/LIBRARY.md).

## Claude plugin packaging

This repo also ships Claude plugin marketplace metadata:

- `.claude-plugin/marketplace.json`

`uv run soulmap build --skill` preserves `.claude-plugin/` inside
`dist/soulmap-ai.skill`.

## Git hooks (recommended)

```bash
uv run lefthook install
uv run lefthook run pre-commit
```

`lefthook` installs the `pre-commit` and `commit-msg` hooks. The `commit-msg`
hook enforces Conventional Commits via Commitizen (`cz check`).

This repo intentionally does not run a heavy `pre-push` hook. Before pushing, run the
local CI core yourself:

```bash
uv run soulmap lint --skip-tests
uv run soulmap test -n auto -q
```

If you use the repo bootstrap commands above, the commit-time hooks are installed
automatically.

## Pull request autofix

This repo also uses `autofix.ci` in `.github/workflows/ci.yml` to push formatting fixes
back to pull requests after `uv run soulmap format` runs on GitHub Actions.

This requires the `autofix.ci` GitHub App to be installed for the repository. It is a
pull-request convenience layer, not a replacement for local `lefthook` checks or the
main CI quality gates.

## Adding new knowledge files

- Add a new `*.md` under `skills/` (pick the best category folder).
- Use kebab-case filenames (no `_`) and keep headings/links GitHub-friendly (the repo
  runs a Markdown contract check).
- Start the file with YAML front matter metadata.

Use:

```yaml
---
name: "file-stem"
description: "One short sentence describing the full file."
---
```

- For files under `skills/`, set frontmatter `name` to the exact
  filename stem in kebab-case. Example:
  [`../skills/brand/brand-doctrine.md`](../../skills/brand/brand-doctrine.md) must use
  `name: "brand-doctrine"`.
- Use the repo tooling for Markdown changes. `uv run soulmap format` is the canonical
  formatter, and `bash scripts/format.sh` delegates to it on macOS/Linux.
- Before landing Markdown-heavy changes, run the contract check plus the focused local
  link and case checkers so broken anchors or canonical term drift fail early.

## Release and versioning

- Canonical version lives in `pyproject.toml` under `[project].version`.
- Add entries under [`../CHANGELOG.md`](../../CHANGELOG.md) in "Unreleased".

### Automated releases (recommended)

This repo includes a GitHub Actions workflow named `Release` that automates:

- Lint + tests
- Version bump (Commitizen)
- Changelog update (Commitizen)
- Building `dist/soulmap-ai.zip` and `dist/soulmap-ai.skill`
- Creating a GitHub Release and uploading both artifacts

Before triggering a release, review:

- [`templates/launch-readiness-checklist.md`](../../templates/launch-readiness-checklist.md) (internal-only, not shipped)
- [`repo-contract.md`](repo-contract.md)
- [`safety-enforcement-matrix.md`](safety-enforcement-matrix.md)

Trigger it from GitHub: `Actions` -> `Release` -> `Run workflow`.

## Prompt and safety regressions

Use the eval suite for behavior regressions before shipping framework or prompt changes:

```bash
uv run soulmap eval-responses
uv run soulmap eval-groups
uv run python tests/eval_regression/test_safety_evals.py
uv run soulmap test -n auto -q
```

`uv run soulmap eval-groups` is the lightest taxonomy-level guardrail here. It checks
grouped routing expectations from `evals/datasets/groups.json` and validates the referenced
`skills/` policy sources at the same time. For higher-risk slices,
`groups.json` can also define `source_markers` so evals fail if the cited files no
longer contain the expected policy anchor.

## Shared Python helpers

When editing detector CLIs or lightweight module entrypoints, prefer the shared helpers
before adding more local boilerplate:

- [`../../src/soulmap/runtime/io/cli_payload.py`](../../src/soulmap/runtime/io/cli_payload.py) for stdin JSON parsing, JSON
  error output, and common payload extraction helpers such as `message/history`,
  `message/history/memory`, and `message/history/memory/selection`
- [`../../src/soulmap/runtime/io/text_normalization.py`](../../src/soulmap/runtime/io/text_normalization.py) for repeated
  message normalization such as smart-quote cleanup and whitespace collapsing

Do not force every module through the same helper if its payload contract is genuinely
different. In those cases, explicit local code is preferred over a misleading abstraction.

## Format and lint ordering

`uv run soulmap format` and `uv run soulmap lint` now share a repo lock. If they are
started at the same time, one waits instead of failing because files are being rewritten
mid-check. The lock file is cleaned up automatically when the tool exits.

## Local AI workflow layers

Use these helper layers only as local workflow support:

- `.claude/` for the local Claude workflow layer, see
  [../.claude/README.md](../../.claude/README.md)

This layer does not replace [`../AGENTS.md`](../../AGENTS.md), which remains the baseline
SoulMap doctrine and
shipped package contract.

For `.skill` packaging metadata only, see
[../.claude-plugin/README.md](../../.claude-plugin/README.md).

## Orchestration Layer

The shipped knowledge base now includes a central orchestration layer in
`skills/meta/`. Key files added in v0.2+:

- [`../skills/meta/orchestration.md`](../../skills/meta/orchestration.md), decision tree
  and framework priority hierarchy
- [`../skills/meta/execution-pipeline.md`](../../skills/meta/execution-pipeline.md),
  deterministic 7-step pipeline
- [`../skills/meta/framework-template-map.md`](../../skills/meta/framework-template-map.md),
  framework-to-output-structure mapping
- [`../skills/meta/stage-classifier.md`](../../skills/meta/stage-classifier.md), user
  journey stage scoring algorithm
- [`../skills/meta/epistemic-guardrails.md`](../../skills/meta/epistemic-guardrails.md),
  metaphor vs reality enforcement
- [`../skills/meta/observation-seed.md`](../../skills/meta/observation-seed.md), session
  closing seed library
- [`../skills/meta/master-prompt.md`](../../skills/meta/master-prompt.md), production-ready
  system prompt

When editing any of these files, re-run the full eval suite:

```bash
uv run soulmap eval-groups
uv run soulmap eval-responses
uv run python tests/eval_regression/test_safety_evals.py
```
