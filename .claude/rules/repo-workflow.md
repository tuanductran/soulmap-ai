---
paths:
  - '**/*'
---

# Repository workflow rules

Use these rules for repository-wide working discipline.

## Sources of truth

- Treat `AGENTS.md` as the baseline SoulMap doctrine, safety contract, and shipped
  package guidance.
- Treat `docs/repo-contract.md` as the repository structure contract.
- Treat `docs/maintenance-boundary.md` as the scope-control document.
- Treat `docs/content-contract.md` as the Markdown structure contract.
- Treat `.claude/rules/language-and-grammar.md` as the repo-local prose style rule.
- Prefer existing repo files over generic assumptions.

## Working style

- Make the smallest correct change first.
- Do not add new surfaces, modules, or docs unless there is a current need.
- Prefer updating existing files over creating parallel ones.
- Keep repo language plain, specific, and ASCII-safe in Markdown.
- Ensure all Markdown updates comply strictly with `.pymarkdown.json` rules, for
  example `MD032` padding around lists and `MD040` fenced code languages.

## Before editing

- Read the nearest source-of-truth file first.
- Check the root `.claude/skills/` directory for a matching skill first.
- Do not change behavior, packaging, or docs by inference alone when the repo already
  defines the contract elsewhere.

## After editing

Run these checks after meaningful changes:

```bash
python -m tools.format
python -m tools.lint
python -m pytest -q
```

If packaging or release behavior changed, also run:

```bash
python -m tools.build_skill
python -m tools.build_skill --skill
```

## AI tool guardrails

- Do not widen scope just because a change is possible.
- Do not invent product capabilities the repo does not implement.
- Do not add dependency-inviting copy, advice-like language, or unsupported claims.
- Do not leave generated caches or build artifacts in the working tree unless they are
  intentionally part of the task.
