# SoulMap AI - Project Roadmap

> **Repository:** [soulmap-ai](https://github.com/tuanductran/soulmap-ai)
> **Maintainer:** Tuan Duc Tran
> **License:** see [LICENSE](../LICENSE)
> **Status:** Actively maintained, current release v0.7.0

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
  wellbeing, emotional de-escalation, pattern mapper
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

### Phase 7 - Response Safety & Multilingual Crisis Detection (v0.7.0) - current

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

* `CRISIS_TIER1_PATTERNS` regex morphological variants remain English-only -
  multilingual coverage exists at the phrase-pack level, not yet at the
  regex-pattern level
* `response_safety_contract.py` is deterministic regex/substring matching
  only; it does not catch paraphrased or implied violations

---

### Phase 8 - Test Coverage Hardening (in progress)

Completed:

* Unit test coverage for previously low-coverage detectors (`anger`,
  `spiritual_bypass`, `inner_conflict`, `perfectionism_paralysis`,
  `existential`, `empath`, `creative_drought`, `somatic`, `dependency`,
  `pattern`, `emotional_intensity`) raised from a 52-79% range to 89-100%
  (97% overall for `runtime/detectors/`), with every phrase sourced verbatim
  from the corresponding Markdown framework file

Not yet done:

* Expand unit test coverage for the remaining `runtime/guards/` modules, the
  layer closest to final output safety. `markdown_contract.py` now has focused
  unit coverage at 96%; `response_contract.py`, `resource_sanitizer.py`, and
  the response-output contracts still need stronger branch coverage.
* Unit test coverage for `devtools/` (audit-knowledge, eval_groups,
  eval_responses, build_skill) - currently 7-30%, functionally verified only
  through direct CLI invocation, not pytest-level unit tests
* Unit test coverage for `runtime/synthesis/conversation_synthesizer.py`
  (currently 74%)

---

### Phase 9 - Morphological & Semantic Detection Depth (proposed, not started)

Not yet done:

* Expand `CRISIS_TIER1_PATTERNS` regex morphological variants beyond English,
  closing the gap noted in `docs/engineering/safety-enforcement-matrix.md`
  and `docs/engineering/crisis-detection-layering-review.md`'s "Future work"
  section
* End-to-end regression test proving every `select_framework_async` return
  branch reaches `_apply_safety_gate`, per the same "Future work" section
* Evaluate semantic-level validation for `response_safety_contract.py` beyond
  literal regex/substring matching, per Issue #132's stated future work -
  contingent on whether an LLM dependency is judged acceptable given the
  "no LLM in safety enforcement" non-goal below

This phase intentionally has no committed implementation plan yet; SoulMap's
own [`known-limitations.md`](../docs/engineering/known-limitations.md) treats
several adjacent ideas as explicit non-goals unless revisited with a new ADR
(see the non-goals table below).

---

### Phase 10 - Platform & Distribution Expansion (proposed, not started)

Not yet done:

* Additional platform adapters beyond the current Claude-first flow, referenced
  as allowed-but-optional in
  [`docs/engineering/maintenance-boundary.md`](../docs/engineering/maintenance-boundary.md)
* Deeper integration testing across the four currently documented platforms
  (Claude, ChatGPT, Gemini, Poe) beyond manual deployment guides
* Formal versioning/compatibility guarantees for `docs/integrations/*.md`
  instruction sets as the doctrine in `AGENTS.md` evolves

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
`v0.5.0` → `v0.5.1` → `v0.6.0` → `v0.7.0` (current).

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

* Multilingual `CRISIS_TIER1_PATTERNS` regex morphological variants
* End-to-end regression proof that every `select_framework_async` branch
  reaches `_apply_safety_gate`
* `runtime/guards/` and `devtools/` unit test coverage expansion
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
