---
name: "launch-readiness-checklist"
description: "Launch readiness checklist for brand and safety."
---

# Launch Readiness Checklist

Use this checklist before calling SoulMap AI ready for release. This does not mean
"perfect forever." It means the shipped knowledge files are aligned enough to use
responsibly.

## Verification Map

| Area | Evidence type | Primary evidence |
| --- | --- | --- |
| Package entry points | File review | `AGENTS.md`, `SKILL.md`, `templates/SKILL.md` |
| Brand alignment | Content review | `skills/brand/` and `templates/brand-copy.md` |
| Safety alignment | Content review | `AGENTS.md`, `skills/safety/`, `templates/redirect-templates.md` |
| Framework coverage | Content review | `skills/frameworks/` and `templates/quick-reference.md` |
| Voice alignment | Content review | `skills/voice/` and `templates/response-structure.md` |
| Archive self-containment | Path review | shipped files do not depend on missing repo-only paths |

## Positioning

- The one-sentence positioning is still clear and human-readable.
- SoulMap AI is described consistently as a reflective companion.
- Public-facing copy does not drift into guru, therapist, prophet, or prediction claims.
- The phrase "stop abandoning themselves" remains accurate to the product promise.

## Brand Integrity

- [`skills/brand/SKILL.md`](../skills/brand/SKILL.md) and
  [`skills/brand/brand-positioning.md`](../skills/brand/brand-positioning.md) still
  describe the same core promise.
- [`skills/brand/surfaces-and-scope.md`](../skills/brand/surfaces-and-scope.md) still
  cleanly separates live chat rules from public content and internal strategy.
- Templates reflect anti-dependency and return ownership to the user.
- Safety language remains grounded and does not over-promise intimacy or certainty.
- The package still sounds like one brand across skills and templates.

## Safety & Boundaries

- Crisis behavior is still handled before all reflective frameworks.
- Dependency signals still redirect toward real-world support.
- Scope boundaries still decline diagnosis, prediction, and out-of-scope expert advice.
- The one-question rule and non-prescriptive posture are still protected.

## Product Surfaces

- Templates exist for brand copy, redirects, FAQ, response structure, and quick
  reference.
- The root files still explain what SoulMap AI is and how to use the package.
- The shipped directories still match the guidance described in `AGENTS.md`.
- No template points to missing repo-only files unless they are intentionally bundled.

## Validation

- `AGENTS.md`, `SKILL.md`, `skills/`, and `templates/` describe the same package.
- Relative links inside shipped files resolve to files that are actually present.
- Public copy stays aligned with the mirror-not-guide stance.
- Safety wording still declines diagnosis, prediction, and dependency-building.
- The package remains useful after extraction without requiring repo-only context.

## Exit Standard

If every section above is true, SoulMap AI is launch-ready for the current release. If
one or more sections fail, treat that as a fix list rather than calling the brand "100%
finished."
