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
python -m tools.build_skill_zip
```

Bash scripts (macOS/Linux):

```bash
bash scripts/format.sh
bash scripts/lint.sh
bash scripts/build-skill-zip.sh
```

## What gets generated

- `skills/AGENTS.md`: bundled knowledge base Markdown (generated).
- `skills/AGENTS.sources.jsonl`: provenance log for the bundle (generated).
- `dist/soulmap-ai.zip`: distribution artifact (generated).

If you change Markdown under `skills/`, regenerate the bundle:

- `skills/AGENTS.md`

Note: `skills/AGENTS.sources.jsonl` is generated and ignored by git in this repo.

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

2. Keep headings and links GitHub-friendly (the repo runs a Markdown contract check).

3. Regenerate the bundle:

   ```bash
   python -m modules.package_skills
   ```

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
