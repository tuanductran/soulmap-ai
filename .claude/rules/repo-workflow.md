---
paths:
  - '**/*'
---

# Repository Workflow Rules

Use these rules for repository-wide working discipline.

## Source Of Truth

- Treat `AGENTS.md` as the primary behavioral and safety contract.
- Treat `docs/repo-contract.md` as the repository structure contract.
- Treat `docs/maintenance-boundary.md` as the scope-control document.
- Treat `docs/content-contract.md` as the Markdown structure contract.
- Prefer existing repo files over generic assumptions.

## Working Style

- Make the smallest correct change first.
- Do not add new surfaces, modules, or docs unless there is a current need.
- Prefer updating existing files over creating parallel ones.
- Keep repo language plain, specific, and ASCII-safe in Markdown.

## Before Editing

- Read the nearest source-of-truth file first.
- Check the root `.claude/skills/` directory for a matching skill first.
- Do not change behavior, packaging, or docs by inference alone when the repo already
  defines the contract elsewhere.

## After Editing

Run these checks after meaningful changes:

```bash
python3 -m tools.format
python3 -m tools.lint
python3 -m pytest -q
```

If packaging or release behavior changed, also run:

```bash
python3 -m tools.build_skill_zip
```

## AI Tool Guardrails

- Do not widen scope just because a change is possible.
- Do not invent product capabilities the repo does not implement.
- Do not add dependency-inviting copy, advice-like language, or unsupported claims.
- Do not leave generated caches or build artifacts in the working tree unless they are
  intentionally part of the task.
