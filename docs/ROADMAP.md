# SoulMap AI - Project Roadmap

> **Repository:** [soulmap-ai](https://github.com/tuanductran/soulmap-ai)
> **Maintainer:** Tuan Duc Tran
> **License:** see [LICENSE](../LICENSE)
> **Status:** Actively maintained, current release v0.8.0
> **Last updated:** 17 August 2026

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
5. [Validation and Quality System](#validation-and-quality-system)
6. [CI/CD and Automation](#cicd-and-automation)
7. [Future Direction](#future-direction)
8. [Success Metrics](#success-metrics)
9. [Glossary](#glossary)

---

## Project Vision

### A Bounded, Anti-Dependency Reflective Companion

SoulMap AI aims to be a reflective companion that helps people hear themselves more
clearly without handing their authority away. The project follows the principle stated
in [README.md](../README.md):

> Mirror-first, not advice-first.

Every framework, safety rule, and detector is treated as a maintainable artifact with:

* Markdown as the single source of truth for knowledge and detection phrases
* a thin, deterministic Python layer for routing, safety gating, and packaging
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
| Type checking      | Pyright (strict)                          |
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
├── skills/
│   ├── frameworks/       Reflective frameworks (grief, anger, existential, ...)
│   ├── spiritual/        Spiritual discernment and bypass detection content
│   ├── safety/           Boundaries, whitelist/blacklist doctrine
│   └── meta/             Master prompt, orchestration, response/redirect templates
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
└── .github/workflows/    ci.yml, autofix.yml, codeql.yml, release.yml
```

---

### Detection & Safety Architecture

Each detector follows a structured, Markdown-sourced format:

```text
skills/frameworks/<framework>.md   → "## Detection signals" (source of truth)
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

Not yet done (tracked, see [Future Direction](#future-direction)):

* Historical note: `CRISIS_TIER1_PATTERNS` morphology was English-only in
  v0.7.0. Sentence-level morphology is now covered in Phase 10; broader
  language-specific variants remain a maintenance consideration.
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

A deliberately low-priority follow-up remains: decide whether thin
`devtools/cli/` entry-point wrappers need direct unit coverage or should remain
verified through the canonical `soulmap` CLI and integration checks.

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
  internal launch checklist records non-sensitive, dated manual acceptance
  evidence for any platform that is actively deployed. Repository tests do not
  claim to prove third-party deployment behavior.

Not yet done:

* Additional platform adapters beyond the current Claude-first flow, referenced
  as allowed-but-optional in
  [`docs/engineering/maintenance-boundary.md`](../docs/engineering/maintenance-boundary.md)
* Live integration testing across the four currently documented platforms
  (Claude, ChatGPT, Gemini, Poe), which requires an active deployment and
  operator-recorded manual acceptance evidence. The 2026-08-15 baseline review
  found no active platform, deployment owner, or configured platform connector;
  this item remains blocked rather than being treated as failed or complete.

---

### Phase 12 - Toolchain Support & Test Reproducibility (in progress)

This track was identified after reviewing the locked development toolchain and official
compatibility policies for Python 3.11. It is maintenance work, not a package migration
or a new product surface.

Completed foundation:

* `docs/engineering/package-compatibility-research.md` records official compatibility,
  lifecycle and operating-boundary findings for every direct development tool in the
  v0.8.0 lock baseline.
* `tests/contract/test_toolchain_support_contract.py` checks that the Python floor, CI
  Python baseline, direct development packages, lockfile and research matrix do not
  drift apart.
* The policy records that pytest-xdist and pytest-randomly failures must preserve seed,
  worker count, operating system, Python version and lock state before diagnosis, and
  that pytest-timeout is a hang/deadlock signal rather than a performance benchmark.

Remaining work:

* Add a small CI diagnostic summary that exposes the pytest-randomly seed and worker
  mode when a parallel test job fails, while retaining a serial `-n 0` reproduction path.
* Record the latest tested Python 3.11 patch release and review lockfile refreshes
  against upstream deprecations and security advisories.
* Keep dependency updates grouped by purpose and require the full repository gate before
  release; do not add a scanner or replace a package without a documented blocker.

The track explicitly does not add a Python version expansion, a runtime dependency,
semantic safety classification, or platform adapter.

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
* Pyright strict type checking
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
`v0.5.0` → `v0.5.1` → `v0.6.0` → `v0.7.0` → `v0.8.0` (current).

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

* Maintain human-reviewed deterministic regression evidence for newly
  observed response-safety phrasing gaps
* Decide whether thin `devtools/cli/` wrappers need direct unit coverage or
  remain covered through canonical CLI and integration checks
* Platform adapters beyond the current Claude-first flow

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

Last updated: August 9, 2026
