---
name: "spirituality"
description: "Symbolic and spiritual reflection, discernment, ancestral themes, sacred polarity, and spiritual purpose with explicit epistemic boundaries. Use this domain router when the request clearly belongs to this area."
version: "0.12.1"
license: Complete terms in LICENSE
---

# SoulMap spirituality domain

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
2. Load the canonical domain files under `skills/spiritual/`.
3. Apply the domain knowledge without inventing runtime or implementation rules.
4. Return to the response pipeline for voice and safety validation.

## Canonical sources

- [spiritual/spiritual-discernment](../../spiritual/spiritual-discernment.md)
- [spiritual/symbolic-report-handling](../../spiritual/symbolic-report-handling.md)
- [spiritual/healing-metaphors](../../spiritual/healing-metaphors.md)
- [spiritual/astrology-symbolic-lens](../../spiritual/astrology-symbolic-lens.md)
- [spiritual/tarot-symbolic-lens](../../spiritual/tarot-symbolic-lens.md)
- [spiritual/chakra-affirmations](../../spiritual/chakra-affirmations.md)
- [spiritual/numerology-chakra-policy](../../spiritual/numerology-chakra-policy.md)
- [spiritual/numerology-profile](../../spiritual/numerology-profile.md)
- [spiritual/founder-numerology](../../spiritual/founder-numerology.md)
- [ancestral-patterns](../../frameworks/ancestral-patterns.md)
- [divine-guidance](../../frameworks/divine-guidance.md)
- [sacred-feminine-masculine](../../frameworks/sacred-feminine-masculine.md)
- [spiritual-purpose](../../frameworks/spiritual-purpose.md)
- [dark-night-of-soul](../../frameworks/dark-night-of-soul.md)

## Rules

- Keep spiritual claims framed as tradition, symbolism, Hypothesis, or user meaning rather than fact.


## Edge Cases

- If multiple domains appear, use the domain selected by meta orchestration rather than blending them.
- If the user is emotionally flooded, safety and de-escalation take precedence over domain depth.

## References

- [SKILL.md](../../meta/SKILL.md)
