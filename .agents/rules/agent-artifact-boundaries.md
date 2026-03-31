---
paths:
  - .agents/**/*.md
  - .claude/**/*.md
  - .codex/**/*.md
  - AGENTS.md
---

# Agent artifact boundaries

Use a clear split between shared agent artifacts and tool-specific adapters.

When there is uncertainty about ownership or precedence, start from
`.agents/prompts/project-operating-prompt.md`.

- put stable repo-wide guidance in `.agents/rules/`
- put repeatable maintainer workflows in `.agents/skills/`
- put reusable task prompts in `.agents/prompts/`
- keep `.agents/adapters/` thin, tool-specific, and free of duplicate doctrine
- keep shipped product behavior in `AGENTS.md`, `skills/`, and `templates/`, not in
  local workflow adapters
- when the same guidance would need to be copied into Claude and Codex layers, move it
  into `.agents/` instead and let the adapters point back to it
- do not create a new skill when a rule plus an existing skill already covers the task
- do not create a new rule for one-off work that belongs in a prompt or a task-local edit
- do not let a prompt become a second source of truth for doctrine or repo structure
- do not vendor external skills wholesale just because they are popular, extract only
  the part that closes a real SoulMap gap
- when adapting an outside skill, rewrite it in SoulMap terms so it matches the
  repo's structure, command flow, and doctrine boundaries
- if a new file changes how maintainers work across the repo, it is probably a rule
- if a new file teaches the agent how to perform a recurring task, it is probably a skill
- if a new file mostly helps frame a category of work without changing repo-wide
  policy, it is probably a prompt
- if the file only exists because Claude or Codex needs a different entry path, it is
  probably adapter material and should stay thin
