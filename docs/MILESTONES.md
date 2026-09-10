# SoulMap AI - Completed Milestones

> **Repository:** [soulmap-ai](https://github.com/tuanductran/soulmap-ai)
> **Purpose:** Historical record of completed roadmap phases and milestones.
> **Current roadmap:** [ROADMAP.md](ROADMAP.md)

This file records completed project milestones. It is historical context, not an active
work queue. Detailed engineering evidence remains in the relevant ADRs, audits, research
notes, tests, and release records.

---

## Completed Phases

| Phase | Milestone | Outcome |
| --- | --- | --- |
| 1 | Foundation | Established doctrine, package contract, initial shipped skill structure, and core safety templates. |
| 2 | QA Hardening & Grouped Eval Harness | Added grouped evals, red-team hardening, shared tooling, build flags, hooks, and CI workflow hardening. |
| 3 | Content Gap Closure & Central Orchestration | Established central orchestration, first-session behavior, framework expansion, and knowledge/config synchronization. |
| 4 | Brand & Numerology Enrichment | Enriched founder/brand material while separating user-facing content from implementation details and hardened CI. |
| 5 | Framework Expansion & QA Closure | Shipped additional frameworks and stabilized the development toolchain and Markdown quality. |
| 6 | Knowledge Migration & Audit Tooling | Moved detector knowledge toward Markdown as the source of truth and added repository knowledge auditing. |
| 7 | Response Safety & Multilingual Crisis Detection | Added response-safety contracts, multilingual crisis detection, and Markdown-aware safety validation. |
| 8 | Test Coverage Hardening | Raised detector, guard, synthesis, audit, eval, packaging, and tooling coverage to the project targets. |
| 9 | Knowledge, Routing & Synthesis Alignment | Routed the remaining spiritual frameworks and aligned synthesis, activation targets, session guidance, and release-time coverage. |
| 10 | Deterministic Response-Safety Governance | Established the deterministic safety-gate regression model, multilingual morphology coverage, and identity-boundary enforcement. |
| 11 | Platform & Distribution Expansion - foundation | Established versioned platform integration contracts, distribution manifests, and release metadata; remaining platform work is conditional. |
| 12 | Toolchain Support & Test Reproducibility | Completed toolchain compatibility research, deterministic diagnostics, local CI installers, and CLI wrapper coverage. |
| 13 | Repo-wide Hardening Pass | Closed runtime, safety, knowledge, testing, release, and documentation gaps identified by the full v0.9.1 audit. |
| 14 | Enforcement Ceiling Clarity | Distinguished package-enforceable rules from intentional host-layer boundaries and formalized `bounded` enforcement. |
| 15 | Regression-strength Verification | Added curated mutation tests and the revert-and-confirm-red standard for safety-critical regression tests. |
| 16 | Soulmate Skill Layer | Added the soulmate skill category, soulmate/partnership routing, supporting knowledge, and corresponding contract coverage. |
| 17 | Post-Phase-16 Audit | Removed routing duplication, improved detector failure observability, and completed a strict repository audit without changing routing semantics. |
| 18 | API Documentation Drift Detection | Added contract coverage for API documentation drift and integrated the checker into the repository validation surface. |
| 19 | Forensic Repository Audit | Audited repository configuration, permissions, tooling, lockfile, automation, and non-`src/` surfaces for hidden gaps. |
| 20 | Shipped-Skills Reference Boundary | Closed a shipped-skill reference gap where boundary validation did not cover a repository-only surface. |
| 21 | Competitive Evolution Audit | Reviewed external AI/agent patterns and deliberately retained the existing architecture where no missing capability justified adoption. |
| 22 | Shipped-Package Boundary | Audited and tightened the boundary between repository-only material and the shipped package. |
| 23 | Dead-Code Audit | Audited for unused code and retained only intentional surfaces, with no unsupported cleanup introduced. |
| 24 | Research & Audit Tooling | Consolidated research/audit findings into repository-native evidence and process guidance rather than adding speculative runtime features. |
| 25 | Safety Matrix Closure | Resolved the remaining safety-matrix status gaps; the matrix now distinguishes enforced, bounded, and guidance-only rules without open `partial` rows. |
| 26 | Tiered Trusted Sources | Established tiering for trusted sources and aligned source governance with SoulMap's epistemic and safety doctrine. |

---

## Current Historical Baseline

The completed roadmap work through Phase 26 establishes the current v0.9.1 architecture and
its boundaries. The project deliberately does not treat the following as completed or
implicitly committed work:

- third-party platform deployment claims without operator evidence;
- additional platform adapters unless a platform-specific workstream is justified;
- model-based runtime safety classification without a superseding ADR;
- persistent personal-memory infrastructure, RAG, MCP discovery, or digital-twin behavior
  unless a new architectural decision explicitly revisits those boundaries.

For rule-level safety status, use
[`engineering/safety-enforcement-matrix.md`](engineering/safety-enforcement-matrix.md).
For intentional boundaries and non-goals, use
[`engineering/known-limitations.md`](engineering/known-limitations.md).
For architecture decisions, use [`engineering/adr/`](engineering/adr/).
For detailed research and audit evidence, use [`research/`](research/).
