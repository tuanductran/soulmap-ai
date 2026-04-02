# Claude workspace

This folder is the repo's local AI workflow layer for Claude-based maintenance work.

For broad repository work, start from
[`prompts/project-operating-prompt.md`](prompts/project-operating-prompt.md).

## Order of precedence

1. `AGENTS.md`
2. shipped product knowledge in `skills/` and `templates/`
3. local workflow files in `.claude/`

If a local Claude file conflicts with `AGENTS.md`, preserve `AGENTS.md`.

## What this folder is for

- local hooks in `hooks/`
- repo-local maintainer rules in `rules/`
- repeatable maintainer skills in `skills/`
- reusable maintenance prompts in `prompts/`
- Claude settings in `.claude/settings.json`
- future Claude subagents in `.claude/agents/` when the repo needs true Claude-native
  subagent files

## What this folder is not for

- replacing `AGENTS.md`
- redefining SoulMap doctrine
- storing shipped product knowledge
- creating a second source of truth for brand, safety, or frameworks

## How to use this folder

- keep `CLAUDE.md` as the Claude entry point and `AGENTS.md` as the baseline doctrine
- treat `.claude/` as supplemental local workflow support
- keep doctrine, safety, and shipped package truth outside this folder

## Claude-native surfaces

Claude Code officially reads these project-level surfaces directly:

- `CLAUDE.md`
- `.claude/settings.json`
- `.claude/settings.local.json` when present and intentionally local-only
- `.claude/agents/*.md` when the repo defines Claude subagents

The repo's `hooks/`, `rules/`, `prompts/`, and `skills/` folders under `.claude/` are
still useful, but they are supporting files rather than Claude Code-native entry
points.

## Related local layers

- use [`.claude-plugin/`](../.claude-plugin/) only as packaged skill metadata for
  `.skill` artifacts
