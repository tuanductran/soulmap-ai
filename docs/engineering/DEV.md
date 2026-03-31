# Developer Guide

## Overview

This repository is content-first (Markdown knowledge base) with a canonical Python
runtime in `src/soulmap_runtime/`, canonical maintainer tooling in
`src/soulmap_devtools/`.

Use [`repo-contract.md`](repo-contract.md) as the structural source of truth when
working across multiple layers of the repo.

## Setup

### macOS/Linux (bash)

```bash
bash scripts/bootstrap_venv.sh
source .venv/bin/activate
```

This bootstrap flow also installs the local Git hooks for:

- `lefthook`
- `commit-msg`
- `pre-push`

Or install directly from `pyproject.toml`:

```bash
python -m pip install .
python -m pip install ".[dev]"
```

For contributor workflows, editable install is also supported:

```bash
python -m pip install -e ".[dev]"
```

This project now builds with `hatchling`, so editable installs follow the modern
PEP 660 path rather than generating source-tree `*.egg-info` metadata.

### Windows (PowerShell)

```powershell
python -m soulmap_devtools.cli.bootstrap_venv
.venv\Scripts\activate
```

The Windows bootstrap flow also installs the local `lefthook`, `commit-msg`, and
`pre-push` hooks.

## Day-to-day commands

Cross-platform (recommended):

```bash
python -m soulmap_devtools.cli.format
python -m soulmap_runtime.guards.markdown_contract --root .
python -m soulmap_devtools.cli.check_markdown_links --root .
python -m soulmap_devtools.cli.check_markdown_case --root .
python -m soulmap_devtools.cli.lint
python -m soulmap_devtools.cli.eval_groups
python -m soulmap_devtools.cli.eval_responses
python -m soulmap_devtools.cli.build_skill
python -m soulmap_devtools.cli.build_skill --skill
python tests/eval_regression/test_safety_evals.py
```

Bash scripts (macOS/Linux):

```bash
bash scripts/format.sh
bash scripts/lint.sh
bash scripts/build-skill.sh
```

These shell scripts are convenience wrappers. The Python commands under
`src/soulmap_devtools/cli/` remain the source of truth for bootstrap, formatting,
linting, evals, and build behavior.

## Markdown QA

Use these commands when you want focused Markdown checks without running the full lint
stack:

```bash
python -m soulmap_runtime.guards.markdown_contract --root .
python -m soulmap_devtools.cli.check_markdown_links --root .
python -m soulmap_devtools.cli.check_markdown_case --root .
```

The contract check guards repo Markdown structure and portability. The local Markdown
link checker validates in-repo files, images, and heading anchors without network
access. The case checker enforces a small SoulMap-specific canonical term table such as
`SoulMap`, `SoulMap AI`, `GitHub`, `Claude`, `Codex`, `Pyright`, `Hypothesis`,
`Ruff`, `lefthook`, and `Markdown`.

`python -m soulmap_devtools.cli.lint` runs all three checks as part of the standard
quality gate.

For live external URL validation, use the link checker in opt-in mode:

```bash
python -m soulmap_devtools.cli.check_markdown_links --root . --check-external
```

This keeps normal local lint deterministic. External checks use `HEAD` first, fall
back to `GET` when needed, and treat common anti-bot or rate-limit responses such as
`403` and `429` as warnings unless you also pass `--fail-on-warning`.

## What gets generated

- `dist/soulmap-ai.zip`: standard knowledge archive without `.claude-plugin/`.
- `dist/soulmap-ai.skill`: skill package with `.claude-plugin/` preserved.

## Claude plugin packaging

This repo also ships Claude plugin marketplace metadata:

- `.claude-plugin/marketplace.json`

`python -m soulmap_devtools.cli.build_skill --skill` preserves `.claude-plugin/` inside
`dist/soulmap-ai.skill`.

## Git hooks (recommended)

```bash
source .venv/bin/activate
lefthook install
lefthook run pre-commit
```

`lefthook` installs both the `pre-commit` and `commit-msg` hooks. The `commit-msg`
hook enforces Conventional Commits via Commitizen.

This repo also defines a `pre-push` hook that runs the local CI core:

```bash
python -m soulmap_devtools.cli.lint --skip-tests
python -m pytest -n auto -q
```

If you use the repo bootstrap commands above, these hooks are installed automatically.

## Pull request autofix

This repo also uses `autofix.ci` in `.github/workflows/ci.yml` to push formatting fixes
back to pull requests after `python -m soulmap_devtools.cli.format` runs on GitHub Actions.

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

- For files under `skills/` and `templates/`, set frontmatter `name` to the exact
  filename stem in kebab-case. Example:
  [`../skills/brand/brand-doctrine.md`](../../skills/brand/brand-doctrine.md) must use
  `name: "brand-doctrine"`.
- Use the repo tooling for Markdown changes. `python -m soulmap_devtools.cli.format` is the canonical
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

- [`templates/launch-readiness-checklist.md`](../../templates/launch-readiness-checklist.md)
- [`repo-contract.md`](repo-contract.md)
- [`safety-enforcement-matrix.md`](safety-enforcement-matrix.md)

Trigger it from GitHub: `Actions` -> `Release` -> `Run workflow`.

## Prompt and safety regressions

Use the eval suite for behavior regressions before shipping framework or prompt changes:

```bash
python -m soulmap_devtools.cli.eval_responses
python -m soulmap_devtools.cli.eval_groups
python tests/eval_regression/test_safety_evals.py
python -m pytest -n auto -q
```

`python -m soulmap_devtools.cli.eval_groups` is the lightest taxonomy-level guardrail here. It checks
grouped routing expectations from `evals/datasets/groups.json` and validates the referenced
`skills/` / `templates/` policy sources at the same time. For higher-risk slices,
`groups.json` can also define `source_markers` so evals fail if the cited files no
longer contain the expected policy anchor.

## Shared Python helpers

When editing detector CLIs or lightweight module entrypoints, prefer the shared helpers
before adding more local boilerplate:

- [`../../src/soulmap_runtime/io/cli_payload.py`](../../src/soulmap_runtime/io/cli_payload.py) for stdin JSON parsing, JSON
  error output, and common payload extraction helpers such as `message/history`,
  `message/history/memory`, and `message/history/memory/selection`
- [`../../src/soulmap_runtime/io/text_normalization.py`](../../src/soulmap_runtime/io/text_normalization.py) for repeated
  message normalization such as smart-quote cleanup and whitespace collapsing

Do not force every module through the same helper if its payload contract is genuinely
different. In those cases, explicit local code is preferred over a misleading abstraction.

## Format and lint ordering

`python -m soulmap_devtools.cli.format` and `python -m soulmap_devtools.cli.lint` now share a repo lock. If they are
started at the same time, one waits instead of failing because files are being rewritten
mid-check. The lock file is cleaned up automatically when the tool exits.

## Local AI workflow layers

Use these helper layers only as local workflow support:

- `.agents/` for the shared local agent workflow layer, see
  [../.agents/README.md](../../.agents/README.md)
- `.claude/` for the Claude compatibility layer, see
  [../.claude/README.md](../../.claude/README.md)
- `.codex/` for the Codex compatibility layer, see
  [../.codex/README.md](../../.codex/README.md)

Neither layer replaces [`../AGENTS.md`](../../AGENTS.md), which remains the baseline
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
python -m soulmap_devtools.cli.eval_groups
python -m soulmap_devtools.cli.eval_responses
python tests/eval_regression/test_safety_evals.py
```
