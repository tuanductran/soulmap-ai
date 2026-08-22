# Architecture Decision Records

This directory holds permanent Architecture Decision Records (ADRs) for
SoulMap AI. An ADR captures a significant architectural decision, its
context, and its rationale, so future contributors do not have to
reconstruct "why" from PR discussion or issue history.

An ADR is appropriate when a decision:

- would otherwise only be discoverable from a closed issue or PR review,
- is easy for a future contributor to accidentally reverse because it looks
  like redundant or simplifiable code, or
- trades off competing concerns (safety, maintainability, performance) in a
  way that is not obvious from reading the code alone.

ADRs are documentation-only. Writing one does not itself authorize a
runtime, routing, or behavior change; it records a decision about the
architecture as it already exists, or as it has already been agreed to
change through the normal contribution process.

## Format

Each ADR follows this structure:

- Status (Proposed, Accepted, Superseded)
- Context
- Decision
- Rationale
- Alternatives Considered
- Consequences

Number ADRs sequentially, zero-padded to four digits:
`NNNN-short-kebab-case-title.md`.

## Index

| ADR | Title | Status |
| --- | --- | --- |
| [0001](0001-layered-crisis-detection.md) | Layered Crisis Detection as Intentional Defense-in-Depth | Accepted |
| [0002](0002-deterministic-response-safety-enforcement.md) | Deterministic Response Safety Enforcement | Accepted |
| [0003](0003-soulmate-library-soulmap-framework.md) | Soulmate Library as the Foundation for the SoulMap Framework | Accepted |
