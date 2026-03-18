# Scripts

This folder contains developer tooling scripts (bash) for working on this repo.

Detector and orchestrator code lives in `modules/` and is standard-library-only.

## Quickstart

```bash
bash scripts/bootstrap_venv.sh
source .venv/bin/activate
```

On Windows (PowerShell):

```powershell
python -m tools.bootstrap_venv
.venv\\Scripts\\activate
```

After the virtual environment exists, treat `source .venv/bin/activate` as the default
first step before running any project command.

## Quality Checks

```bash
source .venv/bin/activate
bash scripts/format.sh
bash scripts/lint.sh
python -m pytest
```

`bash scripts/lint.sh` runs Python linting, formatting checks, Markdown formatting
checks, a GitHub-flavored Markdown contract check
(`python -m modules.markdown_contract`), tests, and Standard type checking via `pyright`
when it is installed in `.venv`.

Cross-platform equivalents (recommended for Windows/Linux/macOS):

```bash
python -m tools.format
python -m tools.lint
python -m tools.build_skill_zip
```

## Run a detector

Most detectors accept JSON via stdin.

```bash
source .venv/bin/activate
echo '{"message":"I feel lost and numb lately."}' | python -m modules.grief_detector
```

## Run the orchestrator

[`modules/framework_selector.py`](../modules/framework_selector.py) runs all detectors,
applies the priority hierarchy, and returns exactly one `primary_framework` (plus
optional `secondary_layer`).

```bash
source .venv/bin/activate
echo '{"message":"I feel lost and numb lately.","history":[{"role":"user","content":"I feel lost and numb lately."}],"memory":{}}' | python -m modules.framework_selector
```

## Demo CLI

```bash
source .venv/bin/activate
bash scripts/soulmap_demo.sh --message "I feel lost and numb lately."
```

## Build the Skills Bundle

Generate [`skills/AGENTS.md`](../skills/AGENTS.md) from all Markdown under `skills/`:

```bash
source .venv/bin/activate
python -m modules.package_skills
```

Exclude patterns (relative to `skills/`) can be added to `.skillsignore`.

## Build a Distribution Zip

Create `dist/soulmap-ai.zip` containing the skill docs:

```bash
source .venv/bin/activate
python -m tools.build_skill_zip
```
