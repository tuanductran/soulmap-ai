---
name: code-quality-review
description: Review and improve Python code quality in SoulMap AI so typing, helper usage, exception handling, and repo tooling conventions stay consistent.
---

# Code quality review

Use this skill when reviewing or improving Python implementation quality in `src/`,
compatibility wrappers, `tests/`, or `scripts/`.

## Do not use this skill for

- product doctrine or response-safety review, use
  [`ai-prompt-engineering-safety-review`](../ai-prompt-engineering-safety-review/SKILL.md)
- eval suite design, use [`eval-suite-maintainer`](../eval-suite-maintainer/SKILL.md)
- packaging and release checks, use
  [`packaging-maintainer`](../packaging-maintainer/SKILL.md)

## Mission

Keep Python changes clear, typed, maintainable, and consistent with the repo's existing
tooling contract.

## Sources to check first

- `pyproject.toml`
- `../rules/python-tooling.md`
- `../rules/source-character-safety.md`
- `docs/engineering/DEV.md`
- the target Python files and nearby tests

## What to look for

- stale or duplicated helper logic
- weak typing or type drift against repo conventions
- broad exception handling or hidden failure paths
- dead branches, unused fields, or wrappers that add no value
- speculative validation, sanitization, or fallback logic for a scenario that
  cannot actually occur at that call site; if you cannot name the concrete
  input or state that triggers it, it does not belong in the diff
- local code that should use shared helpers in
  `src/soulmap/runtime/io/cli_payload.py` or
  `src/soulmap/runtime/io/text_normalization.py`
- dead code below the CI dead-code gate's confidence floor, see "Dead code and
  unused-import audits" below

## Dead code and unused-import audits

`uv run vulture` runs in CI at `min_confidence = 80` (`pyproject.toml`), and
Ruff's `F` rules catch unused imports and local variables. Neither is
complete:

- Vulture's own guidance treats 80 as a reasonable floor for automated
  gating, not a claim that nothing real hides below it. A whole-function or
  module-level constant with no caller anywhere in the repo can still score
  60% and pass CI silently.
- `uv run soulmap audit-knowledge` only tracks a fixed set of known
  phrase-list and threshold constant names. A new constant that is not one of
  those is invisible to it even when genuinely orphaned.

When doing a focused dead-code pass (not routine review of a small diff), run:

```bash
uv run vulture src tests scripts --min-confidence 60
```

Triage every hit before touching anything:

- A `TypedDict` or dataclass field flagged as an "unused variable" is almost
  always a false positive: vulture cannot see `case["field"]` or
  `case.get("field")` access elsewhere in the file. Grep the field name for a
  string-key access before assuming it is dead.
- A module-level constant or a private helper function with zero references
  anywhere in the repo (grep the whole tree, not just the same file) is a
  real finding. Delete it in a small, isolated commit.
- Do not lower the committed `min_confidence` in `pyproject.toml` to make CI
  catch more. That trades routine false-positive noise for occasional
  low-confidence finds; a periodic manual pass at a lower confidence, kept
  out of CI, is the correct place for that trade. If a true false positive
  recurs across many files (the `TypedDict` pattern above), prefer
  `vulture --make-whitelist` over lowering the threshold.
- Before deleting anything under `src/soulmap/runtime/experimental/` or
  `src/soulmap/runtime/memory/`, read
  [`docs/engineering/maintenance-boundary.md`](../../../docs/engineering/maintenance-boundary.md)
  first. Both are documented, boundary-tested, deliberately optional modules,
  not orphaned code: "no caller inside `src/soulmap/runtime/routing/` or
  `guards/`" is the intended shape for them, not a defect. A module actually
  being unreferenced by the core is expected there; treat it as a finding
  only if it is also undocumented and untested.

## Workflow

1. Read the target Python files and the closest tests first.
2. Compare the implementation with `pyproject.toml` and `../rules/python-tooling.md`.
3. Identify concrete quality issues that affect clarity, correctness, or maintenance.
4. Make the smallest correct change that improves the code without widening scope.
5. Update tests when the observable contract changes.
6. Run the repo checks needed for the touched files.

## Expected output

### Findings

List the concrete code-quality issues first.

### Fixes

Summarize the changes that improved type safety, helper usage, or readability.

### Validation

State which checks were run and whether they passed.

## Definition of done

The updated code should be:

- simpler or clearer than before
- aligned with repo tooling rules
- free of obvious duplicated logic
- covered by the right tests for the changed behavior
