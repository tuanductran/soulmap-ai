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

## Skill loading already follows progressive disclosure

The root `SKILL.md` uses the progressive-disclosure pattern described by
Anthropic's Agent Skills documentation: its front matter and entrypoint guidance
are loaded first, then directly referenced canonical knowledge is loaded only
when that part of the response pipeline is needed. This keeps the distributable
Skill entrypoint small while preserving the full canonical knowledge base under
`skills/`. Developer Skills under `.claude/skills/` are separate internal tooling
and are not part of the SoulMap distribution. See the [Agent Skills overview](https://platform.Claude.com/docs/en/agents-and-tools/agent-skills/overview).

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

Detector-backed primary frameworks follow a two-file integration shape:

```text
skills/frameworks/<framework>/content/*.md canonical knowledge source: detection
                                          signals and reflective guidance
src/soulmap/runtime/detectors/<framework>_detector.py
                                          loads the registered Markdown source,
                                          scores signals, and returns a typed result
```

Not every file under `skills/frameworks/` is a standalone detector-backed
primary framework. Some are supporting lenses or knowledge sources consumed by
an existing framework or the host-layer response flow. For example,
`self-compassion.md` is a registered supporting source used by the shadow
detector, while `money-self-worth.md`, `relationship-reflection.md`, and
`feminine-masculine-dynamics.md` are knowledge/evaluation sources rather than
independent runtime detector modules.

The authoritative runtime source-to-consumer mapping is
`src/soulmap/runtime/source_registry.py`. A source belongs in that registry only
when runtime code needs a stable identifier for it. Absence of a detector does
not make a Markdown source invalid or unused.

`skills/soulmate/` is the concrete example of the analogy in the previous
section: a framework layer built on top of existing SoulMap infrastructure rather
than a second runtime architecture. Its primary files,
`soulmate-longing.md` and `partnership-patterns.md`, have runtime-backed
sources and detectors. Its `numerology-connection-lens.md` is intentionally a
topic lens with no detector, applied only after a primary framework is active.

## Skill resource model

A framework can now be decomposed into optional Skill-local resources when its material benefits from progressive disclosure:

```text
skills/frameworks/<name>/
├── content/   canonical framework knowledge
├── examples/  worked demonstrations
└── prompt/    Skill-local orchestration that references the other resources
```

This does not create another `SKILL.md`, detector, or runtime. `content/` owns canonical knowledge, `examples/` demonstrates application without becoming canned answers, and `prompt/` orchestrates resource use without copying their contents. Existing frameworks remain valid as single Markdown files; migration is evidence-driven.

## The authoring rule for new frameworks

When adding framework N+1:

1. Write the canonical framework knowledge under `skills/frameworks/<name>/content/` when using the layered resource model, with a `## Detection signals` section if runtime-backed. A simple single-file framework remains allowed.
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
