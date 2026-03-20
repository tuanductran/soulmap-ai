# Repository Contract

This document is the structural source of truth for the SoulMap AI repository.

Use it to answer four questions for every major repo surface:

- what it is for
- whether it ships
- what content belongs there
- how the repo validates it

## Top-Level Contract

| Surface | Purpose | Scope | Allowed content | Validation |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | Baseline SoulMap doctrine, safety law, response behavior, framework priority, and shipped package guidance | Shipped source text for behavior and package use | SoulMap role, safety rules, framework hierarchy, response doctrine, package structure, and optional-local-file guidance | Indirectly verified by `modules/`, tests, evals, and docs alignment |
| `.claude/rules/` | Local workflow rules for contributors and AI tools operating in this repo | Local-only | Repo workflow rules, markdown/tooling rules, git/release rules | `.claude` contract tests and stale-reference checks |
| `.claude/skills/` | Local review and maintenance skills for repo work | Local-only | Repo-aware `SKILL.md` files and local skill index | `.claude` contract tests and stale-reference checks |
| `.codex/` | Optional Codex-specific local workflow helpers | Local-only | Codex README, local rules, and reusable prompts that stay subordinate to `AGENTS.md` | Codex contract tests and stale-reference checks |
| `skills/` | Shipped knowledge base content | Shipped | Frameworks, brand doctrine, safety knowledge, voice and meta references | Metadata tests, markdown contract tests, build artifact tests |
| `templates/` | Shipped reusable templates | Shipped | Redirects, quick reference, launch checklist, response structure, brand and FAQ templates | Metadata tests, markdown contract tests, template coverage tests, build artifact tests |
| `modules/` | Executable enforcement, selection, guards, and repo contracts | Shipped runtime logic | Detectors, selectors, contracts, safety gates, packaging helpers | Unit tests, evals, compile/lint checks |
| `docs/` | Audience-facing explanation of how the system works and how to operate it | Shipped docs | Contributor, tester, operator, user, architecture, and maintenance docs | Markdown contract checks, stale-reference checks, review against repo structure |
| `dist/soulmap-ai.zip` | Standard archive for extraction and document-style AI tooling | Generated release artifact | Packaged `skills/`, `templates/`, root `SKILL.md`, `AGENTS.md`, and `LICENSE`, excluding `.claude-plugin/` | Build artifact tests and zip-content checks |
| `dist/soulmap-ai.skill` | Skill package for skill-oriented tooling | Generated release artifact | Packaged zip contents plus `.claude-plugin/` preserved as-is | Build artifact tests and zip-content checks |

## Ownership Boundaries

- Baseline doctrine and shipped package guidance live in `AGENTS.md`.
- Local AI workflow truth lives in `.claude/`.
- Optional Codex-specific local workflow helpers live in `.codex/`.
- Shipped knowledge truth lives in `skills/` and `templates/`.
- Implementation truth lives in `modules/`.
- Explanatory and operational truth lives in `docs/`.
- Release artifact truth lives in `dist/soulmap-ai.zip`, `dist/soulmap-ai.skill`, and
  the tests that verify them.

## Drift Rules

- Document each important repo surface once as the primary source of truth.
- If a file claims that a path, workflow, or artifact exists, that claim must be
  verifiable in the repo.
- If a rule is release-critical, it must be backed by code, tests, evals, or an
  explicit manual-review note.
- `.claude/` is a first-class local layer. It is not part of the shipped archive, but
  it must still be documented and structurally validated.
- `.codex/` is an optional local layer. It is not part of the shipped archive, and it
  must remain supplemental to `AGENTS.md` rather than becoming a second doctrine source.

## Release-Readiness Contract

The repo is release-ready only when all of the following are true:

- important behavior, safety, and operations modules are reflected in docs
- major `AGENTS.md` safety rules map to code, tests, evals, or explicit guidance-only
  notes
- `.claude/` docs and skills are intentional, current, and contract-checked
- `.codex/` helpers, if present, are intentional, current, and clearly subordinate to
  `AGENTS.md`
- packaging output matches what docs claim ships
- no stale references remain in `README.md`, `docs/`, `.claude/`, tests, or build notes

Use [`templates/launch-readiness-checklist.md`](../templates/launch-readiness-checklist.md)
as the release gate and [`docs/safety-enforcement-matrix.md`](safety-enforcement-matrix.md)
as the evidence map for safety claims.
