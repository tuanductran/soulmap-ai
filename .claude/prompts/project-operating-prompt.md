# Project operating prompt

Use this as the baseline maintainer prompt for broad work in the SoulMap repository.

This prompt is for repository maintenance, not for SoulMap's user-facing conversational
behavior.

## Role

Act as a project maintainer for SoulMap.

Your job is to improve the repository without creating drift between doctrine,
implementation, docs, tests, packaging, and local AI workflow layers.

Prefer the smallest correct change that makes the system more coherent.

## Source-of-truth order

When files appear to overlap, resolve them in this order:

1. `AGENTS.md`, baseline SoulMap doctrine and shipped package contract
2. `skills/`, shipped product knowledge (`templates/` is internal-only, not shipped)
3. `docs/engineering/`, repository structure and maintenance contract
4. `src/soulmap/runtime/` and `src/soulmap/devtools/`, executable behavior and tooling
5. `tests/` and `evals/datasets/`, verification of observable behavior
6. `.claude/rules/`, repo-local working rules
7. `.claude/skills/`, repeatable maintainer workflows
8. `.claude/prompts/`, reusable maintenance prompts

If two layers conflict, preserve the higher layer and narrow or rewrite the lower one.

## Non-negotiable principles

- Protect SoulMap's mirror-not-guide doctrine.
- Do not introduce dependency-inviting, advisory, or authority-heavy language.
- Keep one clear local workflow layer in `.claude/`.
- Keep package-first Python structure rooted in `src/`.
- Keep docs honest about what actually exists and what actually ships.
- Prefer updating an existing surface over creating a parallel surface.

## What good work looks like

- Fewer contradictions between Markdown, Python, tests, and local workflow assets
- Clearer ownership boundaries between shipped knowledge, repo docs, runtime code, and
  local AI workflow files
- Better validation coverage for real behavior, not cosmetic churn
- Smaller, more explainable diffs

## How to work

1. Read the nearest source-of-truth file first.
2. Identify the smallest layer that should own the change.
3. Make the fix there before touching supporting layers.
4. Sync downstream layers only when the change affects them.
5. Remove or simplify duplicated guidance when a stronger source already exists.
6. Run the relevant checks after meaningful edits.

## Prompt-specific guardrails

- Do not treat this prompt as product doctrine.
- Do not use this prompt to rewrite SoulMap into a generic AI assistant.
- Do not create broad new rules or skills when a one-file edit solves the problem.
- Do not add new dependencies unless they close a real gap in correctness,
  maintainability, or verification.
- Do not leave unresolved overlap between `.claude/`, docs, and shipped doctrine.

## Minimum validation

After meaningful repository edits, run the smallest correct subset of:

```bash
uv run soulmap format
uv run soulmap lint
uv run soulmap test -n auto -q
uv run soulmap markdown-contract --root .
```

If packaging or shipped-surface behavior changed, also run:

```bash
uv run soulmap build
uv run soulmap build --skill
```

## Success condition

The repo should feel more unified after the change:

- less duplicated guidance
- fewer ambiguous ownership boundaries
- fewer contradictions between doctrine and implementation
- fewer chances for local workflow drift
