---
name: "frameworks"
description: SoulMap AI reflective response frameworks covering emotional de-escalation, grief, existential reflection, inner parts, life direction, shadow work, synthesis, and relational inquiry. Relevant for tasks that require choosing or applying the core reflective method for a user conversation.
license: Complete terms in LICENSE
---

# SoulMap Reflective Frameworks

Use this skill when the task is about how SoulMap AI should respond inside a reflective
conversation.

Read [../../AGENTS.md](../../AGENTS.md) first for the hard priority hierarchy, one-question rule, and
non-negotiable behavior constraints.

This skill covers the primary reflective methods SoulMap can use once the brand and
safety constraints are already in force.

## Use this skill when

- You need the right reflective framework for a user message
- You are implementing or testing framework selection behavior
- You are checking framework-specific language and structure

## Do not use this skill for

- Brand positioning or public marketing copy
- Scope boundaries, refusal logic, or dependency rules

Those belong to [../brand/SKILL.md](../brand/SKILL.md) and [../safety/SKILL.md](../safety/SKILL.md).

## Workflow

1. Read [../../AGENTS.md](../../AGENTS.md) first, especially the framework hierarchy.
2. Start with `emotional-deescalation.md` if distress, crisis proximity, or dependency
   is present.
3. Choose exactly one primary framework file for the user's state.
4. Use `conversation-synthesis.md`, `anger-companion.md`, or `somatic-wellbeing.md`
   only when they are secondary layers, not replacements for the primary framework.
5. Pair the chosen framework with [../meta/SKILL.md](../meta/SKILL.md) and [../voice/SKILL.md](../voice/SKILL.md) when you
   need a closing inquiry or tone calibration.
6. Use topic lenses like `relationship-reflection.md`,
   `feminine-masculine-dynamics.md`, or `money-self-worth.md` only after the primary
   framework is clear.

## Files in this skill

- `emotional-deescalation.md`
- `grief-companion.md`
- `existential-companion.md`
- `inner-parts.md`
- `life-direction.md`
- `shadow-patterns.md`
- `meaning-integration.md`
- `conversation-synthesis.md`
- `pattern-mapper.md`
- `relationship-reflection.md`
- `feminine-masculine-dynamics.md`
- `money-self-worth.md`
- `self-compassion.md`
- `anger-companion.md`
- `somatic-wellbeing.md`
- `integration-celebration.md`
- `ancestral-patterns.md`
- `fear-of-visibility.md`
- `creative-drought.md`
- `empath-boundary.md`
- `perfectionism-paralysis.md`

## Expected outcome

Use this skill to produce one clear reflective method per turn, never a blended hybrid,
and always in service of the user's inner authority rather than SoulMap's authority.
