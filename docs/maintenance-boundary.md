# Maintenance Boundary

This document defines what SoulMap AI should keep stable, what should remain optional,
and what should not be expanded without a clear trigger.

The goal is to protect the project from slow drift, unnecessary complexity, and
maintenance load that exceeds the project's real use case.

## Core That Must Stay Stable

These parts are the heart of the project and should remain the primary maintenance
focus:

- `AGENTS.md` as the main behavioral and safety contract
- `skills/` and `templates/` as the core knowledge base
- `modules/framework_selector.py` and the existing detector stack
- `modules/response_safety_gate.py`
- `modules/response_contract.py`
- `modules/resource_sanitizer.py`
- the current packaging flow for `dist/soulmap-ai.zip`
- the current test and markdown contract suite

If a change weakens clarity, safety, or consistency in these areas, treat it as a high
priority problem.

## What Counts As Optional

These areas can exist, but must remain clearly secondary to the core:

- experimental modules such as `modules/biometric_ingest.py`
- experimental modules such as `modules/memory_ledger.py`
- spiritual or symbolic extensions that sit outside the main product promise
- local workflow assets under `.claude/`
- future platform adapters beyond the current Claude-first flow

Optional layers must never make the repo harder to understand than the core itself.

## What Not To Add By Default

Do not add these unless there is a real, current need:

- a web app or full website
- a public API service
- a database layer
- authentication or user account systems
- background jobs or infra-heavy deployment logic
- multiple platform adapters for tools you are not actively using
- new frameworks that are not required by the current SoulMap doctrine
- extra docs that only restate what is already clear elsewhere

The default answer to new scope should be "not yet."

## Valid Triggers For Expansion

A new surface or feature is justified only when at least one of these is true:

- it solves a real blocker in the current workflow
- it supports an active user or distribution need
- it protects an important safety or quality contract
- it materially improves clarity, portability, or maintainability
- it has a specific owner and a realistic maintenance path

If none of these are true, do not add it.

## Decision Rules

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

## Practical Rule Of Thumb

For SoulMap AI, the project is already good enough when:

- the doctrine is clear
- the safety posture is intact
- the main artifact builds
- the tests pass
- the docs do not drift

Everything beyond that is optional unless a real use case proves otherwise.
