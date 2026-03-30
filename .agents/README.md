# Local agent workspace

This folder is the canonical home for repo-local AI workflow assets in SoulMap AI.

It reduces duplication between Claude-facing and Codex-facing layers while keeping
their required entry points intact.

This follows the practical pattern used by multi-tool agent workspaces:

- one shared local workflow layer
- thin tool adapters
- product doctrine kept outside the tool layer

That matches what Claude and Codex each emphasize in different ways:

- Claude uses tool-specific subagent and settings entry paths
- Codex uses portable skills that bundle instructions, resources, and scripts

The stable overlap is:

- shared skills
- shared rules
- shared prompts
- shared hooks
- thin adapters per tool

## What lives here

- shared local rules in [`rules/`](rules/)
- shared local maintenance skills in [`skills/`](skills/)
- shared hook scripts in [`hooks/`](hooks/)
- reusable maintainer prompts in [`prompts/`](prompts/)
- tool-specific adapter material in [`adapters/`](adapters/)

The baseline maintainer prompt for broad repository work is
[`prompts/project-operating-prompt.md`](prompts/project-operating-prompt.md).

## Compatibility model

Claude and Codex still expect their own entry paths.

That is why:

- [`.claude/`](../.claude/) stays as a compatibility layer for Claude-specific loading
- [`.codex/`](../.codex/) stays as a compatibility layer for Codex-specific loading
- both layers should point back to this folder whenever possible

## Internal structure

- `rules/`, shared repo-local editing and workflow rules
- `skills/`, shared maintainer skills
- `prompts/`, reusable maintenance prompts
- `hooks/`, shared shell hooks
- `adapters/`, tool-specific glue such as Claude settings or Codex hook notes

## Which artifact to use

Use the smallest shared artifact that actually matches the problem:

- choose a rule when maintainers should follow the same constraint across many tasks
- choose a skill when the work is recurring and needs a repeatable workflow
- choose a prompt when the task benefits from reusable framing but should not become a
  standing repo rule
- choose an adapter file only when the difference is truly tool-specific

If the same instruction would need to exist in both Claude and Codex layers, it
probably belongs in `.agents/` instead.

## Current note on file paths

The intended long-term shape is for tool-specific settings to live under
`adapters/`.

One Claude settings file also remains available at `.agents/claude/settings.json`
today as a compatibility mirror for existing symlink wiring.

## Boundary

This folder is local workflow infrastructure only.

It does not replace:

- [`AGENTS.md`](../AGENTS.md)
- shipped product knowledge in [`skills/`](../skills/) and [`templates/`](../templates/)
- packaged metadata in [`.claude-plugin/`](../.claude-plugin/)
