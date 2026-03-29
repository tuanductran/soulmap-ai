# Codex Workspace

This folder contains Codex-specific local guidance for working inside the SoulMap AI
repository.

Use it as a supplemental local layer only.

## Order of precedence

1. `AGENTS.md`
2. shipped product knowledge in `skills/` and `templates/`
3. local workflow rules in `.claude/` and `.codex/`

If a local Codex file conflicts with `AGENTS.md`, preserve `AGENTS.md`.

## What this folder is for

- Codex-specific repo workflow notes
- reusable prompts for maintainer, tester, packaging, security, brand, and tooling passes
- small local rules that make Codex usage more consistent in this repository
- path-scoped rules such as `.codex/rules/github-actions.md` for high-risk edit areas
- local hook scripts under `.codex/hooks/` that mirror the intent of the Claude hook layer

## What this folder is not for

- replacing `AGENTS.md`
- redefining SoulMap doctrine
- storing shipped product knowledge
- creating a second source of truth for brand, safety, or frameworks

## Important note

Do not assume every editor or AI tool will automatically prioritize `.codex/`.

For reliable repo-level behavior:

- keep `AGENTS.md` as the baseline entry point
- treat this folder as a convenience layer for Codex-aware workflows
- keep doctrine, safety, and shipped package truth outside this folder
- keep manual release checks aligned with `.claude/` so `CHANGELOG.md` and other
  release-facing Markdown files go through the same lint gates
- treat `.codex/hooks/` as a Codex adapter layer, not as a second doctrine source

## Hook wiring

GitHub Copilot CLI and the coding agent load hook configuration from JSON files in
`.github/hooks/`.

This repo's Codex-facing hook adapter is:

- `.github/hooks/codex-local.json`

That file points into `.codex/hooks/`, where the shell scripts live.
