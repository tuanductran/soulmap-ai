# Maintenance Boundary

This document defines what SoulMap AI should keep stable, what should remain optional,
and what should not be expanded without a clear trigger.

The goal is to protect the project from slow drift, unnecessary complexity, and
maintenance load that exceeds the project's real use case.

## Core that must stay stable

These parts are the heart of the project and should remain the primary maintenance
focus:

- `SOULMAP.md` as the baseline behavioral, safety, and shipped-package contract
- `skills/` as the core shipped knowledge base
- `src/soulmap/runtime/routing/framework_selector.py` and the existing detector stack
- `src/soulmap/runtime/guards/response_safety_gate.py` (both files' independent
  crisis-detection call sites are a deliberate defense-in-depth pair, not
  duplication to consolidate - see
  [`docs/engineering/adr/0001-layered-crisis-detection.md`](adr/0001-layered-crisis-detection.md))
- `src/soulmap/runtime/guards/response_contract.py`
- `src/soulmap/runtime/guards/resource_sanitizer.py`
- the current packaging flow for `dist/soulmap-ai.zip` and `dist/soulmap-ai.skill`
  including the `.claude-plugin/` boundary between them
- the current test and Markdown contract suite

If a change weakens clarity, safety, or consistency in these areas, treat it as a high
priority problem.

## What counts as optional

These areas can exist, but must remain clearly secondary to the core:

- experimental modules such as `src/soulmap/runtime/experimental/biometric_ingest.py`
- experimental modules such as `src/soulmap/runtime/memory/memory_ledger.py`
- spiritual or symbolic extensions that sit outside the main product promise
- local workflow assets under `.claude/`
- future platform adapters beyond the current Claude-first flow

Optional layers must never make the repo harder to understand than the core itself.

## The public website exception

A statically generated public website is permitted, as a scoped exception
approved by the repository owner on 2026-08-30 under the "Valid triggers for
expansion" rule below: it serves a distribution need and has a named owner.

The exception is bounded. The website may:

- generate static HTML at build time from canonical repository files
- publish only documents named in the website allowlist, see
  [`../web/CONTENT-MODEL.md`](../web/CONTENT-MODEL.md)
- explain routing, safety, and architecture in public prose

The website may not:

- run a server, expose an HTTP API, or execute any part of
  `src/soulmap/runtime/` at request time
- store user data, set tracking cookies, or add analytics
- introduce accounts, authentication, or any account-shaped state
- publish detection phrases, internal prompts, or refusal templates
- become a conversational or reflective interface

If a future change needs any of the second list, it is a new decision requiring
its own trigger and its own ADR, not an extension of this exception.

## What not to add by default

Do not add these unless there is a real, current need:

- a public API service
- a database layer
- authentication or user account systems
- background jobs or infra-heavy deployment logic
- multiple platform adapters for tools you are not actively using
- new frameworks that are not required by the current SoulMap doctrine
- extra docs that only restate what is already clear elsewhere

The default answer to new scope should be "not yet."

## Valid triggers for expansion

A new surface or feature is justified only when at least one of these is true:

- it solves a real blocker in the current workflow
- it supports an active user or distribution need
- it protects an important safety or quality contract
- it materially improves clarity, portability, or maintainability
- it has a specific owner and a realistic maintenance path

If none of these are true, do not add it.

## Decision rules

Before adding a new module, document, workflow, or surface, ask:

1. Does this make SoulMap clearer or just bigger?
2. Does this support the current Claude-first use case?
3. Will this require new tests, docs, and release maintenance?
4. If this breaks in three months, will I still want to own it?

If the answer to the first two is weak, or the answer to the last two is "no," do not
add it.

## Preferred Direction

When in doubt, choose:

- polish over expansion
- clarity over breadth
- stronger tests over more features
- cleaner docs over more docs
- one excellent artifact over many partial ones

## Maintenance Standard

A change is worth keeping when it does at least one of these:

- reduces ambiguity
- reduces risk
- reduces manual effort
- improves the artifact users actually consume
- strengthens the project's public coherence

If a change adds surface area without doing one of those things, it should usually be
rejected.

## Practical rule of thumb

For SoulMap AI, the project is already good enough when:

- the doctrine is clear
- the safety posture is intact
- the main artifact builds
- the tests pass
- the docs do not drift

Everything beyond that is optional unless a real use case proves otherwise.
