---
title: "SoulMap AI, Library vs Framework boundary"
description: "Defines which runtime modules are the reusable Library layer and which are the swappable Framework layer, and the rule for building new frameworks on top of the Library instead of duplicating it."
---

# Library vs Framework boundary

This document defines the current relationship between the independent Soulmate
foundation library and the opinionated SoulMap Framework. It complements
[`repo-contract.md`](repo-contract.md), which is the structural source of truth for all
repository surfaces.

The repository also contains reusable layers inside `src/soulmap/runtime/`. Those are
SoulMap-owned implementation layers and must not be confused with the public,
framework-neutral Soulmate boundary described below. This document does not move or
rename either source tree; it records the ownership and authoring rules that keep them
separate.

## The analogy

The intended relationship is the same as a UI library such as React and an
application framework such as Next.js:

- **Soulmate library** - the reusable, framework-neutral substrate in `src/soulmate/`
  with independent package metadata and AI foundation skills under
  `packages/soulmate/`. It owns public contracts, resource resolution, Markdown
  parsing, text normalization, lifecycle primitives, and generic data validation.
- **SoulMap Framework** - the opinionated product layer in `src/soulmap/` and `skills/`.
  It owns reflective doctrine, safety policy, routing, detectors, voice, brand,
  spiritual content, website behavior, and distribution of SoulMap artifacts.

SoulMap may depend on approved public Soulmate APIs. Soulmate must never import SoulMap,
its doctrine, routing state, protected safety policy, voice, brand, or spiritual content.
A new SoulMap framework should not duplicate generic Soulmate capabilities; a genuinely
generic capability should first be proposed and contract-tested at the Soulmate boundary.

## What is Soulmate library (do not duplicate, only extend carefully)

| Boundary | Canonical surface | Does not own |
| --- | --- | --- |
| Python foundation | `src/soulmate/` | SoulMap doctrine, routing, product policy, or protected safety state |
| Standalone release metadata | `packages/soulmate/pyproject.toml` and `packages/soulmate/README.md` | Root SoulMap package metadata or website content |
| AI foundation skills | `packages/soulmate/skills/` | Root `skills/` doctrine, safety, voice, brand, spiritual, or framework files |

The Soulmate Python package and Soulmate AI foundation-skill artifacts are separate
surfaces and are verified independently. Neither is the import surface for the root
SoulMap AI skill artifact.

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

Current routed reflective frameworks include grief, existential-companion,
inner-parts, life-direction, creative-drought, perfectionism-paralysis,
shadow-patterns, ancestral-patterns, fear-of-visibility, empath-boundary,
dark-night-of-soul, soul-nourishment, divine-guidance, sacred-polarity,
spiritual-purpose, integration-celebration, meaning-integration, synthesis,
pattern-mapper, and the spiritual-discernment layer under `skills/spiritual/`.
Crisis, dependency, de-escalation, and intensity are protected or orchestration
paths rather than ordinary swappable frameworks; their priority and safety behavior
remain governed by the runtime safety architecture.

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
