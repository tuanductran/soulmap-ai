# Claude Workspace

This folder contains Claude-specific local guidance for working inside the SoulMap AI
repository.

Use it as a supplemental local layer only.

## Order of precedence

1. `AGENTS.md`
2. shipped product knowledge in `skills/` and `templates/`
3. local workflow rules in `.claude/` and `.codex/`

If a local Claude file conflicts with `AGENTS.md`, preserve `AGENTS.md`.

## What this folder is for

- Claude-specific repo workflow notes
- repo-aware maintenance skills under `.claude/skills/`
- path-scoped local rules under `.claude/rules/`
- local hook scripts under `.claude/hooks/`
- Claude tool settings in `.claude/settings.json`

## What this folder is not for

- replacing `AGENTS.md`
- redefining SoulMap doctrine
- storing shipped product knowledge
- creating a second source of truth for brand, safety, or frameworks

## How to use this folder

- keep `AGENTS.md` as the baseline entry point
- use `.claude/rules/` for local edit discipline and repo workflow guardrails
- use `.claude/skills/` for repo maintenance tasks, not SoulMap conversation behavior
- treat `.claude/hooks/` as automation support for the local workflow only

## Related local layers

- use [`.codex/`](../.codex/) for Codex-specific local workflow guidance
- use [`.claude-plugin/`](../.claude-plugin/) only as packaged skill metadata for
  `.skill` artifacts
