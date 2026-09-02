---
name: brand-copy-review
description: Review and rewrite public-facing SoulMap AI copy so it stays consistent with the brand doctrine, message hierarchy, and safety boundaries in this repository. Relevant for writing or revising public copy, onboarding text, launch material, or any wording that speaks as SoulMap.
---

# Brand copy review

Use this skill when reviewing or rewriting public-facing copy for SoulMap AI.

This includes:

- README messaging
- landing-page copy
- onboarding copy
- FAQ content
- product descriptions
- marketplace descriptions
- founder-brand surfaces

## Do not use this skill for

- Reviewing or editing conversational response text from SoulMap AI, that belongs to
  [`ai-prompt-engineering-safety-review`](../ai-prompt-engineering-safety-review/SKILL.md)
- Writing or updating technical docs such as `docs/engineering/API.md` or
  `docs/engineering/DEV.md`, use
  [`docs-and-api-writer`](../docs-and-api-writer/SKILL.md) for those
- Editing knowledge files under `skills/` (shipped) or `templates/` (internal-only), use
  [`knowledge-base-maintainer`](../knowledge-base-maintainer/SKILL.md)

## Mission

Make copy more accurate, more emotionally coherent, and more faithful to SoulMap AI's
actual brand posture.

The copy must stay aligned with:

- `skills/brand/brand-doctrine.md`
- `skills/brand/brand-positioning.md`
- `skills/brand/message-hierarchy.md`
- `skills/brand/surfaces-and-scope.md`
- `../rules/language-and-grammar.md`
- `templates/brand-copy.md`
- `templates/founder-copy.md`
- `templates/founder-posts.md`
- `templates/marketplace-copy.md`
- `templates/onboarding-copy.md`
- `templates/faq.md`
- `SOULMAP.md`

## What to check

### Positioning accuracy

Check that the copy presents SoulMap AI as:

- a reflective companion
- not a guru
- not a therapist
- not a replacement for real-world support

### Dependency risk

Remove language that creates emotional dependency or makes the product sound like the
user's primary place of truth.

Watch for:

- "I'm always here for you"
- "come back anytime"
- over-intimate promises
- "soulmate AI" or "relationship status" style bonding language
- authority-posturing language

### Brand consistency

Check whether the copy matches the repo's core promise:

- helping people stop abandoning themselves
- returning users to their own inner authority
- mirror, not guide

### Surface fit

Make sure the tone fits the surface.

Examples:

- README can be slightly more technical
- landing copy can be more emotionally resonant
- onboarding must be especially clear about scope and boundaries

### Safety and Scope

Remove claims that imply:

- diagnosis
- prediction
- spiritual certainty
- emotional rescue
- professional authority the product does not have

## Workflow

1. Read the target copy.
2. Cross-check it against the brand files first.
3. Identify the highest-risk misalignments.
4. Rewrite only as much as needed.
5. Keep the language simple, legible, and reusable across surfaces.

## Expected output

Structure the result as:

### Findings

List the main brand, scope, and tone issues first.

### Rewritten copy

Provide the revised text.

### Notes

Briefly note which brand rule or positioning principle the revision now matches.

## Writing rules

- Prefer clean, calm, high-trust language.
- Follow `../rules/language-and-grammar.md` for sentence case, active voice,
  list shape, and SoulMap-safe wording.
- Do not make the copy more mystical than the repo supports.
- Do not make the copy more clinical than the repo supports.
- Avoid generic startup jargon.
- Keep the copy emotionally precise, not inflated.
- If founder copy is rewritten from private source material, keep only rewritten
  patterns and abstractions. Do not include source names, raw excerpts, or identifying
  details.

## Definition of done

The revised copy should be:

- clearly on-brand
- safer
- less dependency-inviting
- more reusable across public surfaces
