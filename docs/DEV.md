# Developer Guide

## Overview

This repository is content-first (Markdown knowledge base) with a small Python
orchestrator (`modules/`) and developer tooling (`tools/`, `scripts/`).

Use [`repo-contract.md`](repo-contract.md) as the structural source of truth when
working across multiple layers of the repo.

## Setup

### macOS/Linux (bash)

```bash
bash scripts/bootstrap_venv.sh
source .venv/bin/activate
```

Or install directly from `pyproject.toml`:

```bash
python -m pip install .
python -m pip install ".[dev]"
```

For contributor workflows, editable install is also supported:

```bash
python -m pip install -e ".[dev]"
```

### Windows (PowerShell)

```powershell
python -m tools.bootstrap_venv
.venv\Scripts\activate
```

## Day-to-day commands

Cross-platform (recommended):

```bash
python -m tools.format
python -m tools.lint
python -m tools.eval_conversations
python -m tools.build_skill_zip
python tests/test_safety_evals.py
```

Bash scripts (macOS/Linux):

```bash
bash scripts/format.sh
bash scripts/lint.sh
bash scripts/build-skill-zip.sh
```

## What gets generated

- `dist/soulmap-ai.zip`: distribution artifact (generated).

## Claude plugin packaging

This repo also ships Claude plugin marketplace metadata:

- `.claude-plugin/marketplace.json`

`python -m tools.build_skill_zip` packages `.claude-plugin/marketplace.json` inside
`dist/soulmap-ai.zip`.

## Pre-commit hooks (recommended)

```bash
source .venv/bin/activate
pre-commit install
pre-commit install --hook-type commit-msg
pre-commit run --all-files
```

The `commit-msg` hook enforces Conventional Commits via Commitizen.

## Adding new knowledge files

1. Add a new `*.md` under `skills/` (pick the best category folder).

2. Use kebab-case filenames (no `_`) and keep headings/links GitHub-friendly (the repo
   runs a Markdown contract check).

3. Start the file with YAML front matter metadata:

   ```yaml
   ---
   name: "file-stem"
   description: "One short sentence describing the full file."
   ---
   ```

4. For files under `skills/` and `templates/`, set frontmatter `name` to the exact
   filename stem in kebab-case. Example: `skills/brand/brand-doctrine.md` must use
   `name: "brand-doctrine"`.

5. Use the repo tooling for Markdown changes. `python -m tools.format` and
   `bash scripts/format.sh` now preserve front matter while applying `pymarkdown`
   consistently across docs, `skills/`, and `templates/`.

## Release and versioning

- Canonical version lives in `pyproject.toml` under `[project].version`.
- Add entries under `CHANGELOG.md` in "Unreleased".

### Automated releases (recommended)

This repo includes a GitHub Actions workflow named `Release` that automates:

- Lint + tests
- Version bump (Commitizen)
- Changelog update (Commitizen)
- Building `dist/soulmap-ai.zip`
- Creating a GitHub Release and uploading the zip

Before triggering a release, review:

- [`templates/launch-readiness-checklist.md`](../templates/launch-readiness-checklist.md)
- [`repo-contract.md`](repo-contract.md)
- [`safety-enforcement-matrix.md`](safety-enforcement-matrix.md)

Trigger it from GitHub: `Actions` -> `Release` -> `Run workflow`.

## Prompt and safety regressions

Use the eval suite for behavior regressions before shipping framework or prompt changes:

```bash
python -m tools.eval_conversations
python tests/test_safety_evals.py
```
