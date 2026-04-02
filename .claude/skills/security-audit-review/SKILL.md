---
name: security-audit-review
description: Review SoulMap AI code and workflow changes for practical security risks such as unsafe shell usage, path handling, secrets exposure, and over-broad automation permissions.
---

# Security audit review

Use this skill when reviewing Python, shell, or workflow changes that could introduce
practical security risk in the repository or its local automation.

## Do not use this skill for

- product response-safety doctrine, use
  [`operations-and-safety-review`](../operations-and-safety-review/SKILL.md)
- GitHub workflow implementation details alone, use
  [`github-actions-maintainer`](../github-actions-maintainer/SKILL.md)
- general code cleanup with no security angle, use
  [`code-quality-review`](../code-quality-review/SKILL.md)

## Mission

Catch security issues that matter to this repo's real tooling and automation surfaces.

## Sources to check first

- `../rules/source-character-safety.md`
- `../rules/github-actions.md`
- `docs/engineering/DEV.md`
- `scripts/`
- `src/soulmap/devtools/`
- `.github/workflows/`

## What to look for

- `subprocess` or shell code that broadens command injection risk
- unsafe path joins or missing path validation
- hardcoded credentials, tokens, or copied secrets
- workflow permission changes that exceed actual need
- docs that encourage unsafe local commands or release behavior

## Workflow

1. Read the changed code or workflow with the threat surface in mind.
2. Check whether the repo already has a safer existing pattern.
3. Identify concrete risks, not generic best-practice noise.
4. Fix the risk directly or tighten the docs and automation around it.
5. Add or update tests when the security-sensitive behavior is enforceable.
6. Run the relevant validation commands.

## Expected output

### Findings

List security issues by severity with the practical risk they create.

### Fixes

Summarize the hardening changes.

### Validation

State which tests, lint checks, or workflow checks were run.

## Definition of done

The touched surface should be:

- no less secure than before
- aligned with existing safe patterns in the repo
- free of obvious secret, shell, or permission regressions
- documented honestly when a risk cannot be fully enforced in code
