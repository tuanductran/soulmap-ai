---
status: Accepted
date: 2026-09-29
---

# ADR 0005: Dependency Detection Knowledge Boundary

## Status

Accepted.

## Context

SoulMap uses Markdown as the source of truth for shipped knowledge and keeps Python
focused on deterministic runtime enforcement. Most runtime detectors now resolve
their signals and routing contracts through `src/soulmap/runtime/source_registry.py`.

The dependency detector is a remaining legacy boundary. It imports
`DEPENDENCY_KEYWORDS`, `DECISION_SEEKING`, `ISOLATION_SIGNALS`, and dependency
thresholds from `src/soulmap/runtime/config/safety.py`. It also contains two
dependency-specific regular expressions in Python.

The same dependency signal vocabulary is also documented in
`skills/safety/boundaries-safety.md`. This creates two semantic surfaces that can
drift.

## Decision

Treat the current dependency detector as a **protected legacy boundary** until a
dedicated migration is completed.

The migration must establish a dedicated Markdown runtime source, register it in
the runtime source registry, provide a deterministic loader/parser, and prove
behavioral equivalence before removing the legacy knowledge dependency from
`safety.py`.

No opportunistic change may modify the protected dependency constants in
`safety.py` merely to make the detector appear knowledge-first.

Issue #524 tracks the migration.

## Rationale

Dependency handling is safety-sensitive. Moving the data without first establishing
a canonical source and compatibility contract could silently change detection
coverage, thresholds, or escalation behavior.

The correct order is:

1. establish the canonical Markdown source;
2. define the runtime contract;
3. validate registry and loader behavior;
4. run dependency regression coverage;
5. migrate the detector;
6. remove the obsolete Python knowledge surface only after equivalence is proven.

## Alternatives Considered

### Immediate extraction

Rejected. It would create a behavior change and modify the protected safety boundary
without a compatibility contract.

### Keep the duplicate indefinitely

Rejected. It preserves semantic drift and contradicts the knowledge-first architecture.

### Add only a drift test

Insufficient. A drift test would preserve two sources of truth rather than establish
one canonical source.

## Consequences

- The current dependency detector remains unchanged and behaviorally stable.
- The architectural exception is explicit and discoverable.
- Future contributors have a defined migration boundary instead of copying or editing
  dependency signals in additional locations.
- Issue #524 is the execution path for completing the migration.
