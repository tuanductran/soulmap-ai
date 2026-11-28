# SoulMap AI - Project Roadmap

> **Repository:** [soulmap-ai](https://github.com/tuanductran/soulmap-ai)
> **Maintainer:** Tuan Duc Tran
> **License:** MIT
> **Status:** Actively maintained
> **Baseline reviewed:** v0.15.1, published 2026-11-21.
> **Baseline commit:** `400b5bd8a9a40aa89b23656b45dec3223bc68b78`.

This document is the **living roadmap** for SoulMap AI. It describes work that is still
planned, conditional, or intentionally deferred. Completed phases and historical outcomes
belong in [`MILESTONES.md`](MILESTONES.md), not here.

---

## Roadmap Principles

- Keep this file forward-looking: no completed phase inventories or historical validation logs.
- Treat GitHub Issues as the execution queue for concrete implementation work.
- Do not turn an architectural non-goal into roadmap work without a new ADR.
- Keep the knowledge-first architecture intact: Markdown is the source of truth for semantic
  knowledge and qualitative guidance; Python owns executable configuration and executes,
  normalizes, routes, validates, and enforces that knowledge.
- Safety changes remain deterministic and evidence-driven unless a superseding ADR explicitly
  changes that boundary.

---

## Current Roadmap

### Platform & Distribution Expansion

**Status:** Conditional / blocked by external platform readiness.

Claude is the primary supported integration surface. The repository maintains a Claude Code
plugin manifest, Claude.ai Custom Skills packaging guidance, and a portable Markdown ZIP
for assistants that can read the source knowledge. Other AI services are linked as optional
destinations only; they are not first-class integration targets and have no platform-specific
setup or acceptance claims.

Potential work:

- Keep the Claude Code plugin manifest, Skill entrypoint, and release metadata synchronized.
- Validate plugin loading and Skill behavior against the current Claude interfaces.
- Record live Claude acceptance evidence separately from repository tests; a successful
  build does not prove that a third-party service has accepted or executed the Skill.

Do not add other platform adapters unless a concrete deployment requirement and maintainer
decision explicitly change this Claude-first scope.

---

### Safety & Governance Maintenance

**Status:** Ongoing maintenance, not a feature backlog.

- Add deterministic safety patterns only for documented, human-reviewed phrasing gaps.
- Preserve positive and near-miss regression coverage for every safety expansion.
- Keep the safety-enforcement matrix synchronized with implementation and eval evidence.
- Keep ADR references synchronized whenever the safety architecture changes.
- Revisit the enforcement boundary only through a superseding ADR with explicit evidence.

---

### Toolchain & Dependency Maintenance

**Status:** Ongoing maintenance.

- Apply the dependency-refresh and advisory-review process when upstream changes create a
  concrete maintenance trigger. Follow the [dependency refresh checklist](operations/dependency-refresh.md)
  for the operational sequence and evidence requirements.
- Keep lockfile, CI, compatibility research, and repository contracts synchronized.
- Preserve reproducible pytest diagnostics and the full repository validation gate.
- Avoid adding dependencies or scanners without a documented problem they solve.

---

### Knowledge & Framework Evolution

**Status:** Demand-driven.

New frameworks, content, routing, or orchestration changes should enter the roadmap only
when a concrete knowledge gap is demonstrated by research, evaluation, user need, or a
maintainer decision.

Any new framework must preserve the existing knowledge-first model and reuse the shared
routing, template, question-bank, and safety infrastructure rather than creating a parallel
architecture.

---

### Architecture Reassessment

**Status:** Deferred until a concrete requirement appears.

The project does not currently commit to persistent personal-memory infrastructure, RAG,
MCP-based tool discovery, digital-twin behavior, or model-based runtime safety classification.
These remain architectural boundaries/non-goals unless a new ADR establishes a specific
need, scope, privacy model, reproducibility model, and rollback path.

---

## Definition of Roadmap Completion

A roadmap item is considered complete only when the repository contains the required
implementation/evidence and the relevant validation gates pass. Once complete, the historical
record moves to [`MILESTONES.md`](MILESTONES.md) or the more specific engineering/research
document rather than remaining in this file.

---

## Related Documents

- [`MILESTONES.md`](MILESTONES.md) - completed phases and historical outcomes
- [`engineering/safety-enforcement-matrix.md`](engineering/safety-enforcement-matrix.md) - current rule-level safety enforcement
- [`engineering/known-limitations.md`](engineering/known-limitations.md) - intentional boundaries and non-goals
- [`engineering/adr/`](engineering/adr/) - architectural decisions
- [`research/`](research/) - research and audit evidence
- GitHub Issues - active implementation and execution tracking
