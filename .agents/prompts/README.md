# Local agent prompts

This folder contains small reusable prompts for recurring maintenance passes in the
SoulMap AI repository.

These prompts are convenience tools only. They do not replace `AGENTS.md`, `docs/`,
or the shipped knowledge base.

## Prompt guide

- `project-operating-prompt.md`, baseline maintainer prompt and conflict-resolution order for broad repo work
- `master-maintainer.md`, broad repository maintenance and sync passes
- `tester-release.md`, release-style tester and readiness review passes
- `brand-surface-sync.md`, founder-brand and public-surface copy alignment
- `content-graph-audit.md`, `docs/`, `skills/`, and `templates/` discoverability and orphan-file checks
- `docs-skills-templates-sync.md`, shipped knowledge and docs graph sync across entry points
- `packaging-extract-audit.md`, archive honesty, extraction, and build-surface checks
- `security-hardening.md`, shell, workflow, privacy, and disclosure hardening
- `tooling-sync.md`, `pyproject.toml`, dotfiles, bots, `src/`, and `scripts/` sync

## Usage rule

Pick the narrowest prompt that matches the task.

If a task spans multiple layers, start with `project-operating-prompt.md`.

Use `master-maintainer.md` when you want a broad maintenance pass on top of that
baseline.

Only add a more specialized prompt when it clearly reduces drift or review blind spots.
