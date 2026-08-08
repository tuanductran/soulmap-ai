---
title: "SoulMap AI, Library vs Framework boundary"
description: "Defines which runtime modules are the reusable Library layer and which are the swappable Framework layer, and the rule for building new frameworks on top of the Library instead of duplicating it."
---

# Library vs Framework boundary

This document names a distinction that already exists implicitly in
`src/soulmap/runtime/` and makes it explicit, the same way
[`repo-contract.md`](repo-contract.md) makes the top-level repo shape explicit.

It does not move, rename, or restructure anything. It is a naming and
authoring-rule document layered on top of the existing structure defined in
[`repo-contract.md`](repo-contract.md).

## The analogy

The same relationship that exists between a UI library (React) and an
application framework built on it (Next.js) already exists inside SoulMap:

- **Library** - the reusable substrate every framework depends on. Stable,
  domain-agnostic, changes rarely.
- **Framework** - one reflective knowledge module (grief, anger, existential,
  pattern-mapper, ...) plus its detector. New ones ship often, each one is
  swappable/removable without touching the Library.

A new framework should never need to duplicate Markdown-loading, scoring
plumbing, or safety-gate wiring. If it does, that logic belongs in the
Library, not copy-pasted into the new detector.

## What is Library (do not duplicate, only extend carefully)

| Module | Role |
| --- | --- |
| `src/soulmap/runtime/knowledge/` | Markdown loaders that turn `skills/` content into runtime data structures. See its own docstring: Python here never hardcodes clinical/reflective content |
| `src/soulmap/runtime/guards/` | Response contract, Markdown contract, and resource sanitizer validation, shared by every framework's output |
| `src/soulmap/runtime/routing/` | `framework_selector.py`, the single place that decides which framework/detector runs, and that always reaches `_apply_safety_gate` |
| `src/soulmap/runtime/io/` | Shared text normalization and CLI payload helpers, used by every detector |
| `src/soulmap/runtime/config/` | Protected-module safety config (crisis, dependency); intentionally not Markdown-loaded, see [`known-limitations.md`](known-limitations.md) |
| `src/soulmap/devtools/support/` | Shared subprocess/run helpers used by every CLI command |

Crisis and dependency detection sit in Library, not Framework, on purpose:
they are protected modules per
[`adr/0001-layered-crisis-detection.md`](adr/0001-layered-crisis-detection.md)
and must not be treated as one swappable framework among many.

## What is Framework (add freely, one file pair per framework)

Every framework follows the same two-file shape:

```text
skills/frameworks/<framework>.md         source of truth: detection signals,
                                          reflective guidance, recommendation text
src/soulmap/runtime/detectors/<framework>_detector.py
                                          loads signals from the Markdown file,
                                          scores them, returns a typed result
```

Current frameworks: grief, life-direction, shadow-patterns, inner-parts, anger,
existential-companion, perfectionism-paralysis, empath-boundary,
creative-drought, somatic-wellbeing, emotional-deescalation, pattern-mapper,
and the spiritual-discernment layer under `skills/spiritual/`.

## The authoring rule for new frameworks

When adding framework N+1:

1. Write `skills/frameworks/<name>.md` with a `## Detection signals` section.
   This is the only place phrase lists live, per
   [`knowledge-architecture.md`](knowledge-architecture.md).
2. Write `src/soulmap/runtime/detectors/<name>_detector.py` that loads from
   that Markdown file via the existing `runtime/knowledge/` loaders. Do not
   hand-roll a new Markdown parser.
3. Route through the existing `framework_selector.py`. Do not add a
   framework-specific bypass of `_apply_safety_gate`.
4. Validate output through the existing `runtime/guards/` layer. Do not add a
   framework-specific response validator.
5. Add `tests/test_<name>_detector.py` and a source-backed entry in
   `evals/datasets/groups.json`.

If a step above feels like it requires new Library code (a new loader
capability, a new guard rule), that change belongs in the Library layer and
should be reviewed as such - it affects every framework, not just the new
one - rather than being special-cased inside the new detector.

## Related documentation

- [`repo-contract.md`](repo-contract.md), the top-level structural source of truth
- [`knowledge-architecture.md`](knowledge-architecture.md), the Markdown-first rule this boundary depends on
- [`safety-architecture.md`](safety-architecture.md), the request pipeline the Library layer implements
- [`known-limitations.md`](known-limitations.md), why crisis/dependency are Library and not Framework
