# SoulMap AI - Project Roadmap

> **Repository:** [soulmap-ai](https://github.com/tuanductran/soulmap-ai)
> **Maintainer:** Tuan Duc Tran
> **License:** see [LICENSE](../LICENSE)
> **Status:** Actively maintained, current release v0.9.1
> **Last updated:** August 30, 2026

This roadmap describes the long-term direction, architecture evolution, and engineering
priorities of SoulMap AI.

SoulMap AI is a content-first knowledge base - a reflective-companion AI system - with a
small Python enforcement and tooling layer on top. The repository's discipline is stated
in [SOULMAP.md](../SOULMAP.md) and [README.md](../README.md): brand, safety, packaging, and
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
├── SOULMAP.md
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

* Initial doctrine and package contract (`SOULMAP.md`)
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

* `docs/integrations/*.md` now declare `SOULMAP.md` as their canonical doctrine
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

### Phase 13 - Repo-wide hardening pass (v0.9.1, complete)

This track came out of a full audit of the runtime, the developer tooling, the
knowledge files and the release workflow. It shipped 43 commits after v0.9.0, of
which 19 were defect fixes, and added 6 test files.

Completed:

* Routing: grief stayed primary at moderate emotional intensity. A bereaved user
  who expressed more distress previously received less grief support, because the
  moderate-intensity branch handed the response to de-escalation and dropped the
  grief framework.
* Safety: the scope classifier now blocks five documented blacklist phrases it had
  let through across Rules 2, 4, 5, 7 and 8, and crisis resource links no longer
  count their query string as the response's one allowed question.
* Runtime: a malformed history entry reaching the demo entrypoint no longer raises
  inside the safety gate.
* Knowledge: 140 duplicated detection phrases were removed from 8 shipped files,
  with per-label deduplication so a phrase authored under two labels survives.
* Test infrastructure: pytest gained strict markers, strict config, strict xfail
  and a hang timeout, and coverage was widened from the runtime alone to the whole
  package. Each of these had been silently inert.
* Release: `cz bump` now carries the version into the four integration guides,
  the bump commit stages the relocked `uv.lock`, and the Markdown contracts are
  re-verified against the bumped tree.
* Python surfaces moved to enforced Google-style docstrings and full annotations
  through the Ruff `D` and `ANN` rule sets, alongside 11 further rule sets that
  the code already satisfied.

---

### Phase 14 - Enforcement ceiling clarity (complete)

`docs/engineering/safety-enforcement-matrix.md` held 10 rows at `enforced` and
11 at `partial`, and instructed readers to "treat `partial` rows as active
hardening targets". Auditing all 11 by hand found two different gaps sharing
one label, not one.

Nine name a gap no amount of new Python code closes: the row's own text asked
for a "production response generator", a "dedicated runtime grandiosity
responder", or a "full runtime independence policy engine". `docs/engineering/known-limitations.md`
records "Python does not generate AI responses" as intentional design, and the
non-goals table below lists Python-generated response content as a non-goal.
Those 9 rows are now `bounded`, a new status distinct from `partial`: each
names the deployed AI surface that completes the wording and the eval that
verifies it there.

The remaining 2 did not fit that pattern on inspection, so they were not
reclassified. "Epistemic guardrails for spiritual content" asked for a Python
*scan*, not a generator, the same shape as the `response_safety_contract.py`
validator that already exists for other rules; nothing dedicated to
numerology, chakra, or karma framing has been built yet. "Stage-appropriate
response depth" asked for enforcement that `response_contract.py` already has
the shape for (grading structural properties of generated text against the
same `selection` metadata it already reads); a hard length ceiling per mode
is buildable, only the emotional-versus-intellectual register distinction is
genuinely bounded. Both stayed `partial`, with gap notes that say so, and both
are now open work below instead of buried inside a "ceiling" narrative that
did not actually apply to them.

Completed:

* `bounded` added to the status legend, defined as enforcement and eval
  coverage complete inside the package, with the remaining gap being
  generated wording that belongs to the deployed AI surface.
* The 9 rows above moved to `bounded`, each citing
  `docs/engineering/known-limitations.md`, "AI response generation", and
  naming the eval that verifies the wording at the host layer.
* The 2 rows above kept `partial`, with gap notes rewritten to say why they
  are real, closable gaps rather than the same ceiling as the other 9.
* The success metric below was restated as reachable: no row sits at
  `partial` for a reason inside the package's own scope. It now holds, since
  the only 2 `partial` rows are exactly that: real, scoped, open work.
* `tests/contract/test_safety_enforcement_matrix.py` checks every status
  token against the legend and every `bounded` row's citation against
  `known-limitations.md`, so a status this matrix cannot back is a test
  failure, not a stale claim.

This track added no runtime behavior and changed no safety enforcement. It
changed what the matrix claims, so the claim matches the architecture, and it
surfaced 2 real gaps the original "all 11" framing had mislabeled as
unreachable.

---

### Phase 15 - Regression-strength verification (complete)

The v0.9.1 pass kept finding the same bug class: a check that cannot fail. The
check exists, runs, and reports success, so it is trusted, but no input makes it
red.

Confirmed instances, each fixed earlier and each verifiable in the repository:

* A safety red-team case whose category the runner could not dispatch printed
  `SKIP`, was still counted under `Passed`, and left the exit code at 0. A typo in
  a case name read as coverage.
* A typo in a pytest marker silently did nothing, before `--strict-markers`.
* An `xfail` that started passing reported `xpassed` and kept the run green,
  before `xfail_strict`.
* `pytest-timeout` was installed but never given a value, so it timed nothing out.
* Coverage measured the runtime only, so 31 developer-tooling modules were
  reported as if absent.

Every fix in that pass was verified the same way: revert the fix, confirm the
test goes red. That method is mutation testing done by hand, it is fully
deterministic.

Completed:

* Named the bug class as "Charter 5, a regression test that cannot fail" in
  `docs/engineering/TESTER.md`, alongside the existing exploratory testing
  charters, with the revert-and-confirm-red method stated as the standard a
  new safety-critical regression test should meet before merge, and the 5
  confirmed instances above recorded as evidence.
* Added `tests/mutation/test_safety_critical_mutations.py`: 6 curated
  mutations over the crisis detector's Tier 1 lists, the dependency
  keyword list, the grief-type tuple this session's own headline routing fix
  depends on, one scope-classifier blacklist category, the resource
  sanitizer's banned-word list, and the response-safety-contract's diagnosis
  patterns. Each test disables exactly one list with `monkeypatch` (which
  restores it automatically) and asserts a known-dangerous fixture, several
  reused verbatim from existing tests or the shipped red-team corpus, is no
  longer caught. Every fixture was independently confirmed dangerous before
  mutation and safe after, so the harness cannot pass vacuously in either
  direction.
* Kept the list curated rather than generated, as planned: 6 tests add
  negligible runtime next to a suite that already runs in seconds, where a
  general mutation-testing tool re-running the full suite per mutated branch
  would not.

This track added no runtime dependency, no semantic classification, and no
response-generation layer. It tests the tests.

---

### Phase 16 - Soulmate skill layer (v0.9.1, complete)

`docs/engineering/library-vs-framework.md` already names the pattern this phase
follows: the same relationship between a UI library and an application framework
built on it (React, Next.js) already exists inside SoulMap, where each individual
framework is built on the shared runtime without duplicating it. This phase applies
that same pattern one level up: `skills/soulmate/` is a new, more specialized skill
category built on top of SoulMap's existing frameworks and spiritual doctrine, the
way a framework built on Next.js still depends on and never bypasses Next.js itself.

Completed:

* `skills/soulmate/`, a new shipped skill category (`SKILL.md` plus 3 content files)
  for soulmate longing, partner-seeking patterns, and connection numerology. Every
  file states an explicit "Inherits from" list citing the existing skills it
  specializes rather than duplicates:
  [`relationship-reflection.md`](../skills/frameworks/relationship-reflection.md),
  [`spiritual-discernment.md`](../skills/spiritual/spiritual-discernment.md),
  [`numerology-chakra-policy.md`](../skills/spiritual/numerology-chakra-policy.md),
  [`symbolic-report-handling.md`](../skills/spiritual/symbolic-report-handling.md),
  [`epistemic-guardrails.md`](../skills/meta/epistemic-guardrails.md), and
  [`whitelist-blacklist-system.md`](../skills/safety/whitelist-blacklist-system.md).
* `soulmate-longing.md` and `partnership-patterns.md` are routable Python
  frameworks, wired the same way commit `beba57e` wired the five previously
  unrouted spiritual frameworks: each file gained an "## Activation Signals"
  section, each section is loaded by a matching detector
  (`soulmate_longing_detector.py`, `partnership_patterns_detector.py`) through
  the existing `load_keyword_section` loader, and `framework_selector.py` gained
  two new Medium-priority branches, right after Spiritual Purpose, each closing
  through the existing `_apply_safety_gate`. `SOULMAP.md`,
  `skills/meta/orchestration.md`, `skills/meta/framework-template-map.md`, and
  `skills/meta/deep-inquiry-bank.md` all gained matching entries, keeping the
  doctrine tables, the routing code, and the detailed structure and question
  banks in sync by the same contract every other framework already follows.
  Before finalizing the new signal phrases, both lists were checked against
  every higher-priority framework's existing signals (grief, shadow, existential,
  life direction) to confirm none of the new phrasing was already claimed and
  silently unreachable, the same collision check the `beba57e` precedent used.
  `numerology-connection-lens.md` stays a topic lens with no detector, the same
  category `relationship-reflection.md` belongs to in
  [`skills/frameworks/SKILL.md`](../skills/frameworks/SKILL.md): applied only
  after a primary framework, one of the two new ones included, is already active.
* Closed a real gap the new content exposed: the scope classifier's
  `identity_confirmation` blacklist already blocked "am I a twin flame" and "am I a
  starseed" but had no equivalent for "soulmate" phrasing. Added positive coverage
  in both question and statement word order, verified with curated near-miss cases
  so ordinary soulmate longing (`I'm looking for my soulmate`) is not swallowed by
  the block meant for identity-confirmation requests (`is he my soulmate`).
* `library/catalog.json` and `.claude-plugin/marketplace.json` both gained a
  seventh entry, kept in sync by
  `tests/contract/test_library_catalog_contract.py`; `SOULMAP.md`'s package-shape
  tree, the root `SKILL.md` table, and `docs/operations/LIBRARY.md`'s entry count
  were updated to match.
* Personal numerology reports the maintainer supplied as background were used only
  to confirm general Vietnamese numerology report structure (a report describes
  several named indices, not one single number). No personal identifier, birth
  date, or individual reading from those reports was carried into any shipped
  file. `skills/soulmate/numerology-connection-lens.md` never computes or confirms
  compatibility between two specific people's numbers, matching the same
  discipline `founder-numerology.md` already applies to numbers-only, no personal
  identifiers.

This track added two new Python detectors and two new priority-hierarchy entries,
and no change to any existing framework's routing or priority order. It is a
Framework-layer addition in the `library-vs-framework.md` sense: new Markdown
content plus the matching detector pair, governed entirely by the Library-layer
rules that already existed, with no change to `runtime/knowledge/`,
`runtime/guards/`, or the shared safety gate.

---

### Phase 17 - Post-Phase-16 audit: routing duplication and a silent failure mode (complete)

A requested strict full-repository audit, run after Phase 16 merged. Phases 13-15
already covered the runtime, tooling, knowledge files, and release workflow in
depth, and this pass confirmed that work held: `uv run vulture`, `uv run deptry .`,
and `uv run pip-audit` (all three already gated in CI) came back clean, no
`# type: ignore`, `# noqa`, `TODO`, `FIXME`, mutable default argument, or unsafe
`subprocess`/`eval`/`pickle`/unguarded `yaml.load` call exists anywhere in
`src/soulmap/`, and `parse_yaml_front_matter` already avoids a full YAML
dependency by design rather than by omission. The audit's real findings were
narrower and specific to `framework_selector.py`, the file Phase 16 had just
extended:

* `framework_selector.py` had grown to 986 lines, almost entirely from 27 return
  paths that each repeated the same 4-line `_apply_safety_gate` plus
  `_maybe_attach_debug` close, and 12 of those 27 branches (creative drought,
  perfectionism paralysis, ancestral patterns, fear of visibility, empath
  boundary, dark night, soul nourishment, divine guidance, sacred polarity,
  spiritual purpose, soulmate longing, partnership patterns) additionally
  repeated an identical 7-line "Mirror mode, no secondary, blocked: [], instruction
  from the detector's own recommendation" selection dict. Extracted as `_finish`
  (the shared close) and `_simple_selection` (the shared single-signal Mirror
  shape), used only where the existing branch was already byte-for-byte that
  shape. The priority-ordered `if`/`elif` chain itself, and every branch with
  real distinguishing logic (secondary layers, interpolated instructions, custom
  blocked lists), was left untouched, since that ordering is what lets the file
  be audited line-by-line against the priority table in `SOULMAP.md`. Net: 986
  lines to 872, zero behavior change, confirmed by the full existing regression
  suite (`tests/regression/test_routing_safety_gate.py`,
  `tests/integration/test_framework_selector_priorities.py`, every detector test,
  the mutation suite, 79/79 safety evals, and `eval-groups`) passing unmodified.
* `_run_detector_async` swallows any exception from any detector so one broken
  framework cannot fail the whole request, an intentional degrade-to-Mirror
  design, not a bug. Before this pass, that swallow was total: the failure was
  recorded to `debug_events` only when a caller had already set
  `SOULMAP_DEBUG=1`, so a detector regression in production would leave no trace
  anywhere, including in the crisis and dependency detectors that run through
  the same helper. `response_safety_gate.py`'s independent crisis re-derivation
  (ADR 0001) means a broken `detect_crisis` cannot silently produce an unsafe
  response, since the gate's own unwrapped call to the same function would raise
  and fail loudly instead, but "loud, unmonitored crash" is still a worse outcome
  than "logged and diagnosable." Added a single `_LOGGER.warning` call inside the
  existing `except` block, additive only, no control-flow change.
  `tests/regression/test_routing_safety_gate.py::test_a_detector_exception_is_logged_not_only_silently_swallowed`
  covers it and was confirmed red against the pre-fix code before being confirmed
  green, per the Phase 15 revert-and-confirm-red standard.
* Fixed one cosmetic instruction-string typo in the grief branch (a doubled-space
  spaced hyphen, "Presence first  -  witness the loss", left over from an em-dash
  conversion) that `language-and-grammar.md` already forbids in prose; harmless to
  behavior, since it never reaches shipped Markdown, but confusing to a future
  reader of the routing code.
* Investigated, and deliberately did not add, an automated contract test
  asserting that every priority-hierarchy framework has a matching
  `framework-template-map.md` detailed-structure section and
  `deep-inquiry-bank.md` question section (the pattern this session used by hand
  for Soulmate Longing and Partnership Patterns in Phase 16). Both files already
  use intentional many-to-one groupings that predate this audit: grief's 4
  subtypes share 2 template sections, Mirror's 3 variants share 1, and
  `deep-inquiry-bank.md` mixes per-framework sections with shared banks
  ("Post-Grounding Questions", "Session-Opening Questions") that do not
  correspond to any single framework. A literal 1:1 contract test would need to
  hand-encode those exceptions to avoid false failures, which moves the
  maintenance burden without removing it. Verified by hand instead: every
  `framework-template-map.md` Core mapping table `Source File` entry resolves to
  a real file under `skills/`.

Everything else the audit checked came back clean and is not listed as a finding:
Skill front matter (`license:` lives only on each category's `SKILL.md` by
design, not per content file, which `markdown-contract` already enforces
correctly), `default_skill_path`'s path resolution (every call site passes a
source-level string literal, never user or message-derived input, so path
traversal does not apply), and every `subprocess.run` call in
`src/soulmap/devtools/` (list-form arguments only, no `shell=True` anywhere in
the package).

This track added no new detector, no new framework, and no priority-hierarchy
change. It reduced one file's size by roughly 12 percent through duplication
removal, closed one production-observability gap, and fixed one string typo.

---

### Phase 18 - API documentation drift detection (complete)

A requested automatic API-documentation generation system. Reconnaissance found
`docs/engineering/API.md` already exists, and is hand-written: it explains
SoulMap's local CLI/JSON contracts in prose, with policy notes ("use only when
the product has explicit user consent") and historical corrections ("previously
labelled `INSIGHT` in older documentation") a generator cannot reconstruct. A
mechanical AST-based rewrite of that file would have destroyed real information,
exactly the failure case a strict audit is supposed to catch, not cause. Given
the choice, the narrower and safer path was chosen: detect drift against the
existing hand-written doc rather than regenerate it.

Completed:

* `src/soulmap/devtools/checks/check_api_docs.py`, a new checker in the same
  package and shape as `check_markdown_links.py` and `check_markdown_case.py`.
  It never writes to `API.md`. It statically checks two narrow, mechanical
  claims the doc makes about the Python source, both parsed from the AST, the
  module is never imported:
  * every `python -m <module>` command the doc references still exists and
    still has a `__main__` entrypoint (catches a documented module being
    renamed, moved, or losing its entrypoint)
  * every `primary_framework` value `framework_selector.py` can emit, across
    both shapes the selector uses (a literal `{"primary_framework": "X"}` dict
    and the `_simple_selection("X", ...)` helper Phase 17 introduced), is
    listed in the doc's documented output enum, and vice versa
* Deliberately did not check whether every module with a `__main__` block has
  its own doc section in `API.md`. The doc already covers the detector modules
  under `src/soulmap/runtime/detectors/` with one blanket paragraph plus a
  single example, by design, and several internal modules
  (`scope_classifier.py`, `stage_detector.py`, `conversation_synthesizer.py`,
  `markdown_contract.py`, `soulmap_demo.py`) are intentionally documented
  elsewhere or not documented individually. A literal "every entrypoint needs
  its own section" rule would have flagged all of that pre-existing, correct
  structure as broken, the same false-positive risk Phase 17 already declined
  for `framework-template-map.md` and `deep-inquiry-bank.md`.
* Running the new checker against the real repository, before any doc fix,
  found real, pre-existing drift: `API.md`'s documented `primary_framework`
  enum and "Framework name reference" table were missing 13 of the frameworks
  the router can actually emit, including both frameworks Phase 16 added.
  Fixed by updating both the enum and the table, confirmed the checker then
  passes clean. This is the revert-and-confirm-red standard applied in the
  direction that matters here: the check was proven to fire on a real,
  present-day bug, not just on synthetic fixtures.
* Wired into `soulmap check-api-docs` (a new command, `_command_table()` in
  `cli.py`) and into `soulmap lint`, so CI's existing lint job covers it with
  no new CI workflow step. Documented in `docs/engineering/DEV.md`'s new "API
  documentation drift check" section, and added to the `markdown-contract` /
  `check-links` / `check-case` command list in `AGENTS.md`, `CONTRIBUTING.md`,
  `docs/engineering/DEV.md`, and `.claude/rules/repo-workflow.md`.
* `tests/unit/test_check_api_docs.py`, 9 tests covering a clean pass, a missing
  doc, a stale module reference, a module that lost its `__main__` block, a new
  framework missing from the documented enum, a removed framework still
  documented, non-`soulmap` `python -m` references being ignored, and both CLI
  exit codes.

No Skill was added. This is a maintainer-tooling capability, not shipped
product knowledge, and no existing `.claude/skills/` workflow already covers
repository-specific drift checking in a way a new Skill would meaningfully
extend.

---

### Phase 19 - Forensic repository audit: config, permissions, tooling gaps (complete)

A requested forensic audit of the whole repository, not only `src/`: root dotfiles,
`.github/`, `.claude/`, `scripts/`, the lockfile, and dependency configuration.
Phases 13-18 already covered the runtime, tooling, knowledge files, and API docs in
depth and this pass confirmed that held (`uv lock --check`, `deptry`, `vulture`,
`pip-audit` all clean, `lefthook validate` clean, no secrets found in tracked files,
no orphaned or near-duplicate files, no empty directories). New territory this pass
actually covered: full read of all 6 workflow files and both composite actions,
`.claude/settings.json` and its hook wiring, every root dotfile, and `pyproject.toml`
in full.

Completed:

* `p-level-governance.yml` granted `pull-requests: read` for a job that never
  calls the GitHub API: `scripts/check_p_level_pr.py` reads the pull request's
  title and body entirely from the local `$GITHUB_EVENT_PATH` file GitHub Actions
  already writes to disk. Removed the unused permission grant, `contents: read`
  (needed by `actions/checkout`) is enough.
* `.claude/rules/markdown-portability.md` documents MD032 (blank lines around
  lists) as an enforced `pymarkdownlnt` rule, but `.pymarkdown.json` had it
  disabled, with no comment recording why. Tested first: enabling it against
  every tracked Markdown file surfaced exactly 2 violations, both genuine
  formatting slips, not a systemic incompatibility. Fixed both (one missing
  blank line, one spaced-hyphen line break that pymarkdown was parsing as an
  unintended list item) and enabled the rule for real, closing the gap between
  what the rule file claims and what actually runs.
* `[tool.vulture]` in `pyproject.toml` scanned only `src` and `tests`, while
  `PYTHON_SOURCE_DIR_NAMES` in `src/soulmap/devtools/support/repo.py`, the
  definition Ruff and Pyright both already use, also includes `scripts`.
  Vulture had quietly never scanned `scripts/*.py` for dead code. Added
  `scripts` to close the gap; a full run against all three directories found
  nothing, so this was a blind spot, not a backlog of unreported findings.
* `lefthook.yml`'s pre-commit hooks and `scripts/README.md`'s command list both
  still reflected the pre-Phase-18 markdown-QA trio (`markdown-contract`,
  `check-links`, `check-case`) and had not picked up `check-api-docs` from
  Phase 18, even though the 4 prose docs updated in that phase had. Added it to
  both, closing a cross-layer gap this pass's own predecessor left behind.
* Investigated, and confirmed already correctly handled: `.claude/skills/README.md`'s
  index lists exactly the 22 skill directories present on disk, no drift.
  `renovate.json` and `.github/dependabot.yml` configure two overlapping
  dependency-update tools; `docs/operations/dependency-refresh.md` already
  documents this as a known, deliberately unresolved overlap that is the
  repository owner's call, not routine maintenance, so this pass did not
  reopen it. `autofix.yml`'s `contents: read` permission alongside a job that
  pushes commits is correct, not a misconfiguration: `autofix-ci/action` pushes
  through its own GitHub App installation, not the workflow's own token.
* Flagged, not removed: `.whitesource` (Mend/WhiteSource scanning configuration)
  has no mention anywhere in the repository's documentation and no matching
  check has appeared on any pull request observed across this session, while
  Socket Security's checks appear on every one, suggesting the app behind this
  config may no longer be installed. This is circumstantial, not confirmed, an
  installed-GitHub-App state this pass has no tool to query directly. Left in
  place; the repository owner can confirm and remove it if the app is
  genuinely gone.

This track added no new dependency, no new workflow, and no architectural
change. It closed 4 small, evidence-backed drift and permission gaps and
converted one previously-undocumented "why is this disabled" config question
into either a fix or a recorded, deliberate non-finding.

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
* Doctrine ↔ Markdown contract consistency (SOULMAP.md vs skills/)
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
| Framework combination (two active primary frameworks) | Violates `SOULMAP.md` doctrine; makes routing and testing ambiguous |
| Dynamic language expansion without static phrase review | Crisis detection requires human authorship, not automated translation |
| Python-generated response content | Violates the knowledge-first architecture; content belongs in Markdown |
| Per-language framework routing | Framework selection is language-unaware by design |
| Markdown-loaded crisis detection | Protected-module policy; no pending safety evaluation evidence |

### Open, tracked future work

* Maintain human-reviewed deterministic regression evidence for newly
  observed response-safety phrasing gaps
* Platform adapters beyond the current Claude-first flow
* Close the 2 `partial` rows Phase 14 found were real, closable gaps rather
  than bounded by the missing response generator:
  * a Python scanner for the "Epistemic guardrails" row, shaped like
    `response_safety_contract.py`, flagging numerology, chakra, or karma
    language that presents certainty, identity, or destiny as fact, backed by
    curated positive and near-miss evidence the same way every other detector
    in the matrix was
  * a hard per-mode length ceiling in `response_contract.py` for the "Stage-
    appropriate response depth" row (the emotional-versus-intellectual
    register distinction within a mode stays genuinely bounded, since telling
    those apart is a content judgment)
* Decide [ADR 0003](../docs/engineering/adr/0003-bounded-edit-distance-crisis-backstop-proposal.md),
  the bounded edit-distance crisis backstop. It remains `Proposed` and
  authorizes nothing. Moving it to `Accepted` needs a multilingual regression
  corpus, a reviewed exclusion list, a separate approach for Chinese, and
  maintainer sign-off, none of which an implementation pass can supply on its
  own. The complementary path the ADR names, adding reviewed misspelling
  variants as literal patterns, stays open under the existing ADR 0002
  maintenance allowance and needs no new decision

---

## Success Metrics

| Area              | Direction                                              |
| ------------------ | -------------------------------------------------------- |
| Safety enforcement  | Keep every `safety-enforcement-matrix.md` row backed by its stated evidence, and keep no row at `partial` for a reason inside the package's own scope. `bounded` rows are at their ceiling by design, not backlog; the 2 `partial` rows are real, tracked, open work |
| Eval coverage       | Maintain 0 `failed_checks` across eval-groups and eval-markdown-contracts |
| Test coverage       | Hold the package at the `runtime/detectors/` bar (97%). `runtime/guards/` and `devtools/` reached it, so the remaining uncovered lines are platform-specific imports, `__main__` guards, and defensive fallbacks |
| Knowledge integrity | Zero orphaned config constants in `audit-knowledge`      |
| Documentation       | Doctrine, safety, packaging, and public claims stay one consistent story |
| Distribution        | Keep all four documented platform integrations current with `SOULMAP.md` |

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

Last updated: August 30, 2026
