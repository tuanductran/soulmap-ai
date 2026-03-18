# Launch Readiness Checklist

Use this checklist before calling SoulMap AI ready for release. This does not mean
"perfect forever." It means the brand, safety posture, and implementation are aligned
enough to ship responsibly.

## 1. Positioning

- The one-sentence positioning is still clear and human-readable.
- SoulMap AI is described consistently as a reflective companion.
- Public-facing copy does not drift into guru, therapist, prophet, or prediction claims.
- The phrase "stop abandoning themselves" remains accurate to the product promise.

## 2. Brand Integrity

- README, [`SKILL.md`](../SKILL.md), and
  [`skills/brand/brand_positioning.md`](../skills/brand/brand_positioning.md) still
  describe the same core promise.
- [`skills/brand/surfaces_and_scope.md`](../skills/brand/surfaces_and_scope.md) still
  cleanly separates live chat rules from public content and internal strategy.
- Templates reflect anti-dependency and return ownership to the user.
- Safety language remains grounded and does not over-promise intimacy or certainty.
- The project still sounds like one brand across docs, prompts, and code comments.

## 3. Safety & Boundaries

- Crisis behavior is still handled before all reflective frameworks.
- Dependency signals still redirect toward real-world support.
- Scope boundaries still decline diagnosis, prediction, and out-of-scope expert advice.
- The one-question rule and non-prescriptive posture are still protected.

## 4. Product Surfaces

- README explains what SoulMap AI is and is not.
- Templates exist for brand copy, redirects, FAQ, response structure, and quick
  reference.
- References bundle generation still works.
- Demo and developer scripts still point to the current workflow.

## 5. Validation

- `python -m pytest` passes.
- `python -m py_compile $(find modules -name '*.py' | sort) $(find tests -name '*.py' | sort)`
  passes.
- Any changed docs have been reviewed for wording drift.
- [`CHANGELOG.md`](../CHANGELOG.md) reflects meaningful project changes.

## Exit Standard

If every section above is true, SoulMap AI is launch-ready for the current release. If
one or more sections fail, treat that as a fix list rather than calling the brand "100%
finished."
