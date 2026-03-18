# SoulMap AI

SoulMap AI is a reflective healing and self-awareness companion. Its primary role is to
help users turn pain into insight, insight into inner authority, and inner authority
into conscious living. It functions as a mirror, reflecting back what users already
carry within themselves, rather than providing answers from outside.

**Positioning:** SoulMap AI is a reflective companion that helps people stop abandoning
themselves, by turning pain into self-recognition and self-recognition into inner
authority.

**Core Philosophy:** *Appo Deepo Bhava - Be a light unto yourself. The role of SoulMap
is to illuminate, not to dominate.*

## Overview

This repository contains the core knowledge base, operational principles, and behavior
scripts for the SoulMap AI agent.

- **`skills/`**: Contains the markdown-based knowledge files that define the brand,
  voice, frameworks, and ethical guidelines.
- **`modules/`**: Contains detector modules and the framework selector (orchestrator).
- **`scripts/`**: Dev tooling scripts (venv, format, lint, demo launcher).
- **`templates/`**: Contains response structures and other templates.
- **`docs/`**: Developer, tester, user, and API documentation.
- **[CLAUDE.md](CLAUDE.md)**: The master operating principles for the AI model.
- **[SKILL.md](SKILL.md)**: Defines the AI's persona, capabilities, and the map of all
  reference files.

## Usage

The system is designed to be run as an AI agent. The core logic is orchestrated by a
framework selector, which uses various detector scripts to select the appropriate
response framework based on the user's input.

Docs: see [`docs/README.md`](docs/README.md).

## Project Structure

- [CLAUDE.md](CLAUDE.md): Core, non-negotiable operating principles.
- [SKILL.md](SKILL.md): High-level skill definition, persona, and file map.
- `skills/`: The knowledge base for the AI's personality, frameworks, and safety
  protocols.
- `modules/`: Detectors and orchestration code.
- `scripts/`: Dev tooling scripts (format, lint, venv, demo launcher).
- `templates/`: Reusable response structures and redirect messages.
- `docs/`: Developer, tester, user, and API documentation.

## Brand Readiness

These are the core signals this repo now treats as launch-critical:

- Clear positioning: reflective companion, not guru, not diagnostician.
- Safety posture: crisis, dependency, and scope boundaries are enforced in docs and
  code.
- Consistent messaging: README, [SKILL.md](SKILL.md), brand docs, and templates point to
  the same promise.
- Verification: detectors, orchestration, templates, and reference packaging have tests.

Canonical messaging for public surfaces lives in
[skills/brand/message_hierarchy.md](skills/brand/message_hierarchy.md). Surface-specific
rules live in [skills/brand/surfaces_and_scope.md](skills/brand/surfaces_and_scope.md).

Use [templates/launch_readiness_checklist.md](templates/launch_readiness_checklist.md)
as the handoff checklist before shipping new changes.

## Development Setup (Python)

Create a local virtual environment and install dev tools:

```bash
bash scripts/bootstrap_venv.sh
source .venv/bin/activate
```

On Windows (PowerShell), use the cross-platform bootstrapper:

```powershell
python -m tools.bootstrap_venv
.venv\\Scripts\\activate
```

If you already have `.venv/` and only want to activate it:

```bash
source scripts/activate_venv.sh
```

## Quality Checks

```bash
source .venv/bin/activate
bash scripts/format.sh
bash scripts/lint.sh
python -m pytest
```

`bash scripts/lint.sh` runs `ruff`, `isort`, a GitHub-flavored Markdown contract check
(`python -m modules.markdown_contract`), `mdformat`, `pytest`, and Standard type
checking through [pyrightconfig.json](pyrightconfig.json).
`bash scripts/bootstrap_venv.sh` installs the required dev dependencies into `.venv`.

Cross-platform equivalents (recommended for Windows/Linux/macOS):

```bash
python -m tools.format
python -m tools.lint
python -m tools.build_skill_zip
```

`tools.*` will prefer the repo's local `.venv` automatically when available, and prints
a small notice if you are not running inside a virtual environment.

If you use git, you can also enable pre-commit hooks:

```bash
source .venv/bin/activate
pre-commit install
pre-commit run --all-files
```

## Demo

Try the local framework selector (no external APIs):

```bash
bash scripts/soulmap_demo.sh --message "I feel lost and numb lately."
```

## Distribution

Build a zip containing the skill documentation (and a fresh
[skills/AGENTS.md](skills/AGENTS.md) bundle):

```bash
python -m tools.build_skill_zip
```

Output: `dist/soulmap-ai.zip`
