# Codex Prompts

This folder contains small reusable prompts for recurring Codex maintenance passes in
the SoulMap AI repository.

These prompts are convenience tools only. They do not replace `AGENTS.md`, `docs/`,
or the shipped knowledge base.

## Prompt guide

- `master-maintainer.md`, broad repository maintenance and sync passes
- `tester-release.md`, release-style tester and readiness review passes
- `brand-surface-sync.md`, founder-brand and public-surface copy alignment
- `content-graph-audit.md`, `docs/`, `skills/`, and `templates/` discoverability and orphan-file checks
- `docs-skills-templates-sync.md`, shipped knowledge and docs graph sync across entry points
- `packaging-extract-audit.md`, archive honesty, extraction, and build-surface checks
- `security-hardening.md`, shell, workflow, privacy, and disclosure hardening
- `tooling-sync.md`, `pyproject.toml`, dotfiles, bots, `tools/`, and `scripts/` sync

## Usage rule

Pick the narrowest prompt that matches the task.

If a task spans multiple layers, start with `master-maintainer.md` and only add a more
specialized prompt when it clearly reduces drift or review blind spots.
