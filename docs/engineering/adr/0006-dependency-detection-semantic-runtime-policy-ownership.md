---
status: Accepted
date: 2026-11-17
supersedes: ADR 0005 (current dependency-ownership boundary only)
---

# ADR 0006: Dependency Detection Semantic and Runtime Policy Ownership

## Status

Accepted. This ADR records the dependency detector ownership boundary already
implemented on `main`. It supersedes the ownership statements in ADR 0005
where they conflict with the current implementation; ADR 0005 remains an
immutable historical record of the original migration decision.

## Context

ADR 0005 recorded the completion of the migration that established
`skills/safety/dependency-detection.md` as the canonical dependency knowledge
source. Its original wording also stated that scoring weights and thresholds
were loaded from Markdown and that no dependency-specific knowledge should be
added to Python configuration.

The current implementation has since separated semantic source material from
executable runtime policy. The old ADR wording no longer accurately describes
that boundary and can direct maintainers to edit the wrong owner.

This clarification documents the existing architecture only. It does not
authorize a detector, threshold, routing, or safety behavior change.

## Decision

The canonical Markdown source for dependency semantic knowledge is:

`skills/safety/dependency-detection.md`

Markdown owns:

- dependency signal groups and keywords;
- decision-seeking phrases;
- isolation and context-exclusion cues;
- dependency regex expressions;
- response and recommendation guidance.

Python owns executable dependency policy in
`src/soulmap/runtime/knowledge/runtime_config.py`, including:

- scoring weights and detection thresholds;
- context-exclusion policy switches;
- clause-boundary rules used by the detector.

The Python runtime resolves and loads the Markdown source through the
Python-owned runtime source registry. It parses and normalizes semantic
knowledge, then applies the Python-owned executable policy to score, route,
validate, and enforce the result.

Markdown must not duplicate Python-owned numeric policy or machine-facing
runtime configuration. Conversely, semantic phrases, regex expressions,
context cues, and user-facing guidance must not be moved into Python merely
because the runtime consumes them.

Future changes to dependency semantics belong in
`skills/safety/dependency-detection.md`. Changes to scoring, thresholds,
context-policy switches, or clause-boundary execution behavior belong in
`src/soulmap/runtime/knowledge/runtime_config.py`. Both require the
corresponding runtime and regression tests.

## Rationale

Dependency handling is safety-sensitive. Keeping semantic source material and
executable policy in explicit, single-owner locations reduces drift while
preserving the ability to review and test each responsibility independently.

This boundary matches the current detector imports and Markdown source loader,
the November 2026 ownership follow-up, and the repository's knowledge-first
architecture. It does not move knowledge or alter detector behavior.

## Alternatives Considered

### Edit ADR 0005 in place

Rejected because accepted ADRs are immutable under
`docs/engineering/known-limitations.md` and the ADR directory contract.
Historical decisions must remain auditable; changed decisions are recorded in
a new, explicitly superseding ADR.

### Keep the original ownership wording as current guidance

Rejected because the original scoring/threshold ownership statement no longer
matches the runtime configuration consumed by the detector.

### Move all dependency data into Python

Rejected because semantic phrases, regex expressions, context cues, and
response guidance are canonical Markdown knowledge and should remain
maintainable in the shipped knowledge surface.

## Consequences

- ADR 0005 remains unchanged as the historical record of the original migration.
- ADR 0006 is the current ownership reference for dependency semantic knowledge
  and executable runtime policy.
- Markdown remains the canonical owner of dependency semantics and guidance.
- Python remains the canonical owner of executable scoring and context policy.
- No runtime, detector, threshold, routing, crisis, or safety behavior changes
  are authorized by this documentation decision.
