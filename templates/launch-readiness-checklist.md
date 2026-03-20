---
name: "launch-readiness-checklist"
description: "Launch readiness checklist for brand and safety."
---

# Launch Readiness Checklist

Use this checklist before calling SoulMap AI ready for release. This does not mean
"perfect forever." It means the brand, safety posture, and implementation are aligned
enough to ship responsibly.

Use [`docs/repo-contract.md`](../docs/repo-contract.md) as the structure contract and
[`docs/safety-enforcement-matrix.md`](../docs/safety-enforcement-matrix.md) as the
evidence map for safety claims.

## Verification Map

| Area | Evidence type | Primary evidence |
| --- | --- | --- |
| Repository structure and ownership | Doc and contract test | `docs/repo-contract.md`, `tests/test_claude_contract.py` |
| `.claude/` workflow layer | Contract test | `tests/test_claude_contract.py` |
| Shipped knowledge and templates | Metadata, markdown, and build tests | `tests/test_skill_metadata_contract.py`, `tests/test_markdown_contract.py`, `tests/test_build_artifacts.py` |
| Runtime safety and selector priority | Unit tests and evals | `tests/test_framework_selector_priorities.py`, `tests/test_response_safety_gate.py`, `tests/test_safety_evals.py` |
| Packaging output | Build and artifact test | `python -m tools.build_skill`, `python -m tools.build_skill --skill`, `tests/test_build_artifacts.py` |
| Manual release review | Explicit reviewer pass | `CHANGELOG.md`, changed docs, and public-facing copy review |

## Positioning

- The one-sentence positioning is still clear and human-readable.
- SoulMap AI is described consistently as a reflective companion.
- Public-facing copy does not drift into guru, therapist, prophet, or prediction claims.
- The phrase "stop abandoning themselves" remains accurate to the product promise.

## Brand Integrity

- README, [`skills/brand/SKILL.md`](../skills/brand/SKILL.md), and
  [`skills/brand/brand-positioning.md`](../skills/brand/brand-positioning.md) still
  describe the same core promise.
- [`skills/brand/surfaces-and-scope.md`](../skills/brand/surfaces-and-scope.md) still
  cleanly separates live chat rules from public content and internal strategy.
- Templates reflect anti-dependency and return ownership to the user.
- Safety language remains grounded and does not over-promise intimacy or certainty.
- The project still sounds like one brand across docs, prompts, and code comments.

## Safety & Boundaries

- Crisis behavior is still handled before all reflective frameworks.
- Dependency signals still redirect toward real-world support.
- Scope boundaries still decline diagnosis, prediction, and out-of-scope expert advice.
- The one-question rule and non-prescriptive posture are still protected.

## Product Surfaces

- README explains what SoulMap AI is and is not.
- Templates exist for brand copy, redirects, FAQ, response structure, and quick
  reference.
- `docs/repo-contract.md` still matches the actual repo shape.
- `docs/safety-enforcement-matrix.md` still reflects current code and test coverage.
- References bundle generation still works.
- Demo and developer scripts still point to the current workflow.

## Validation

- `python -m pytest -q` passes.
- `python -m py_compile $(find modules -name '*.py' | sort) $(find tests -name '*.py' | sort)`
  passes.
- `tests/test_claude_contract.py` passes.
- Any changed docs have been reviewed for wording drift.
- [`CHANGELOG.md`](../CHANGELOG.md) reflects meaningful project changes.
- Release notes, docs, and packaging still describe the same shipped assets.

## Exit Standard

If every section above is true, SoulMap AI is launch-ready for the current release. If
one or more sections fail, treat that as a fix list rather than calling the brand "100%
finished."
