# Tool adapters

This folder holds tool-specific adapter material for local AI workflows.

Use this structure when more than one AI tool works on the same repository:

- keep shared instructions, skills, hooks, and prompts in the parent
  [`.agents/`](../)
- keep only tool-specific wiring or settings in [`adapters/`](./)
- let [`.claude/`](../../.claude/) and [`.codex/`](../../.codex/) remain thin
  entry layers that point back to these shared assets

## Design rule

There should be one shared workflow layer and many thin adapters.

Do not duplicate doctrine, repo rules, or maintenance skills per tool unless a tool
truly requires a different file format or entry path.

## Current adapters

- [claude/](claude/), Claude-specific settings and adapter notes
- [codex/](codex/), Codex-specific hook and entry-layer notes
