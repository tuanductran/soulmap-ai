# Claude workspace

This folder is the repo's local AI workflow layer for Claude-based maintenance work.

For broad repository work, start from
[`prompts/project-operating-prompt.md`](prompts/project-operating-prompt.md).

## Entry point for coding agents

`AGENTS.md` at the repository root is the baseline contract for AI coding agents
working on this codebase: project shape, build and test commands, and workflow
rules. `CLAUDE.md` is a symlink to it, so Claude Code reads the same file as any
other agent. `AGENTS.md` points to `SOULMAP.md` for SoulMap's own product doctrine.

## Order of precedence

1. `SOULMAP.md`, SoulMap's own doctrine, safety rules, and shipped package contract
2. shipped product knowledge in `skills/` (`templates/` is internal-only, not shipped)
3. local workflow files in `.claude/`

If a local Claude file conflicts with `SOULMAP.md`, preserve `SOULMAP.md`.

## What this folder is for

- local hooks in `hooks/`
- repo-local maintainer rules in `rules/`
- repeatable maintainer skills in `skills/`
- reusable maintenance prompts in `prompts/`
- Claude settings in `.claude/settings.json`
- future Claude subagents in `.claude/agents/` when the repo needs true Claude-native
  subagent files

## What this folder is not for

- replacing `SOULMAP.md`
- redefining SoulMap doctrine
- storing shipped product knowledge
- creating a second source of truth for brand, safety, or frameworks

## How to use this folder

- keep `CLAUDE.md` (a symlink to `AGENTS.md`) as the Claude entry point and
  `SOULMAP.md` as the baseline doctrine
- treat `.claude/` as supplemental local workflow support
- keep doctrine, safety, and shipped package truth outside this folder

## Claude-native surfaces

Claude Code officially reads these project-level surfaces directly:

- `CLAUDE.md`, a symlink to `AGENTS.md`
- `.claude/settings.json`
- `.claude/settings.local.json` when present and intentionally local-only
- `.claude/agents/*.md` when the repo defines Claude subagents

The repo's `hooks/`, `rules/`, `prompts/`, and `skills/` folders under `.claude/` are
still useful, but they are supporting files rather than Claude Code-native entry
points.

## Related local layers

- use [`.claude-plugin/`](../.claude-plugin/) only as packaged skill metadata for
  `.skill` artifacts
