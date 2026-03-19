# Developer Guide

## Overview

This repository is content-first (Markdown knowledge base) with a small Python
orchestrator (`modules/`) and developer tooling (`tools/`, `scripts/`).

## Setup

### macOS/Linux (bash)

```bash
bash scripts/bootstrap_venv.sh
source .venv/bin/activate
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
   id: skills-<area>-<file-stem>
   kind: skills
   version: 1
   ---
   ```

4. For files under `skills/` and `templates/`, set frontmatter `name` to the exact
   filename stem in kebab-case. Example: `skills/brand/brand-doctrine.md` must use
   `name: "brand-doctrine"`.

5. Do not run auto-formatters that rewrite YAML front matter across `skills/` and
   `templates/`. Use `python -m tools.format` or `bash scripts/format.sh` which avoid
   reformatting those folders to prevent structural damage.

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

Trigger it from GitHub: `Actions` -> `Release` -> `Run workflow`.

## Prompt and safety regressions

Use the eval suite for behavior regressions before shipping framework or prompt changes:

```bash
python -m tools.eval_conversations
```
