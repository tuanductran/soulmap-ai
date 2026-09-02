---
name: packaging-maintainer
description: Maintain SoulMap AI packaging and build artifacts so pyproject metadata, dist outputs, build scripts, and shipped-package claims stay in sync. Relevant for changing build outputs, pyproject metadata, or any claim about what ships in the distribution artifacts.
---

# Packaging maintainer

Use this skill when changing build scripts, `pyproject.toml`, `dist/` expectations, or
docs that describe what SoulMap AI ships.

## Do not use this skill for

- release-readiness audits across the whole repo, use
  [`release-readiness-review`](../release-readiness-review/SKILL.md)
- GitHub Actions CI design, use
  [`github-actions-maintainer`](../github-actions-maintainer/SKILL.md)
- pure Markdown knowledge updates with no packaging impact, use
  [`knowledge-base-maintainer`](../knowledge-base-maintainer/SKILL.md)

## Mission

Keep packaging behavior and packaging claims aligned.

## Sources to check first

- `pyproject.toml`
- `docs/engineering/repo-contract.md`
- `docs/engineering/DEV.md`
- `scripts/build-skill.sh`
- `src/soulmap/devtools/packaging/build_skill.py`
- `dist/`

## What to look for

- docs that describe the wrong artifact contents
- stale references to files that are not shipped
- mismatches between build scripts and repo docs
- packaging steps that bypass the current
  `uv run soulmap build` contract
- broken assumptions about skill archives, zip archives, or extracted bundle structure

## Workflow

1. Read the relevant build script, Python build tool, and packaging docs first.
2. Compare claimed artifact contents with what the repo actually builds.
3. Fix the smallest set of files needed to restore packaging consistency.
4. Update tests or contract checks when packaging expectations change.
5. Run the build and validation commands that cover the touched surface.

## Expected output

### Findings

List packaging mismatches, stale claims, or build-surface drift.

### Fixes

Summarize what was synchronized between build logic and docs.

### Validation

State which build or packaging checks passed.

## Definition of done

Packaging should be:

- accurately described
- reproducible with current repo commands
- consistent across scripts, Python tools, and docs
- honest about what is and is not shipped
