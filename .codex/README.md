# Codex workspace

This folder is a Codex compatibility layer for the shared local agent workspace.

The canonical local workflow source now lives in [`.agents/`](../.agents/).

For broad repository work, start from
[`project-operating-prompt.md`](../.agents/prompts/project-operating-prompt.md).

Codex-specific adapter notes now live in
[`.agents/adapters/codex/`](../.agents/adapters/codex/).

## Order of precedence

1. `AGENTS.md`
2. shipped product knowledge in `skills/` and `templates/`
3. local workflow rules in `.agents/`, with `.claude/` and `.codex/` as adapters

If a local Codex file conflicts with `AGENTS.md`, preserve `AGENTS.md`.

## What this folder is for

- exposing the paths Codex expects
- pointing Codex to the shared hooks, rules, skills, and prompts in `.agents/`
- keeping Codex-specific wiring discoverable without duplicating the source material

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
- treat [`.agents/`](../.agents/) as the source of truth for shared local workflow files
- keep doctrine, safety, and shipped package truth outside this folder
- keep manual release checks aligned with `.claude/` so `CHANGELOG.md` and other
  release-facing Markdown files go through the same lint gates
- treat `.codex/` as an adapter layer, not as a second doctrine source

## Hook wiring

GitHub Copilot CLI and the coding agent load hook configuration from JSON files in
`.github/hooks/`.

This repo's Codex-facing hook adapter is:

- `.github/hooks/codex-local.json`

That file points into `.agents/hooks/`, where the shared shell scripts now live.
