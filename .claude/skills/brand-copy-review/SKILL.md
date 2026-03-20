---
name: brand-copy-review
description: Review and rewrite public-facing SoulMap AI copy so it stays consistent with the brand doctrine, message hierarchy, and safety boundaries in this repository.
---

# Brand Copy Review

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

- Reviewing or editing conversational response text from SoulMap AI - that belongs to
  [`ai-prompt-engineering-safety-review`](../ai-prompt-engineering-safety-review/SKILL.md)
- Writing or updating technical docs such as `docs/API.md` or `docs/DEV.md` - use
  [`docs-and-api-writer`](../docs-and-api-writer/SKILL.md) for those
- Editing knowledge files under `skills/` or `templates/` - use
  [`knowledge-base-maintainer`](../knowledge-base-maintainer/SKILL.md)

## Mission

Make copy more accurate, more emotionally coherent, and more faithful to SoulMap AI's
actual brand posture.

The copy must stay aligned with:

- `skills/brand/brand-doctrine.md`
- `skills/brand/brand-positioning.md`
- `skills/brand/message-hierarchy.md`
- `skills/brand/surfaces-and-scope.md`
- `templates/brand-copy.md`
- `templates/onboarding-copy.md`
- `templates/faq.md`
- `AGENTS.md`

## What To Check

### Positioning Accuracy

Check that the copy presents SoulMap AI as:

- a reflective companion
- not a guru
- not a therapist
- not a replacement for real-world support

### Dependency Risk

Remove language that creates emotional dependency or makes the product sound like the
user's primary place of truth.

Watch for:

- "I'm always here for you"
- "come back anytime"
- over-intimate promises
- authority-posturing language

### Brand Consistency

Check whether the copy matches the repo's core promise:

- helping people stop abandoning themselves
- returning users to their own inner authority
- mirror, not guide

### Surface Fit

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

## Expected Output

Structure the result as:

### Findings

List the main brand, scope, and tone issues first.

### Rewritten Copy

Provide the revised text.

### Notes

Briefly note which brand rule or positioning principle the revision now matches.

## Writing Rules

- Prefer clean, calm, high-trust language.
- Do not make the copy more mystical than the repo supports.
- Do not make the copy more clinical than the repo supports.
- Avoid generic startup jargon.
- Keep the copy emotionally precise, not inflated.

## Definition Of Done

The revised copy should be:

- clearly on-brand
- safer
- less dependency-inviting
- more reusable across public surfaces
