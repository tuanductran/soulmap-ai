# SoulMap AI

SoulMap AI is a reflective companion designed to help people stop abandoning
themselves. It is built as a mirror, not a guide.

## What this repo contains

- `AGENTS.md`: the baseline SoulMap doctrine and package contract
- `skills/` and `templates/`: the knowledge base
- `modules/`: detectors, selector logic, and response safeguards
- `tools/` and `scripts/`: formatting, linting, eval, and packaging workflows
- `docs/`: developer, tester, user, and upload guides

## Core stance

- reflective companion, not guru
- no diagnosis, prediction, or dependency-building
- one active framework at a time
- user independence is the success condition

## Quick start

```bash
bash scripts/bootstrap_venv.sh
source .venv/bin/activate
python -m tools.format
python -m tools.lint
python -m pytest -q
```

## Build

```bash
python -m tools.build_skill
python -m tools.build_skill --skill
```

Outputs:

- `dist/soulmap-ai.zip`: standard knowledge archive without `.claude-plugin/`
- `dist/soulmap-ai.skill`: skill package with `.claude-plugin/` preserved

## Docs

Start here: [`docs/README.md`](docs/README.md)

Structural source of truth: [`docs/repo-contract.md`](docs/repo-contract.md)

## For AI tools

- use [`AGENTS.md`](AGENTS.md) for the baseline SoulMap doctrine, safety rules, and
  shipped package guidance
- use [`.claude/rules/`](.claude/rules/) for repository workflow rules when those files
  are present in the current checkout
- use [`.codex/`](.codex/) as an optional Codex-specific local workflow layer when those
  files are present in the current checkout
- check root [`.claude/skills/`](.claude/skills/) for cross-repo skills
