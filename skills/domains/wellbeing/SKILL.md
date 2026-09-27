---
name: "wellbeing"
description: "Somatic awareness, emotional de-escalation, grounding, and body-oriented reflective support. Use this domain router when the request clearly belongs to this area."
version: "0.12.1"
license: Complete terms in LICENSE
---

# SoulMap wellbeing domain

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
2. Load the canonical domain files under `skills/frameworks/`.
3. Apply the domain knowledge without inventing runtime or implementation rules.
4. Return to the response pipeline for voice and safety validation.

## Canonical sources

- [somatic-wellbeing](../../skills/frameworks/somatic-wellbeing.md)
- [emotional-deescalation](../../skills/frameworks/emotional-deescalation.md)
- [anger-companion](../../skills/frameworks/anger-companion.md)
- [grief-companion](../../skills/frameworks/grief-companion.md)
- [self-compassion](../../skills/frameworks/self-compassion.md)
- [empath-boundary](../../skills/frameworks/empath-boundary.md)

## Rules

- Use wellbeing frameworks as supportive lenses; safety and crisis boundaries remain higher priority.

## Examples

- A request about grief and self-compassion -> route through the inner-work domain.
- A request about relationship patterns -> route through the relationships domain.
- A symbolic spiritual question -> route through the spirituality domain.

## Edge Cases

- If multiple domains appear, use the domain selected by meta orchestration rather than blending them.
- If the user is emotionally flooded, safety and de-escalation take precedence over domain depth.

## References

- [SKILL.md](../../meta/SKILL.md)
