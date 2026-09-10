# SoulMap AI - Project Roadmap

> **Repository:** [soulmap-ai](https://github.com/tuanductran/soulmap-ai)
> **Maintainer:** Tuan Duc Tran
> **License:** see [LICENSE](../LICENSE)
> **Current release:** v0.11.0
> **Last updated:** September 10, 2026

This document is the **living roadmap** for SoulMap AI. It describes work that is still
planned, conditional, or intentionally deferred. Completed phases and historical outcomes
belong in [`MILESTONES.md`](MILESTONES.md), not here.

---

## Roadmap Principles

- Keep this file forward-looking: no completed phase inventories or historical validation logs.
- Treat GitHub Issues as the execution queue for concrete implementation work.
- Do not turn an architectural non-goal into roadmap work without a new ADR.
- Keep knowledge-first architecture intact: Markdown remains the source of truth for shipped
  knowledge and detection phrases; Python remains a thin enforcement and tooling layer.
- Safety changes remain deterministic and evidence-driven unless a superseding ADR explicitly
  changes that boundary.

---

## Current Roadmap

### Platform & Distribution Expansion

**Status:** Conditional / blocked by external platform readiness.

The repository has the foundation for Claude-first distribution plus documented ChatGPT,
Gemini, and Poe integration surfaces. The remaining work should only become an active
implementation track when there is a real deployment owner and a configured platform
integration to validate.

Potential work:

- Add additional platform adapters where a concrete deployment requirement justifies them.
- Run live integration acceptance tests for Claude, ChatGPT, Gemini, and Poe when the
  corresponding deployment surfaces are active.
- Record operator acceptance evidence without claiming that repository tests prove
  third-party deployment behavior.

This work remains intentionally outside the current package-only execution scope until the
external prerequisites exist.

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
