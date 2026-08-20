# Local agent skills

This folder contains repo-aware local skills for working on SoulMap AI.

> **Important:** Skills here are repo-workflow tools only (code review, docs writing,
> gap analysis). They do not define how SoulMap AI behaves in conversation.
> Product knowledge, frameworks, safety rules, voice, and brand, lives in
> [`../../skills/`](../../skills/), the shipped knowledge base. Internal-only,
> non-shipped product and brand copy lives in [`../../templates/`](../../templates/).

Repository workflow rules live in [`../rules/`](../rules/). Use those files for edit
discipline, quality checks, path-specific conventions, and scope control. Use
`AGENTS.md` for the baseline SoulMap doctrine, safety rules, and shipped package
contract.

## Core review skills

- `ai-prompt-engineering-safety-review`
- `bug-hunt-review`
- `code-quality-review`
- `eval-audit-review`
- `github-actions-maintainer`
- `operations-and-safety-review`
- `security-audit-review`
- `release-readiness-review`
- `webapp-testing-review`

## Product development skills

- `cli-tooling-maintainer`
- `detector-engineer`
- `eval-suite-maintainer`
- `framework-author`
- `packaging-maintainer`
- `property-based-hardening`
- `tooling-performance-review`
- `python-maintainer`
- `testing-strategy-review`

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
- for SoulMap conversational behavior, load files from `skills/` (shipped knowledge
  base) and, for internal-only copy, `templates/`, not from this folder

If you are unsure where to start, begin with `research-and-gap-analysis` or
`release-readiness-review`.

## External patterns adopted selectively

This folder may absorb ideas from strong external skill libraries, but only when they
fill a real SoulMap gap.

Current examples:

- `webapp-testing-review` adapts the reconnaissance, semantic-selector, browser-matrix,
  and rendered-evidence pattern from Anthropic's
  [webapp-testing skill](https://github.com/anthropics/skills/tree/main/skills/webapp-testing)
  to SoulMap's static export, htmx, Alpine, and EN/VI surfaces
- `bug-hunt-review`, `eval-audit-review`, and `property-based-hardening` remain local
  workflow skills whose patterns were selectively shaped by external practice; they
  are listed once above as active local skills

## Shipped product knowledge (not in this folder)

| Need | Where to look |
| :--- | :------------ |
| Response frameworks and companions | `skills/frameworks/` |
| Safety rules and boundaries | `skills/safety/` |
| Brand, voice, and tone | `skills/brand/`, `skills/voice/` |
| Meta guidance and inquiry questions | `skills/meta/` |
| Reusable response and redirect templates (shipped) | `skills/meta/` |
| Internal-only brand and product copy (not shipped) | `templates/` |
| Baseline behavioral contract | `AGENTS.md` |
