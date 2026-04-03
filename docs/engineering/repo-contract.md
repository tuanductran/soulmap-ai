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
| `AGENTS.md` | Baseline SoulMap doctrine, safety law, response behavior, framework priority, and shipped package guidance | Shipped source text for behavior and package use | SoulMap role, safety rules, framework hierarchy, response doctrine, package structure, and optional-local-file guidance | Indirectly verified by `src/soulmap/runtime/`, tests, evals, and docs alignment |
| `.claude/` | Canonical local AI workflow layer for maintainer work | Local-only | Claude README, settings, local hooks, maintainer rules, maintainer skills, and reusable maintainer prompts that stay subordinate to `AGENTS.md` | Markdown contract checks, repo-wide linting, and manual stale-reference review |
| `.github/` | Repository automation and hosting metadata | Local-only repo operations surface | CI workflows, release automation, Dependabot, funding metadata, and other repository-hosting config | Manual stale-reference review, workflow linting in CI, and release review |
| `.claude-plugin/` | Local skill-package metadata preserved only in `.skill` artifacts | Local-only packaging metadata | Marketplace metadata and package-only support files | `uv run soulmap build --skill`, extraction checks, and release review |
| `skills/` | Shipped knowledge base content | Shipped | Frameworks, brand doctrine, safety knowledge, voice and meta references | Markdown contract checks, eval source checks, build smoke, and release review |
| `templates/` | Shipped reusable templates | Shipped | Redirects, quick reference, launch checklist, response structure, brand and FAQ templates | Markdown contract checks, eval source checks, build smoke, and release review |
| `src/soulmap/runtime/` | Canonical executable enforcement, selection, guards, and runtime support | Local runtime source of truth | Detectors, selectors, guards, I/O helpers, memory, synthesis, and experimental modules | Unit tests, evals, compile/lint checks |
| `src/soulmap/devtools/` | Canonical maintainer tooling package | Local tooling source of truth | CLI entry points, eval runners, packaging helpers, formatting, linting, and shared support helpers | Tooling tests, lint checks, and build smoke |
| `docs/` | Audience-facing explanation of how the system works and how to operate it | Shipped docs | Contributor, tester, operator, user, architecture, and maintenance docs | Markdown contract checks, repo-wide linting, and review against repo structure |
| `dist/soulmap-ai.zip` | Standard archive for extraction and document-style AI tooling | Generated release artifact | Packaged `skills/`, `templates/`, root `SKILL.md`, `AGENTS.md`, and `LICENSE`, excluding `.claude-plugin/` | `uv run soulmap build`, extraction checks, and release review |
| `dist/soulmap-ai.skill` | Skill package for skill-oriented tooling | Generated release artifact | Packaged zip contents plus `.claude-plugin/` preserved as-is | `uv run soulmap build --skill`, extraction checks, and release review |

## Ownership Boundaries

- Baseline doctrine and shipped package guidance live in [../AGENTS.md](../../AGENTS.md).
- Local AI workflow truth lives in `.claude/`.
- Repository automation and hook wiring truth live in `.github/`.
- `.claude-plugin/` holds local skill-package metadata only.
- Shipped knowledge truth lives in `skills/` and `templates/`.
- Runtime implementation truth lives in `src/soulmap/runtime/`.
- Tooling implementation truth lives in `src/soulmap/devtools/`.
- Explanatory and operational truth lives in `docs/`.
- Release artifact truth lives in `dist/soulmap-ai.zip`, `dist/soulmap-ai.skill`, and
  the tests that verify them.

## Drift rules

- Document each important repo surface once as the primary source of truth.
- If a file claims that a path, workflow, or artifact exists, that claim must be
  verifiable in the repo.
- If a rule is release-critical, it must be backed by code, tests, evals, or an
  explicit manual-review note.
- `.claude/` is the canonical local workflow layer. It is not part of the shipped archive, but it must still be documented and structurally validated.
- `.github/` is an operational layer, not product doctrine, and should stay aligned
  with the repo's actual checks, release flow, and local hook wiring.
- `.claude-plugin/` is packaging metadata, not product doctrine, and it should only be
  described as part of `.skill` artifacts.

## Release-readiness contract

The repo is release-ready only when all of the following are true:

- important behavior, safety, and operations modules are reflected in docs
- major [../AGENTS.md](../../AGENTS.md) safety rules map to code, tests, evals, or
  explicit guidance-only notes
- `.claude/` files are intentional, current, and contract-checked
- `.github/` workflows and hook wiring, if present, match the repo's actual tooling and
  release flow
- packaging output matches what docs claim ships
- no stale references remain in [../README.md](../README.md), `docs/`, `.claude/`,
  tests, or build notes

Use [`templates/launch-readiness-checklist.md`](../../templates/launch-readiness-checklist.md)
as the release gate and [`docs/engineering/safety-enforcement-matrix.md`](safety-enforcement-matrix.md)
as the evidence map for safety claims.
