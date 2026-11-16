---
status: Accepted
date: 2026-09-29
---

# ADR 0005: Dependency Detection Knowledge Boundary

## Status

Accepted.

## Context

SoulMap uses Markdown as the source of truth for shipped knowledge and keeps Python
focused on deterministic runtime enforcement. Runtime detectors resolve their
signals and routing contracts through the Python-owned runtime source registry,
while the semantic content remains in canonical Markdown sources.

The dependency detector was previously a protected legacy boundary. Its dependency
signals, regex patterns, thresholds, and guidance were maintained in Python safety
configuration while related dependency vocabulary was documented in Markdown.
Issue #524 tracked the migration required to establish a single canonical
knowledge surface without changing detector behavior.

## Decision

The dependency detector migration is complete.

The canonical dependency knowledge source is:

`skills/safety/dependency-detection.md`

The Python runtime now resolves that source through the Python-owned runtime source
registry and loads the following knowledge directly from the Markdown source:

- dependency keywords;
- decision-seeking phrases;
- isolation signals;
- dependency regex patterns;
- scoring weights and thresholds;
- dependency guidance.

The runtime implementation is responsible for loading, parsing, normalizing, scoring,
routing, and enforcing the knowledge. It must not duplicate the dependency signal
lexicon, regex patterns, thresholds, or recommendation wording.

The migration is considered complete only because the runtime source, registry
mapping, deterministic Markdown loaders, and dependency detector now operate through
the canonical source. The protected legacy dependency knowledge surface in
`src/soulmap/runtime/config/safety.py` is no longer the detector's source of truth.

No new dependency-specific knowledge should be added to Python configuration.
Changes to dependency semantics must be made in the canonical Markdown source and
covered by the corresponding runtime/regression tests.

## Rationale

Dependency handling is safety-sensitive. Moving the data without a compatibility
contract could silently change detection coverage, thresholds, or escalation
behavior.

The completed migration follows the intended order:

1. establish the canonical Markdown source;
2. define the runtime contract;
3. register the source in the Python-owned runtime registry;
4. load and parse the source deterministically;
5. validate dependency regression coverage;
6. migrate the detector to the canonical source;
7. remove the obsolete Python knowledge dependency from the detector path.

Issue #524 was the execution path for this migration.

## Alternatives Considered

### Immediate extraction

Rejected as the initial migration strategy. It would have changed a
safety-sensitive boundary without first establishing a canonical source and
compatibility contract.

### Keep the duplicate indefinitely

Rejected. It preserves semantic drift and contradicts the knowledge-first
architecture.

### Add only a drift test

Insufficient. A drift test would preserve two sources of truth rather than establish
one canonical source.

## Consequences

- Dependency detection knowledge now has one canonical Markdown source.
- Runtime Python remains responsible for deterministic execution rather than semantic
  authorship.
- The dependency detector can continue to use stable runtime loading and registry
  contracts without maintaining a second knowledge copy.
- Future contributors should edit
  `skills/safety/dependency-detection.md` for dependency semantics and use Python
  only for runtime behavior, parsing, validation, and enforcement.
- The former protected-legacy exception described by this ADR no longer applies.
