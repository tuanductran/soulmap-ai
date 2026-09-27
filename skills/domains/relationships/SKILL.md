---
name: "relationships"
description: "Relationship reflection, partnership patterns, attachment-adjacent reflection, and connection themes without turning them into prediction. Use this domain router when the request clearly belongs to this area."
version: "0.12.1"
license: Complete terms in LICENSE
---

# SoulMap relationships domain

## Role

This is a domain routing skill. It points to canonical SoulMap knowledge without
duplicating it.

## Use when

- The conversation clearly belongs to this domain.
- Meta orchestration has already established the response posture.
- A domain-specific framework or knowledge file is needed.

## Do not use when

- Safety, crisis, dependency, or scope handling is the primary concern.
- The request is about brand, voice, orchestration, or runtime implementation.
- Another domain is clearly primary.

## Workflow

1. Start from the central orchestration skill.
2. Load the canonical domain files under `skills/soulmate/`.
3. Apply the domain knowledge without inventing runtime or implementation rules.
5. Return to the response pipeline for voice and safety validation.

## Rules

- Domain skills own meaning and response knowledge.
- Do not add implementation languages, source paths, module names, code examples, or packaging instructions here.
- Use relationship knowledge only after the primary response posture is selected.

## Examples

- A request about grief and self-compassion -> route through the inner-work domain.
- A request about relationship patterns -> route through the relationships domain.
- A symbolic spiritual question -> route through the spirituality domain.

## Edge Cases

- If multiple domains appear, use the domain selected by meta orchestration rather than blending them.
- If the user is emotionally flooded, safety and de-escalation take precedence over domain depth.

## References

- [SKILL.md](../../meta/SKILL.md)
