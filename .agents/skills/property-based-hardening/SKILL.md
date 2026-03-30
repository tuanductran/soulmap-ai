---
name: property-based-hardening
description: Use Hypothesis and invariant-driven tests to harden SoulMap AI parsers, normalizers, and small deterministic helpers without creating flaky or slow suites.
---

# Property-based hardening

Use this skill when a Python surface benefits from invariants over example-by-example
tests, especially for parsing, normalization, serialization, and boundary-safe helper
logic.

## Do not use this skill for

- large end-to-end behavior that is clearer as directed examples, use
  [`testing-strategy-review`](../testing-strategy-review/SKILL.md)
- eval dataset authoring, use
  [`eval-suite-maintainer`](../eval-suite-maintainer/SKILL.md)
- general Python cleanup with no invariant question, use
  [`code-quality-review`](../code-quality-review/SKILL.md)

## Mission

Strengthen small but important Python contracts with compact, deterministic
property-based tests that still run cleanly in SoulMap's local and CI workflows.

## Sources to check first

- `pyproject.toml`
- `tests/unit/`
- the helper or parser being hardened
- nearby example-driven tests
- `../rules/python-tooling.md`

## What to look for

- small deterministic functions with clear invariants
- parsers or normalizers that should round-trip or preserve constraints
- example tests that miss obvious edge cases
- Hypothesis strategies that are too broad, slow, or unstable under `pytest -n auto`
- opportunities to shrink a large list of brittle examples into one stronger invariant

## Workflow

1. Name the invariant before writing the strategy.
2. Keep generated inputs bounded and realistic for the touched helper.
3. Reuse existing example tests when they explain intent better than a property.
4. Avoid strategies that create slow, opaque failures or noisy CI runs.
5. Prefer one or two strong invariants over a large test matrix.
6. Run the narrow property test first, then the broader suite if the helper is shared.

## Expected output

### Invariants

State the property being protected in plain language.

### Fixes

Summarize the Hypothesis strategy or helper change that made the contract safer.

### Validation

State which targeted and broad tests were run.

## Definition of done

The hardened surface should be:

- protected by a clear invariant
- fast enough for normal repo workflows
- stable under `pytest -n auto`
- easier to trust than before
