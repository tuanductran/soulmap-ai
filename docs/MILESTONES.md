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
| 27 | v0.14.0 Audit & Release Integrity | Added review-only Python/resource reachability inventories, stale-path and detector-knowledge drift checks, incomplete-scan reporting, relative-import resolution, and Docker Action workspace trust; verified release finalization, cross-platform CI, Python compatibility, and CodeQL. |
| 28 | Audit False-Positive Reduction & Reference Repair | Reduced confirmed stale-path and Markdown-reference audit false positives; included CLI, Docker Action, and P-level governance entrypoints in reachability analysis; corrected stale maintainer rule paths and a deleted-module docstring reference. The follow-up inventory found no actionable source deletion; the docstring-only `safety.py` remains review-only and is retained. |

## Post-Merge Audit Verification

The canonical inventory jobs ran in [CI run 38692440277](https://github.com/tuanductran/soulmap-ai/actions/runs/38692440277) on PR #679 commit `2401299fc71d6e16fa8dff9330451537c037b58d`, a documentation-only branch based on post-merge `main` at `3e4b279207c956b9a5df795be874df6c61d16cd0`. The runtime and audit implementation matched `main`; the full-history scan also included the documentation-branch commits. The report artifact is `soulmap-knowledge-inventory`.

- Knowledge inventory: 11 safety-protected overlaps; zero exact detector/Markdown overlaps; 15 active config constants and zero orphaned constants; zero Markdown implementation-reference findings.
- Python reachability: 99 reachable modules and one review-only candidate, `src/soulmap/runtime/config/safety.py`. It contains no runtime constants, but remains referenced by architecture/tests and is retained; reachability alone is not proof of safe deletion.
- Resource inventory: no missing resource targets or incomplete-scan marker; 5 eval datasets, 17 internal templates, 10 maintainer prompts, 13 maintainer rules, 23 maintainer skills, 2 plugin metadata files, 78 shipped-knowledge files, and 46 supporting documents. Unreferenced resources remain review-only.
- Current-branch consistency audit: zero deleted paths/directories examined and zero path/directory candidates because the PR contains documentation-only changes.
- Full-history audit: 140 deleted paths and 38 deleted directories examined; 24 path candidates, 10 directory candidates, and 2 comment candidates. Manual classification found the remaining path hits to be historical changelog references, test fixtures/negative guards, basename-only matches to relocated/current files, or supporting-document references. The directory hits describe an intentionally absent product-level source folder, a historical pre-package layout, and a shell-rule glob. The two comment candidates explain test intent. No additional source deletion or runtime change was justified.

The audit artifacts are review evidence, not a deletion list. Reopen this workstream only if a later source, entrypoint, packaging, or knowledge change produces new actionable findings.

## Current Historical Baseline

Phases 1-28 record the current architecture and audit work through the v0.14.0 release
and the follow-up false-positive/reference fixes. Post-merge canonical audit verification
remains active work in [`ROADMAP.md`](ROADMAP.md). The v0.14.0 release adds stronger review-only repository
inventories and makes incomplete audit scans visible without weakening the project's
knowledge-first, deterministic-safety, and package-boundary rules. The project deliberately
does not treat the following as completed or implicitly committed work:

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
