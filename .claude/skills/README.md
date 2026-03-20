# Claude Skills

This folder contains repo-aware local skills for working on SoulMap AI.

> **Important:** Skills here are repo-workflow tools only (code review, docs writing,
> gap analysis). They do not define how SoulMap AI behaves in conversation.
> Product knowledge - frameworks, safety rules, voice, and brand - lives in
> [`../../skills/`](../../skills/) and [`../../templates/`](../../templates/),
> which are the shipped knowledge base.

Repository workflow rules live in [`../rules/`](../rules/). Use those files for edit
discipline, quality checks, path-specific conventions, and scope control. Use
`AGENTS.md` for the baseline SoulMap doctrine, safety rules, and shipped package
contract.

## Core review skills

- `ai-prompt-engineering-safety-review`
- `operations-and-safety-review`
- `release-readiness-review`

## Docs and content skills

- `brand-copy-review`
- `docs-and-api-writer`
- `knowledge-base-maintainer`
- `research-and-gap-analysis`
- `workflow-automation-designer`

## How to use this folder

- use one or two skills that match the task
- prefer the smallest correct combination
- treat `AGENTS.md` as the baseline source of truth for SoulMap doctrine and shipped
  package behavior
- for SoulMap conversational behavior, load files from `skills/` and `templates/`
  (shipped knowledge base), not from this folder

If you are unsure where to start, begin with `research-and-gap-analysis` or
`release-readiness-review`.

## Shipped product knowledge (not in this folder)

| Need | Where to look |
| :--- | :------------ |
| Response frameworks and companions | `skills/frameworks/` |
| Safety rules and boundaries | `skills/safety/` |
| Brand, voice, and tone | `skills/brand/`, `skills/voice/` |
| Meta guidance and inquiry questions | `skills/meta/` |
| Reusable templates and quick reference | `templates/` |
| Baseline behavioral contract | `AGENTS.md` |
