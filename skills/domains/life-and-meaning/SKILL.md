---
name: "life-and-meaning"
description: "Meaning integration, creative drought, visibility, nourishment, direction, and other life-context reflection. Use this domain router when the request clearly belongs to this area."
version: "0.13.0"
license: Complete terms in LICENSE
---

# SoulMap life-and-meaning domain

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

- [existential-companion](../../frameworks/existential-companion.md)
- [meaning-integration](../../frameworks/meaning-integration.md)
- [life-direction](../../frameworks/life-direction.md)
- [creative-drought](../../frameworks/creative-drought.md)
- [fear-of-visibility](../../frameworks/fear-of-visibility.md)
- [soul-nourishment](../../frameworks/soul-nourishment.md)

## Rules

- Choose one primary framework through meta before loading a domain framework.

## Edge Cases

- If multiple domains appear, use the domain selected by meta orchestration rather than blending them.
- If the user is emotionally flooded, safety and de-escalation take precedence over domain depth.

## References

- [SKILL.md](../../meta/SKILL.md)
