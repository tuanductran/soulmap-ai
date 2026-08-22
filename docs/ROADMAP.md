# SoulMap AI - Project Roadmap

> **Repository:** [soulmap-ai](https://github.com/tuanductran/soulmap-ai)
> **Maintainer:** Tuan Duc Tran
> **License:** see [LICENSE](../LICENSE)
> **Status:** Actively maintained, v0.9.0 baseline; post-v0.9.0 roadmap in execution
> **Last updated:** 21 August 2026

This roadmap describes the long-term direction, architecture evolution, and engineering
priorities of SoulMap AI.

SoulMap AI is a content-first knowledge base - a reflective-companion AI system - with a
small Python enforcement and tooling layer on top. The repository's discipline is stated
in [AGENTS.md](../AGENTS.md) and [README.md](../README.md): brand, safety, packaging, and
implementation must always tell one consistent story.

For the current rule-by-rule enforcement status, always refer to:

* `docs/engineering/safety-enforcement-matrix.md`

For intentional architecture boundaries that are not bugs, refer to:

* `docs/engineering/known-limitations.md`

For active implementation tasks, milestones, and execution tracking:

* GitHub Issues

---

## Table of Contents

1. [Project Vision](#project-vision)
2. [Repository Overview](#repository-overview)
3. [Architecture](#architecture)
4. [Development Phases](#development-phases)
5. [Next Phase Plan](#next-phase-plan)
6. [Validation and Quality System](#validation-and-quality-system)
7. [CI/CD and Automation](#cicd-and-automation)
8. [Future Direction](#future-direction)
9. [Success Metrics](#success-metrics)
10. [Glossary](#glossary)

---

## Project Vision

### A Bounded, Anti-Dependency Reflective Companion

SoulMap AI aims to be a reflective companion that helps people hear themselves more
clearly without handing their authority away. The project follows the principle stated
in [README.md](../README.md):

> Mirror-first, not advice-first.

Every framework, safety rule, and detector is treated as a maintainable artifact with:

* canonical English Markdown as the source of truth for shipped knowledge and doctrine
* narrowly scoped, human-authored locale evidence under `reference/languages/`
* a thin, deterministic Python layer for routing, safety gating, packaging, and locale evidence loading
* automated eval regression (`eval-groups`, `eval-markdown-contracts`, `eval-responses`)
* explicit Architecture Decision Records for anything safety-adjacent
* multi-platform distribution (Claude, ChatGPT, Gemini, Poe)

The goal is not to maximize AI authority or engagement, but to protect user independence
as the actual success condition.

---

## Repository Overview

SoulMap AI ships a knowledge base covering:

* Frameworks - grief, life direction, shadow patterns, inner parts, anger, existential
  companion, perfectionism paralysis, empath boundary, creative drought, somatic
  wellbeing, emotional de-escalation, pattern mapper, dark night of the soul, soul
  nourishment, divine guidance, sacred polarity, and spiritual purpose
* Spiritual discernment - bypass detection, grounded reflective framing
* Safety - crisis detection, dependency detection, boundaries, whitelist/blacklist
* Meta - master prompt, orchestration, response and redirect templates

Content is distributed through:

* Claude Skills (`dist/soulmap-ai.skill`)
* Direct knowledge archive (`dist/soulmap-ai.zip`)
* ChatGPT Custom GPT, Gemini, and Poe instruction sets (`docs/integrations/`)

---

## Architecture

### Technology Stack

| Layer              | Technology                              |
| ------------------ | ---------------------------------------- |
| Runtime            | Python 3.11+                             |
| Package manager    | uv                                        |
| Build backend       | Hatchling                                 |
| Validation         | Deterministic regex/substring detectors   |
| Formatter / Linter | Ruff                                      |
| Type checking      | Pyright (standard mode)                   |
| Markdown Quality   | pymarkdownlnt                             |
| Testing            | pytest, pytest-xdist, pytest-randomly, Hypothesis |
| Dead code detection | Vulture                                  |
| Dependency Updates | Dependabot                                |
| CI                 | GitHub Actions (`ci.yml`, `autofix.yml`, `codeql.yml`, `release.yml`) |

---

### Repository Structure

```text
soulmap-ai/
│
├── AGENTS.md
│   └── Baseline doctrine, safety law, response behavior, package contract
│
├── SKILL.md
│   └── Top-level shipped package entry point
│
├── reference/
│   └── languages/        Packaged human-authored locale evidence
│
├── library/
│   └── catalog.json      Versioned Library source catalog
│
├── .claude/
│   └── Local maintainer workflow layer (not shipped)
│
├── .claude-plugin/
│   └── Skill-package metadata (preserved only in `.skill`)
│
├── skills/
│   ├── frameworks/       Reflective frameworks (grief, anger, existential, ...)
│   ├── spiritual/        Spiritual discernment and bypass detection content
│   ├── safety/           Boundaries, whitelist/blacklist doctrine
│   └── meta/             Master prompt, orchestration, response/redirect templates
│
├── src/soulmate/
│   ├── contracts/        Framework-neutral public contracts
│   ├── data/             Framework-neutral JSON parsing and field validation
│   ├── knowledge/        Foundation knowledge interfaces and Markdown parser
│   ├── pipeline/         Framework-neutral lifecycle primitives
│   ├── resources/        Explicit resource resolution boundary
│   └── text/             Framework-neutral text normalization utilities
│
├── packages/soulmate/
│   ├── pyproject.toml    Release-only package metadata
│   ├── README.md         Package identity and release boundary
│   ├── LICENSE           Package license copy
│   └── skills/           Soulmate-only foundation skill source and manifest
│
├── src/soulmap/
│   ├── runtime/
│   │   ├── detectors/    Per-signal detection modules (anger, crisis, pattern, ...)
│   │   ├── routing/      Framework selector
│   │   ├── guards/       Response/markdown/resource contract validation
│   │   ├── knowledge/    Markdown-backed loaders (protected-module policy)
│   │   ├── config/       Static safety config (multilingual crisis packs)
│   │   ├── memory/       Experimental memory ledger
│   │   └── experimental/ Experimental modules (biometric ingest, demo)
│   ├── web/              Python-only public website and static export surface
│   └── devtools/
│       ├── audit/        Knowledge-usage audit (audit-knowledge)
│       ├── evals/        eval-groups, eval-markdown-contracts, eval-responses
│       └── cli/          format, lint, test, build, check-links, check-case
│
├── tests/
│   ├── (per-detector unit tests)
│   ├── contract/         Response/markdown contract tests
│   ├── integration/       Framework selector priority tests
│   └── eval_regression/   Safety eval regression tests
│
├── evals/datasets/       Grouped routing and response-safety eval datasets
│
├── docs/
│   ├── engineering/      Architecture, ADRs, safety matrix, known limitations
│   ├── operations/       Privacy, operations, regulatory, upload
│   ├── product/          User-facing product doc
│   └── integrations/      Per-platform deployment guides
│
├── .github/
│   ├── CODEOWNERS        Maintainer ownership and review map
│   ├── actions/          Pinned local CI helper actions
│   ├── dependabot.yml    uv and GitHub Actions update policy
│   └── workflows/        ci.yml, autofix.yml, codeql.yml, release.yml,
│                         website-pages.yml
```

---

### Detection & Safety Architecture

Each detector follows a structured, source-backed format:

```text
skills/frameworks/<framework>.md   → "## Detection signals" (canonical English source)
reference/languages/<locale>/      → reviewed runtime-only locale evidence where needed
src/soulmap/runtime/detectors/<framework>_detector.py  → loads + scores signals
tests/test_<framework>_detector.py  → unit coverage of the loaded signals
evals/datasets/groups.json          → grouped end-to-end routing coverage
```

Crisis and dependency detection are treated as protected modules: they are not
Markdown-loaded like other detectors, by explicit policy (see
[`docs/engineering/adr/0001-layered-crisis-detection.md`](../docs/engineering/adr/0001-layered-crisis-detection.md)).
Any change to this layer requires an ADR and full eval-suite evidence, not just a
passing test.

The maturity/enforcement state of every safety rule is tracked in:

```text
docs/engineering/safety-enforcement-matrix.md
```

---

## Development Phases

### Phase 1 - Foundation (v0.1.0)

Completed:

* Initial doctrine and package contract (`AGENTS.md`)
* First shipped skill package structure
* Core safety templates - crisis and dependency hotlines embedded in
  boundaries-safety, ethics-safety, and redirect templates
* Local vs shipped skill boundary clarified (`.claude/`)

---

### Phase 2 - QA Hardening & Grouped Eval Harness (v0.2.0)

Completed:

* Grouped, source-backed eval harness (`evals/datasets/groups.json`,
  `eval-groups` wired into CI/release)
* Scope hardening against substring false positives and gradual-pressure,
  AI-identity, ambiguous-distress, spiritual-manipulation red-team cases
* Shared Python helpers centralized (text normalization, CLI payload helpers,
  static detector phrase lists)
* `--zip`, `--skill`, `--all` build flags
* Claude Code hooks for local workflow automation
* Detector keyword coverage and routing hardened (Battery 1: 8/20 → 20/20)
* Full GitHub Markdown compliance and CI workflow hardening (autofix.yml split
  from ci.yml, CodeQL concurrency guard)

---

### Phase 3 - Content Gap Closure & Central Orchestration (v0.3.0)

Completed:

* Central orchestration layer and execution pipeline (`skills/meta/orchestration.md`)
* First-session contract, shift markers, observation seeds, synthesis-on-demand
* 5 new frameworks from content gap analysis; remaining 11% production-readiness
  gaps closed
* Markdown/Python blacklist and whitelist synchronized
* 4 morphological gaps patched in crisis detection
* Detector configs split by domain (`modules/config/`)
* Cross-platform test path normalization

---

### Phase 4 - Brand & Numerology Enrichment (v0.4.x)

Completed:

* ICP and founder story enriched from a personal-numerology lens
* Technical implementation details removed from user-facing skills/templates
  (content/implementation separation)
* CI hardening for manual release Markdown checks
* Repo-root resolution fixed for checkout-workspace CI runs

---

### Phase 5 - Framework Expansion & QA Closure (v0.5.x)

Completed:

* 5 additional frameworks shipped
* Dependency and tooling upgrades stabilized (Ruff, Pyright, Hypothesis, lefthook,
  commitizen)
* Markdown lint (MD032) violations resolved repo-wide

---

### Phase 6 - Knowledge Migration & Audit Tooling (v0.6.0)

Completed:

* `audit-knowledge` CLI command - repository knowledge inventory, config
  dependency mapping, orphaned-constant detection
* Markdown duplicate-consistency check
* Large-scale migration of detector signal lists from Python config into
  Markdown (existential, inner conflict, direction, pattern, ancestral,
  visibility, intensity modifiers, affect) - completing the knowledge-first
  architecture goal for those detectors
* Legacy pattern config module and stale config re-exports removed
* Emotional de-escalation and cross-framework detection phrase coverage expanded
* Numerology accuracy fixes (Balance number, Signature reading)

---

### Phase 7 - Response Safety & Multilingual Crisis Detection (v0.7.0)

Completed:

* Response contract validation layer for content-level safety
  (`response_safety_contract.py`, Issue #132) - catches literal diagnosis,
  prediction-as-fact, dependency-reinforcing, and guru-positioning phrasing in
  generated responses
* Multilingual crisis detection for Vietnamese, Spanish, French, and Chinese
  (Simplified) (Issue #130), via `crisis_language_packs.py` and per-language
  safety config modules
* Fenced-code-block-aware Markdown contract and HTML comment validation
* False-positive fixes in `audit-knowledge` for config usage and package-level
  re-exports
* ASCII-hyphen and code-block-language-tag documentation cleanup

Maintenance note (not an open implementation item):

* `CRISIS_TIER1_PATTERNS` morphology was English-only in v0.7.0. Sentence-level
  morphology is now covered in Phase 10; broader language-specific variants remain
  a human-reviewed maintenance consideration.
* `response_safety_contract.py` is deterministic regex/substring matching
  only; it does not catch paraphrased or implied violations

---

### Phase 8 - Test Coverage Hardening (v0.8.0, complete)

Completed:

* Unit test coverage for previously low-coverage detectors (`anger`,
  `spiritual_bypass`, `inner_conflict`, `perfectionism_paralysis`,
  `existential`, `empath`, `creative_drought`, `somatic`, `dependency`,
  `pattern`, `emotional_intensity`) raised from a 52-79% range to 89-100%
  (97% overall for `runtime/detectors/`), with every phrase sourced verbatim
  from the corresponding Markdown framework file
* Focused coverage for all response-output guards: `markdown_contract.py` at
  96%, and `response_contract.py`, `resource_sanitizer.py`,
  `response_safety_contract.py`, and `response_safety_gate.py` at 100%
* Focused coverage for `runtime/synthesis/conversation_synthesizer.py` at
  100%, including recurring-theme scoring, longitudinal memory, trigger
  thresholds, and user-ownership framing
* Focused coverage for audit, eval, packaging, Markdown support, checker, and
  quality tooling, including `audit-knowledge` (99%), `eval_groups` (98%),
  `eval_responses` (99%), `build_skill` (97%), `check_markdown_case` (98%),
  and `quality/lint` (100%)

The core and tooling coverage target is complete. Focused tests now cover
POSIX/Windows tooling-lock behavior and deterministic HTTP response, fallback,
and transport-error paths in the Markdown link checker.

The previously low-priority wrapper-coverage follow-up is complete: thin
`devtools/cli/` entry points now have direct execution coverage, while their behavior
continues to be verified through canonical implementation and integration checks.

---

### Phase 9 - v0.8.0 Knowledge, Routing & Synthesis Alignment (complete)

Completed:

* Routed the five spiritual frameworks that had knowledge assets but no primary
  framework route: dark night of the soul, soul nourishment, divine guidance,
  sacred polarity, and spiritual purpose.
* Corrected conversation synthesis so the current user message participates in
  history-based analysis, rather than being omitted from the synthesis input.
* Aligned runtime `Activate` instruction targets with the canonical kebab-case
  knowledge filenames, and added a contract test to prevent target drift.
* Synchronized voice session-ritual first-session guidance with the canonical
  session contract and corrected the safety configuration documentation link.
* Hardened core, contract, synthesis, and developer-tool test coverage to
  96.8% line and 92.6% branch coverage across the package at release time.

---

### Phase 10 - Deterministic Response-Safety Governance (post-v0.8.0, complete)

Completed:

* End-to-end regression coverage now proves every current
  `select_framework_async` primary-framework path reaches `_apply_safety_gate`.
  The matrix includes the five spiritual framework routes introduced in v0.8.0
  (`dark_night`, `soul_nourishment`, `divine_guidance`, `sacred_polarity`, and
  `spiritual_purpose`) as well as the existing safety and mirror paths. A
  selector-miss regression also forces the selector's local crisis detector to
  miss a real Tier 1 message, proving the gate independently re-derives and
  overrides it to `CRISIS`.
* `CRISIS_TIER1_PATTERNS` now covers reviewed sentence-level morphology beyond
  English for Vietnamese, Spanish, French, and Simplified Chinese, with
  positive and near-miss regression cases. Literal per-language phrase packs
  remain the primary source of truth.
* ADR 0002 records the decision to keep response-safety enforcement and its CI
  regression gate deterministic. Semantic or LLM classification is not added
  to runtime enforcement, safety gating, or CI; any future reversal requires a
  superseding ADR with explicit fallback, privacy, reproducibility, cost, and
  rollback evidence.
* The safety-enforcement matrix now records sentence-level multilingual
  morphology and the approved deterministic boundary for the response-safety
  contract.
* Reviewed Vietnamese input safety phrase packs now cover accented and
  diacritic-stripped diagnosis, prediction, jailbreak, and system-extraction
  requests, with deterministic regression fixtures and grouped-eval evidence.
  This remains a narrow maintenance expansion, not semantic classification.
* Closed the remaining Issue #133 identity-boundary gap: direct requests to
  delegate self-definition to SoulMap or treat it as a spiritual guide/awakener
  now use the deterministic `identity_confirmation` boundary, with reflective
  and fictional near-miss coverage.

Ongoing maintenance:

* Add a narrowly scoped deterministic pattern only for a human-reviewed,
  documented phrasing gap, with positive regression and a relevant near-miss
  where feasible.
* Keep the safety-enforcement matrix and ADR references synchronized whenever
  the response-safety categories or enforcement architecture change.

Phase 10 deliberately stays narrow: deterministic safety evidence and
maintenance only. SoulMap's [`known-limitations.md`](../docs/engineering/known-limitations.md)
continues to treat model-based safety enforcement as an explicit non-goal unless
a superseding ADR revisits it.

---

### Phase 11 - Platform & Distribution Expansion (in progress)

Completed foundation:

* `docs/integrations/*.md` now declare `AGENTS.md` as their canonical doctrine
  source and the exact compatible package version in front matter. The Markdown
  contract validates both fields against repository truth, so release drift in
  any of the Claude, ChatGPT, Gemini, or Poe guides fails local CI.
* Static integration contracts verify core identity/safety anchors in each
  platform instruction surface and ensure every archive file referenced by the
  deployment upload lists actually ships in the standard distribution artifact.
* The integration index defines compatibility actions by change type, while the
  internal launch checklist records non-sensitive, dated manual acceptance evidence for any platform that is actively deployed. Repository tests do not
  claim to prove third-party deployment behavior.
* Library v1 now has a versioned source catalog at `library/catalog.json` and a
  generated `dist/soulmap-ai-library.json` manifest with release URL, compatibility,
  artifact size, and SHA-256 metadata. The release workflow publishes the manifest
  beside the standard ZIP and `.skill` archives; this is still manual distribution,
  not a public marketplace registration or one-click installer.

Not yet done:

* Additional platform adapters beyond the current Claude-first flow, referenced
  as allowed-but-optional in
  [`docs/engineering/maintenance-boundary.md`](../docs/engineering/maintenance-boundary.md)
* Live integration testing across the four currently documented platforms
  (Claude, ChatGPT, Gemini, Poe), which requires an active deployment and
  operator-recorded manual acceptance evidence. The 2026-08-15 baseline review
  found no active platform, deployment owner, or configured platform connector;
  this item remains blocked rather than being treated as failed or complete.

These two items are intentionally outside the current non-AI execution scope and
remain unchanged for a future platform-specific workstream.

---

### Phase 12 - Toolchain Support & Test Reproducibility (complete; maintenance ongoing)

This track was identified after reviewing the locked development toolchain and official
compatibility policies for Python 3.11. Its implementation work is complete; the
remaining obligations are recurring maintenance, not a package migration or a new
product surface.

Completed foundation:

* `docs/engineering/package-compatibility-research.md` records official compatibility,
  lifecycle and operating-boundary findings for every direct development tool in the
  v0.9.0 lock baseline.
* `tests/contract/test_toolchain_support_contract.py` checks that the Python floor, CI
  Python baseline, direct development packages, lockfile and research matrix do not
  drift apart.
* The policy records that pytest-xdist and pytest-randomly failures must preserve seed,
  worker count, operating system, Python version and lock state before diagnosis, and
  that pytest-timeout is a hang/deadlock signal rather than a performance benchmark.
* `scripts/pytest_diagnostics.py` gives CI and release verification an explicit
  pytest-randomly seed, records xdist worker mode and Python/OS context in the
  GitHub step summary on failure, and prints a serial `-n 0` reproduction command.
* The 2026-08-19 baseline review records Python 3.11.16, the latest official
  3.11 security bugfix release at review time, in
  `docs/engineering/package-compatibility-research.md` with the upstream release
  evidence and security-review boundary.
* CI, release, CodeQL, and autofix now use local composite installers instead of
  third-party setup-uv/actionlint archives. uv is pinned to 0.12.5 through the
  official unmanaged installer, while actionlint 1.7.12 is downloaded from its
  release URL and SHA-256 verified before workflow validation. This removes the
  repeated codeload rate-limit failure mode without adding a runtime dependency.
* Direct tests now execute every thin `src/soulmap/devtools/cli/` entrypoint and cover
  the meaningful `quality.format` Markdown-file and subprocess-status branches. The
  wrappers remain forwarding layers, while behavior stays tested in their canonical
  implementation modules.

Maintenance obligations:

* Apply the [dependency refresh and advisory review checklist](../docs/operations/dependency-refresh.md)
  whenever a future lockfile refresh is triggered by upstream deprecations, security
  advisories, incompatibility, drift or a deliberate maintenance window.
* Keep dependency updates grouped by purpose and require the full repository gate before
  release; do not add a scanner or replace a package without a documented blocker. The
  process is contract-tested in `tests/contract/test_dependency_refresh_process_contract.py`.

The track explicitly does not add a Python version expansion, a runtime dependency,
semantic safety classification, or platform adapter.

---

### Public Website Surface - Python-only, non-AI

The repository now includes a deliberately small public website surface under
`src/soulmap/web/`. It is served by Python's standard-library WSGI server and exists to
explain SoulMap, publish boundaries, and direct users to the generated `.skill` and `.zip`
artifacts.

Completed foundation:

* Responsive public pages for Home, How it works, Boundaries, Download, Notes, About,
  FAQ, Privacy, Skills catalog, and Skill detail routes in EN/VI/KO.
* `uv run soulmap web` with configurable local host and port.
* In-process route tests, security headers, skip-link/accessibility markers, responsive CSS,
  reduced-motion support, and local browser smoke validation.
* Explicit separation from `skills/`, `.claude/`, runtime knowledge loaders, and custom AI
  artifacts.
* `uv run soulmap web --export-static` generates a project-site-safe static tree with an
  optional base path, and `scripts/verify_static_site.py` rejects source leakage, scripts,
  symlinks, local hosts, missing routes, and unsafe links.
* The Skills catalog has localized EN/VI/KO metadata and prompt scenarios, JSON-backed
  locale catalogs with exact parity tests, deterministic Search/Ask modes, safe question
  starters, localized error states, compact Ask results, raw Markdown/API bundles, htmx
  detail loading, Alpine transitions, and a static-export contract.
* Shared HTML head generation includes conservative `preload`, `preconnect`, and
  `dns-prefetch` hints derived from the actual external stylesheet/script origins, without
  adding runtime dependencies or speculative platform integrations.
* The original `server.py` boundary is now split into HTTP/config, page renderers, Skill
  views, and ordered route dispatch modules with compatibility aliases and characterization
  tests preserved throughout the migration.
* `.github/workflows/website-pages.yml` rebuilds on website-source changes, uploads the
  verified output for inspection, and publishes only generated files to `gh-pages` after a
  successful `main` build.

Non-goals for this surface:

* No live AI chat, accounts, database, memory, community feed, numerology calculator,
  health claims, scheduled reminders, or platform connector.
* No website content is treated as shipped Skill doctrine unless it is deliberately authored
  and promoted through the existing knowledge-base workflow.

---

## Next Phase Plan

This section is the execution roadmap after the v0.9.0 baseline. It is intentionally ordered by risk and dependency rather than by feature novelty. Each phase should be delivered through one or more small pull requests, with characterization tests added before boundary changes and no automatic merge.

### Phase 13 - Post-v0.9.0 Repository Truth and Release Hygiene

**Priority:** P0 - immediate after the current web/tooling PR train.

**Goal:** Make `main`, release metadata, documentation, generated artifacts, and repository contracts describe the same shipped state.

| Workstream | Required outcome | Definition of Done |
| --- | --- | --- |
| Mainline reconciliation | Merge or explicitly close all reviewed PRs and remove stale branches from the active execution list | `main` is the only release baseline and `git diff` against the documented baseline is explainable |
| Roadmap and contract sync | Keep `docs/ROADMAP.md`, `repo-contract.md`, `README.md`, integration guides, and release notes consistent | Markdown contracts, link checks, case checks, and documentation review pass |
| Release identity | Align version, changelog, release manifest, artifact hashes, and website build metadata | A clean build produces the expected versioned artifacts and manifest without manual edits |
| Ownership map | Record who owns runtime safety, knowledge, packaging, website, CI, and release review | Every active surface has one canonical owner document and one escalation path |

The phase must not introduce a new runtime API, platform connector, or semantic safety layer. Its purpose is to remove repository ambiguity before further implementation begins.

### Phase 14 - Runtime and Tooling Quality Consolidation

**Priority:** P0 - high value, low product risk.

**Goal:** Keep the Python layer small, typed, reproducible, and free of accidental dead code while preserving the knowledge-first boundary.

The work includes a full Pyright pass over `src`, `tests`, and `scripts`; coverage configuration aligned with CI; branch-coverage review for routing, guards, packaging, Markdown support, and devtools; dead-code classification with Vulture; and focused performance measurements for import, build, static export, and detector loading. Any deletion must be preceded by a usage audit and a regression test where behavior is public.

**Exit criteria:** Pyright is clean under the repository configuration; Deptry, Vulture, Ruff, and the full test suite pass; the combined runtime/web coverage floor remains at least 95%; benchmark results are recorded for any claimed performance improvement; and no content is moved from Markdown into Python.

### Phase 15 - Safety and Knowledge Maintenance Without Semantic Expansion

**Priority:** P0 - continuous safety track.

**Goal:** Improve deterministic safety coverage only when a human-reviewed phrasing gap is demonstrated.

Each change must begin with `soulmap audit-knowledge`, identify the canonical Markdown or protected Python source, add a positive case and a near-miss, update the relevant grouped eval, and refresh the safety-enforcement matrix. Crisis language packs remain protected Python modules. New language support requires qualified human authorship, explicit phrase review, and full before/after crisis evaluation. No automated translation is accepted as safety evidence.

**Exit criteria:** All changed safety rows remain `enforced` or have a documented reason for `partial`; grouped and response evaluations pass; the relevant ADR or matrix row is updated; and the change does not add semantic classification, LLM calls, or probabilistic runtime behavior.

### Phase 16 - Public Website and Static Export Hardening

**Priority:** P1 - next product-facing track.

**Goal:** Make the Python-only website reliable, accessible, localized, and reproducible across mobile, tablet, desktop, and GitHub Pages.

| Area | Planned work |
| --- | --- |
| Localization | Maintain EN/VI/KO JSON parity, fallback tests, localized metadata, and a documented workflow for adding keys without hard-coded web copy |
| Accessibility | Add keyboard and screen-reader regression checks for navigation, language menu, search/ask mode, modal fragments, focus return, and reduced motion |
| Static correctness | Verify every localized route, canonical URL, hreflang, raw bundle, hash, asset path, and base-path variant in clean and incremental builds |
| Performance | Track export time, incremental-build savings, HTML size, asset hints, and critical route response time without adding a JavaScript framework or runtime API |
| Visual QA | Maintain browser smoke evidence at representative viewport sizes and check typography, spacing, contrast, radius, overflow, and touch targets |

**Exit criteria:** Static verifier passes for EN/VI/KO and `/soulmap-ai`; browser smoke passes on desktop and narrow mobile viewports; accessibility checks cover the interactive controls; and the website remains independent from shipped Skill doctrine unless content is intentionally promoted.

### Phase 17 - Packaging, Library, and Release Provenance

**Priority:** P1 - required before broad distribution.

**Goal:** Make every release artifact reproducible, inspectable, and safe to import into supported AI tools without claiming live provider behavior that has not been tested.

The phase covers artifact manifest generation, SHA-256 verification, wheel/sdist resource checks, ZIP and `.skill` content contracts, catalog parity, release provenance attestations, clean-environment extraction tests, and release rollback documentation. The standard distribution remains the two-artifact model defined by `known-limitations.md`. Any new artifact format requires an ADR and a contract test before implementation.

**Exit criteria:** A clean checkout can build the standard artifacts twice with explainable deterministic differences; hashes and manifest metadata agree; internal files do not leak into public Skill bundles; release CI verifies provenance; and upload/import instructions match the actual artifacts.

### Phase 18 - Operations, Incident Readiness, and Maintenance Automation

**Priority:** P1 - parallel maintenance track after release hardening.

**Goal:** Reduce operational ambiguity without adding accounts, databases, scheduled runtime jobs, or user-data storage.

Planned work includes dependency refresh evidence, security advisory review, CI failure diagnosis, release rollback, static-site publication recovery, artifact retention, ownership rotation, and a lightweight issue triage policy. Automation may open or label maintenance work, but a maintainer must review dependency changes, safety changes, release mutations, and any external publication action.

**Exit criteria:** Operations documents identify triggers, owners, evidence, rollback steps, and escalation paths; scheduled or automated tasks do not mutate releases without human review; and the repository remains usable offline for tests, evals, packaging, and artifact verification.

### Phase 19 - Optional Platform Acceptance Workstream

**Priority:** P2 - blocked until prerequisites exist.

**Goal:** Validate documented Claude, ChatGPT, Gemini, and Poe integration surfaces only when there is an active deployment owner, a chosen target, access to the relevant provider, and explicit manual acceptance scope.

This phase is not a commitment to add provider connectors or runtime APIs. It may include provider-specific documentation fixes, raw Markdown fallback validation, prompt handoff checks, and operator-recorded acceptance evidence. Live behavior must never be inferred from repository tests. If a platform lacks reliable prefilled prompts or requires sign-in, the raw Markdown URL remains the canonical fallback.

**Entry gate:** named owner, active deployment target, test account or documented takeover procedure, privacy review, rollback plan, and a separate PR scope. Without these prerequisites, the work remains blocked and should not be represented as incomplete implementation.

### Phase Order and Pull Request Strategy

| Order | Phase | Depends on | Recommended PR boundary |
| --- | --- | --- | --- |
| 1 | 13 | Current PR train and merged `main` | Repository truth, release metadata, and roadmap cleanup |
| 2 | 14 | Phase 13 | Pyright/coverage/tooling alignment, then focused dead-code or performance fixes |
| 3 | 15 | Phase 13; independent of website work | One safety gap or one documented maintenance cluster per PR |
| 4 | 16 | Phase 13 and current static export contracts | Accessibility, localization, static verifier, and visual QA as separate PRs |
| 5 | 17 | Phase 14 and Phase 16 build contracts | Packaging/provenance changes separate from content changes |
| 6 | 18 | Phase 13 release ownership map | Operations documentation and automation changes separately reviewed |
| 7 | 19 | Explicit entry gate above | One provider or one documentation acceptance surface per PR |

### Global Definition of Done for Every Future Phase

A phase is complete only when its source-of-truth documents are updated, characterization tests precede boundary changes, the relevant unit/contract/eval tests pass, Pyright and Ruff are clean, the full validation gates pass, static artifacts are verified when applicable, and the PR is reviewable without an automatic merge. Changes must preserve Python 3.11 support, the no-runtime-API boundary, canonical English Markdown ownership, explicitly reviewed runtime locale evidence, deterministic safety enforcement, EN/VI/KO website parity, and the two-artifact packaging contract.

---

## Validation and Quality System

SoulMap AI uses a multi-layer validation architecture.

### Structural & Format Layer

```bash
uv run soulmap format
uv run soulmap lint
```

Responsibilities:

* Ruff formatting and linting
* Pyright standard-mode type checking
* pymarkdownlnt Markdown compliance
* `soulmap check-links` broken-link detection
* `soulmap check-case` case-consistency checks

---

### Knowledge Consistency Layer

```bash
uv run soulmap audit-knowledge
uv run soulmap eval-markdown-contracts
```

Responsibilities:

* Orphaned config constant detection
* Config dependency and import-provenance mapping
* Doctrine ↔ Markdown contract consistency (AGENTS.md vs skills/)
* Markdown duplicate-consistency checks

---

### Behavioral Eval Layer

```bash
uv run soulmap eval-groups
uv run soulmap eval-responses
```

Responsibilities:

* Grouped, source-backed routing coverage (86 groups / 237 items)
* Response-safety contract regression (`RESPONSE_SAFETY_CONTRACT` cases)
* Red-team and gray-zone case coverage (crisis, dependency, spiritual
  manipulation, gradual pressure, ambiguous distress)

---

### Test Layer

```bash
uv run soulmap test -n auto -q
```

Responsibilities:

* Unit tests per detector, guard, and routing module
* `tests/contract/` - response and Markdown contract enforcement
* `tests/integration/` - framework selector priority behavior
* `tests/eval_regression/` - safety eval regression gate

---

## CI/CD and Automation

### Current Workflows

| Workflow      | Purpose                                          |
| ------------- | ------------------------------------------------- |
| ci.yml        | Format, lint, type-check, test, eval-groups, eval-markdown-contracts |
| autofix.yml   | Automated formatting fixes on PRs                  |
| codeql.yml    | Static security analysis                           |
| release.yml   | Changelog and versioned release automation          |
| website-pages.yml | Verified static website export and GitHub Pages publication |

### Release System

The project uses Commitizen-style conventional commits for changelog generation.

Workflow:

```text
Change
  |
Conventional commit
  |
release.yml
  |
Version bump + CHANGELOG.md entry
  |
GitHub Release + git tag
```

Version history: `v0.1.0` → `v0.2.0` → `v0.3.0` → `v0.4.0` → `v0.4.1` →
`v0.5.0` → `v0.5.1` → `v0.6.0` → `v0.7.0` → `v0.8.0` → `v0.9.0` (current).

---

## Future Direction

### Non-goals (explicitly out of current scope)

Per [`docs/engineering/known-limitations.md`](../docs/engineering/known-limitations.md),
these are not planned unless a new ADR revisits them:

| Non-goal | Why it is not a goal |
| --- | --- |
| Semantic safety classification | Adds LLM dependency to safety enforcement; deterministic detection is sufficient for current scope |
| LLM response quality evaluation in CI | Requires non-deterministic scoring; outside the regression gate's purpose |
| Framework combination (two active primary frameworks) | Violates `AGENTS.md` doctrine; makes routing and testing ambiguous |
| Dynamic language expansion without static phrase review | Crisis detection requires human authorship, not automated translation |
| Python-generated response content | Violates the knowledge-first architecture; content belongs in Markdown |
| Per-language framework routing | Framework selection is language-unaware by design |
| Markdown-loaded crisis detection | Protected-module policy; no pending safety evaluation evidence |

### Open, tracked future work

The remaining roadmap work is intentionally bounded. Human-reviewed deterministic
regression evidence remains an ongoing maintenance obligation whenever a real safety
phrasing gap is observed. Platform adapters beyond the current Claude-first flow remain
optional and blocked until there is an active platform owner, deployment target, and
explicit scope for the required live acceptance evidence. They are not implemented in
this non-AI workstream because the repository boundary explicitly excludes unused
platform adapters and connectors.

---

## Success Metrics

| Area              | Direction                                              |
| ------------------ | -------------------------------------------------------- |
| Safety enforcement  | Keep `safety-enforcement-matrix.md` rows at `enforced`   |
| Eval coverage       | Maintain 0 `failed_checks` across eval-groups and eval-markdown-contracts |
| Test coverage       | Increase `runtime/guards/` and `devtools/` coverage toward the `runtime/detectors/` bar (97%) |
| Knowledge integrity | Zero orphaned config constants in `audit-knowledge`      |
| Documentation       | Doctrine, safety, packaging, and public claims stay one consistent story |
| Distribution        | Keep all four documented platform integrations current with `AGENTS.md` |

---

## Glossary

| Term                 | Definition                                                          |
| --------------------- | ---------------------------------------------------------------------|
| Framework             | A reflective knowledge module (grief, anger, existential, ...) with its own detector |
| Detector               | Python module scoring Markdown-sourced signal phrases for a framework |
| Protected module       | A module (crisis, dependency) intentionally excluded from Markdown-loading policy |
| ADR                     | Architecture Decision Record, required for any safety-adjacent reversal |
| Eval group             | A source-backed routing test case in `evals/datasets/groups.json`   |
| Response safety contract | Content-level validation of generated response text for diagnosis/prediction/dependency violations |
| Non-goal                | An idea explicitly out of scope unless a new ADR revisits it        |
| Skill package            | The shipped `.skill`/`.zip` artifact built via `soulmap build`      |

---

Last updated: August 21, 2026
