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
| `.github/` | Repository automation, ownership, and hosting metadata | Local-only repo operations surface | CI workflows, local CI helper actions, Dependabot, CODEOWNERS, funding metadata, and other repository-hosting config | Manual stale-reference review, workflow linting in CI, CODEOWNERS review, and release review |
| `.claude-plugin/` | Local skill-package metadata preserved only in `.skill` artifacts | Local-only packaging metadata | Marketplace metadata and package-only support files | `uv run soulmap build --skill`, extraction checks, and release review |
| `skills/` | Shipped knowledge base content | Shipped | Canonical English frameworks, brand doctrine, safety knowledge, voice and meta references | Markdown contract checks, eval source checks, build smoke, and release review |
| `reference/` | Packaged Markdown locale evidence and optional localized references | Shipped resource data | Human-authored locale phrase evidence and optional localized resource metadata; no doctrine or response content | Markdown contracts, focused detector regression tests, package smoke, and runtime validation |
| `library/` | Versioned Library source catalog | Shipped metadata | Library identity, skill entries, source-of-truth paths, compatibility, and manual distribution boundary; no runtime phrase lists | Library catalog contract tests and release review |
| `templates/` | Internal-only product and brand copy, not shipped | Local-only | Launch checklist, brand, marketing, onboarding, and FAQ copy | Manual stale-reference review; excluded from build packaging |
| `src/soulmap/runtime/` | Canonical executable enforcement, selection, guards, and runtime support | Local runtime source of truth | Detectors, selectors, guards, I/O helpers, memory, synthesis, and experimental modules | Unit tests, evals, compile/lint checks |
| `src/soulmap/runtime/knowledge/soulmate_consumer_scope.json` | Explicit reviewed approval contract for SoulMap consumption of Soulmate skills | Local SoulMap consumer metadata; not Soulmate content | Consumer identity, library compatibility, ordered approved IDs, versions, ranges, and canonical source paths | `scripts/verify_soulmate_consumer_sync.py` and contract tests |
| `src/soulmap/runtime/knowledge/_soulmate_consumer_scope.py` | Deterministic runtime projection of the SoulMap approval contract | Generated local SoulMap metadata; not shipped in Soulmate artifacts | Generated approved skill tuples only; never hand-authored policy or content | Sync verifier parity check, Pyright, and contract tests |
| `src/soulmate/` | Framework-neutral foundation library for future consumers such as SoulMap | Local source boundary; not shipped by current SoulMap AI artifacts | Public contracts, Markdown parsing, text utilities and generic JSON validation only; no SoulMap doctrine, routing state, or protected safety policy | Dedicated import/dependency-direction tests, Pyright, Ruff, and package-boundary review |
| `packages/soulmate/` | Release metadata and Soulmate-only AI skill source boundary | Local Soulmate release/knowledge boundary; not a second Python source tree | Independent package manifest, README, license, foundation and companion skill Markdown, artifact contract, and skill manifest; canonical Python source remains in `src/soulmate/` and is staged explicitly by the Python package builder | Skill manifest/content contracts, deterministic builder, artifact verifier and manual workflow review |
| `dist/soulmate-skills/` | Generated pre-release Soulmate AI skill output | Generated review artifact; not public by default | `soulmate-ai.zip`, byte-identical `soulmate-ai.skill`, projected manifest, provenance, and SHA-256 sidecar produced from the package-owned allow-list | `scripts/build_soulmate_skills.py`, `scripts/verify_soulmate_skills.py`, extraction checks, and release review |
| `src/soulmap/devtools/` | Canonical maintainer tooling package | Local tooling source of truth | CLI entry points, eval runners, packaging helpers, formatting, linting, and shared support helpers | Tooling tests, lint checks, and build smoke |
| `web/` | Public SoulMap website surface | Local static frontend, not shipped Skills content | React/TanStack routes, Tailwind design system, i18n copy, build-time raw-bundle inputs, Playwright checks and GitHub Pages configuration | Locked pnpm install, TypeScript, Vite base-path build, static verifier and browser audit |
| Python wheel/sdist | Local developer and test distribution | Local-only | `soulmap` CLI, `soulmap` runtime/tooling source, the `soulmate` foundation library, repository validation and source files needed for checkout workflows; not a standalone knowledge runtime | `uv build`, metadata inspection, lock checks, and local tooling tests |
| `docs/` | Audience-facing explanation of how the system works and how to operate it | Shipped docs | Contributor, tester, operator, user, architecture, and maintenance docs | Markdown contract checks, including integration doctrine/version metadata, repo-wide linting, and review against repo structure |
| `dist/soulmap-ai.zip` | Standard archive for extraction and document-style AI tooling | Generated release artifact | Packaged `skills/`, root `SKILL.md`, `AGENTS.md`, and `LICENSE`, excluding `.claude-plugin/` and `templates/` (internal-only) | `uv run soulmap build`, extraction checks, and release review |
| `dist/soulmap-ai.skill` | Skill package for skill-oriented tooling | Generated release artifact | Packaged zip contents plus `.claude-plugin/` preserved as-is | `uv run soulmap build --skill`, extraction checks, and release review |
| `dist/soulmap-ai-library.json` | Versioned Library manifest | Generated release artifact | Catalog metadata, project version, release URL, artifact sizes, and SHA-256 digests | `uv run soulmap library-manifest`, Library unit/contract tests, and release review |
| `dist/soulmap-with-soulmate-ai.zip` and `.skill` | Explicit composed AI-facing import surface | Generated pre-release review artifact | Root SoulMap Framework content plus the exact reviewed Soulmate foundation and companion entries under `soulmate/`; no source-only approval metadata | `soulmap build-composed`, `scripts/verify_soulmap_with_soulmate.py`, composition contract tests, and release review |

## Ownership Boundaries

- Baseline doctrine and shipped package guidance live in [../AGENTS.md](../../AGENTS.md).
- Local AI workflow truth lives in `.claude/`.
- Repository automation, hook wiring, and review ownership truth live in `.github/`; `.github/CODEOWNERS` records the maintainer owner for critical surfaces, while branch-protection settings determine whether approval is enforced.
- `.claude-plugin/` holds local skill-package metadata only.
- Shipped knowledge truth lives in `skills/` and is canonical English. Packaged locale evidence lives in `reference/` and must not define doctrine or response content. `library/catalog.json` owns Library distribution metadata; it is not a runtime knowledge source. `templates/` is internal-only and is not shipped.
- Runtime implementation truth lives in `src/soulmap/runtime/`.
- SoulMap's explicit Soulmate consumer approval truth lives in
  `src/soulmap/runtime/knowledge/soulmate_consumer_scope.json`; the checked-in Python
  projection is generated from it and must not be edited manually.
- Framework-neutral foundation implementation truth lives in `src/soulmate/`.
- Tooling implementation truth lives in `src/soulmap/devtools/`.
- Public website implementation truth lives in `web/`; it is not imported by Python and
  is not part of the shipped Skill knowledge surface or custom `.skill`/`.zip` artifacts.
- `gh-pages` is a generated publication branch containing static website output only; it is
  never a source of doctrine, runtime code, or repository documentation.
- Explanatory and operational truth lives in `docs/`.
- The Soulmate manifest's consumer capability declaration is not automatic activation.
  Any SoulMap approval change must be explicit, reviewed, synchronized, and contract-tested;
  the approval JSON and generated projection must remain outside the Soulmate artifact
  allow-list.
- Release artifact truth lives in `dist/soulmap-ai.zip`, `dist/soulmap-ai.skill`,
  `dist/soulmap-ai-library.json`, and the tests that verify them. Soulmate pre-release AI
  artifact truth lives in `dist/soulmate-skills/` and its builder/verifier tests; composed
  SoulMap-on-Soulmate artifact truth lives in `dist/soulmap-with-soulmate-ai/` and its
  composition verifier/tests. Neither is a public registry or live release surface.
- Python wheel/sdist output is local tooling only; it must not be described as the AI Skill
  installation surface. AI-tool imports use the generated `.skill` or `.zip` artifacts.
  Both AI artifacts include the packaged Markdown under `reference/`; source distributions
  include it as well for local runtime and maintenance tooling. The composed artifact has its own
  `soulmate/` namespace and verifier; it does not change the standalone artifact contracts.

## Drift rules

- Document each important repo surface once as the primary source of truth.
- If a file claims that a path, workflow, or artifact exists, that claim must be
  verifiable in the repo.
- If a rule is release-critical, it must be backed by code, tests, evals, or an
  explicit manual-review note.
- Integration guides must declare their canonical doctrine source and exact package
  compatibility in front matter; `markdown-contract` verifies those fields against
  `AGENTS.md` and `pyproject.toml`.
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

Use [`templates/launch-readiness-checklist.md`](../../templates/launch-readiness-checklist.md) (internal-only, not shipped)
as the release gate and [`docs/engineering/safety-enforcement-matrix.md`](safety-enforcement-matrix.md)
as the evidence map for safety claims. For a narrative walkthrough of how the
runtime and `skills/` knowledge base cooperate end to end, including request
flow and layer ownership, see
[`docs/engineering/safety-architecture.md`](safety-architecture.md). For the
canonical reference on intentional architectural limitations and what the
repository does not do by design, see
[`docs/engineering/known-limitations.md`](known-limitations.md).
