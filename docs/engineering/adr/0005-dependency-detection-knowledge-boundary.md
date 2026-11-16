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

The Python runtime resolves that source through the Python-owned runtime source
registry and loads the semantic knowledge from Markdown, including:

- dependency signal groups and keywords;
- decision-seeking phrases;
- isolation and context-exclusion cues;
- dependency regex expressions;
- response and recommendation guidance.

Executable policy remains Python-owned in
`src/soulmap/runtime/knowledge/runtime_config.py`, including:

- scoring weights and detection thresholds;
- context-exclusion policy switches;
- clause-boundary rules used by the detector.

The runtime implementation is responsible for loading, parsing, normalizing,
scoring, routing, validating, and enforcing this knowledge and policy. Markdown
must not become a duplicate store for Python-owned numeric policy or machine-facing
runtime configuration. Conversely, semantic phrases, regex expressions, context
cues, and user-facing guidance must not be moved into Python merely because the
runtime consumes them.

The migration is considered complete because the runtime source, registry mapping,
deterministic Markdown loaders, executable Python policy, and dependency detector
operate through this explicit ownership boundary. The protected legacy dependency
knowledge surface in `src/soulmap/runtime/config/safety.py` is no longer the
detector's source of truth.

Changes to dependency semantics must be made in the canonical Markdown source.
Changes to scoring, thresholds, context-policy switches, or clause-boundary
execution behavior must be made in the Python runtime configuration. Both kinds
of changes require the corresponding runtime and regression tests.

## Rationale

Dependency handling is safety-sensitive. Moving semantic data or executable policy
without a compatibility contract could silently change detection coverage,
thresholds, or escalation behavior.

The completed migration follows the intended order:

1. establish the canonical Markdown source for semantic dependency knowledge;
2. define the runtime contract;
3. register the source in the Python-owned runtime registry;
4. load and parse the source deterministically;
5. keep executable scoring and context policy in Python runtime configuration;
6. validate dependency regression coverage;
7. migrate the detector to the canonical source and remove the obsolete Python
   semantic-knowledge dependency from the detector path.

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

- Dependency semantic knowledge has one canonical Markdown source.
- Executable scoring weights, thresholds, context-policy switches, and
  clause-boundary rules have one Python runtime configuration owner.
- Runtime Python remains responsible for deterministic execution rather than
  semantic authorship.
- The dependency detector uses stable runtime loading and registry contracts
  without maintaining a second semantic-knowledge copy.
- Future contributors should edit
  `skills/safety/dependency-detection.md` for semantic signals, regex expressions,
  context cues, and guidance; use
  `src/soulmap/runtime/knowledge/runtime_config.py` for executable scoring and
  context policy.
- The former protected-legacy exception described by this ADR no longer applies.
