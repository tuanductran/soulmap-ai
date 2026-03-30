---
name: cli-tooling-maintainer
description: Maintain SoulMap AI command-line tooling so Python entry points, shell wrappers, stdin payload handling, and local automation scripts stay consistent.
---

# CLI tooling maintainer

Use this skill when changing repo tooling exposed through `python -m ...`, shell
scripts under `scripts/`, or stdin-driven helpers in `src/soulmap_runtime/`.

## Do not use this skill for

- GitHub Actions workflow design, use
  [`github-actions-maintainer`](../github-actions-maintainer/SKILL.md)
- packaging artifact review, use
  [`packaging-maintainer`](../packaging-maintainer/SKILL.md)
- general Python refactors with no CLI or tooling surface, use
  [`code-quality-review`](../code-quality-review/SKILL.md)

## Mission

Keep the repo's command-line surfaces predictable, documented, and cross-platform
enough for local development workflows.

## Sources to check first

- `../rules/python-tooling.md`
- `../rules/repo-workflow.md`
- `docs/engineering/DEV.md`
- `scripts/`
- `src/soulmap_devtools/`
- `src/soulmap_runtime/io/cli_payload.py`

## What to look for

- stale command examples or old invocation styles
- shell wrappers that duplicate Python entry-point behavior
- inconsistent stdin payload parsing across tooling modules
- missing or misleading docs for CLI behavior
- exit-code or stderr behavior that would confuse automation

## Workflow

1. Identify the Python entry point or shell wrapper being changed.
2. Compare it with nearby scripts, docs, and tests so command behavior stays aligned.
3. Prefer shared payload parsing and JSON error helpers where the contract matches.
4. Keep shell wrappers thin when Python already owns the logic.
5. Update docs or smoke tests if the command surface changes.
6. Run the relevant repo checks.

## Expected output

### Findings

List mismatches in command behavior, docs, or wrapper layers.

### Fixes

Summarize what was simplified or synchronized.

### Validation

State the commands or tests you ran.

## Definition of done

The tooling surface should be:

- consistent across Python, shell, and docs
- easy to invoke with current repo commands
- free of needless wrapper duplication
- covered by the right smoke or regression checks
