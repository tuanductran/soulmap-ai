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
- **Primary routed framework** - an independently selectable response route, backed by
  semantic Markdown knowledge and a Python-owned detector/routing binding. Its executable
  scoring and routing configuration remains in Python.
- **Supporting lens or secondary layer** - reusable knowledge that enriches an already
  selected primary route. It does not automatically become an independent primary route.

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

## Primary routed frameworks and supporting knowledge

A primary routed framework is a normal, independently selectable framework route the
selector can return as `primary_framework`. Crisis and dependency short-circuits are
protected Library-level safety overrides, not swappable framework files. Its runtime role is defined by Python-owned labels, detector
bindings, routing configuration, and the registered knowledge-source mapping. The
relevant implementation contracts live in:

- `src/soulmap/runtime/knowledge/labels.py` for reader-label mappings;
- `src/soulmap/runtime/routing/framework_selector.py` for primary and secondary
  detector bindings and selection order;
- `src/soulmap/runtime/knowledge/runtime_config.py` for executable scoring, routing,
  and deterministic template configuration (`FRAMEWORK_TEMPLATE_ROWS`);
- `skills/meta/framework-template-map.md` for qualitative, AI-facing response-structure
  guidance; it is not the deterministic runtime template mapping;
- `src/soulmap/runtime/knowledge/runtime_registry.py` for registered Markdown sources.

The `skills/frameworks/` directory is a knowledge-file inventory, not a one-to-one
detector registry. It contains primary framework sources as well as secondary guidance
and supporting lenses. A filename, folder, or presence of a `Detection signals`
section does not by itself mean that the file has an independent primary route or needs
a dedicated detector.

Current Markdown files under `skills/frameworks/` include:

- ancestral-patterns
- anger-companion
- conversation-synthesis
- creative-drought
- dark-night-of-soul
- divine-guidance
- emotional-deescalation
- empath-boundary
- existential-companion
- fear-of-visibility
- feminine-masculine-dynamics
- grief-companion
- inner-parts
- integration-celebration
- life-direction
- meaning-integration
- money-self-worth
- pattern-mapper
- perfectionism-paralysis
- relationship-reflection
- sacred-feminine-masculine
- self-compassion
- shadow-patterns
- somatic-wellbeing
- soul-nourishment
- spiritual-purpose

This list is a directory inventory only. Some entries are supporting lenses or
secondary-layer guidance; the authoritative primary/secondary routing relationships
must be read from the current Python mappings and selector, not inferred from this list.

`skills/soulmate/` illustrates the same distinction: `soulmate-longing.md` and
`partnership-patterns.md` are independently routed primary knowledge sources, while
`numerology-connection-lens.md` is a supporting topic lens with no independent primary
detector. `skills/frameworks/relationship-reflection.md` is also supporting guidance
that may be used after a primary route is active.

## Authoring rule

When adding a new primary routed framework:

1. Confirm that the need is not already served by an existing route or supporting lens.
2. Add semantic activation signals and reflective guidance to the registered Markdown
   source. Do not place executable scoring weights or thresholds in Markdown.
3. Add or extend the detector and Python-owned routing/configuration only when a new
   primary route is genuinely required.
4. Preserve the existing selector order and independent safety-gate path.
5. Add source-backed eval coverage and the appropriate template mapping.

When adding a supporting lens or secondary guidance, do not create a new primary route,
detector, priority row, or template mapping by default. Link the knowledge from the
appropriate canonical guidance and test only the contract it actually owns.

If a change requires new Library code (a loader capability, shared guard rule, or routing
primitive), review it as a Library change because it affects more than one knowledge
module.

## Related documentation

- [`repo-contract.md`](repo-contract.md), the top-level structural source of truth
- [`knowledge-architecture.md`](knowledge-architecture.md), the Markdown-first rule this boundary depends on
- [`safety-architecture.md`](safety-architecture.md), the request pipeline the Library layer implements
- [`known-limitations.md`](known-limitations.md), why crisis/dependency are Library and not Framework
