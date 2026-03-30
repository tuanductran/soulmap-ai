# Claude workspace

This folder is a Claude compatibility layer for the shared local agent workspace.

The canonical local workflow source now lives in [`.agents/`](../.agents/).

For broad repository work, start from
[`project-operating-prompt.md`](../.agents/prompts/project-operating-prompt.md).

## Order of precedence

1. `AGENTS.md`
2. shipped product knowledge in `skills/` and `templates/`
3. local workflow rules in `.agents/`, with `.claude/` and `.codex/` as adapters

If a local Claude file conflicts with `AGENTS.md`, preserve `AGENTS.md`.

## What this folder is for

- exposing the paths Claude expects
- pointing Claude to the shared hooks, rules, and skills in `.agents/`
- keeping Claude-specific settings in `.claude/settings.json`

The long-term source for Claude adapter settings is
[`.agents/adapters/claude/`](../.agents/adapters/claude/). A compatibility mirror may
still exist under `.agents/claude/` while local symlink wiring is phased over.

## What this folder is not for

- replacing `AGENTS.md`
- redefining SoulMap doctrine
- storing shipped product knowledge
- creating a second source of truth for brand, safety, or frameworks

## How to use this folder

- keep `AGENTS.md` as the baseline entry point
- use [`.agents/`](../.agents/) as the source of truth for local agent workflow files
- treat `.claude/` as a thin adapter layer only

## Related local layers

- use [`.codex/`](../.codex/) for the Codex compatibility layer
- use [`.claude-plugin/`](../.claude-plugin/) only as packaged skill metadata for
  `.skill` artifacts
