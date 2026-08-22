# ADR 0003: Soulmate Library as the Foundation for the SoulMap Framework

## Status

Accepted

This ADR records the agreed architectural direction. It does not, by itself, authorize a runtime migration, a package rename, a new artifact, or a change to the existing SoulMap behavior. Each implementation step must still be delivered through the normal review process with characterization tests and the relevant repository gates.

## Context

SoulMap AI currently combines a knowledge-first Markdown surface with a small Python runtime for routing, safety enforcement, validation, packaging, and developer tooling. The public identity is defined by `SKILL.md`, `AGENTS.md`, and the coordinated content under `skills/`. The executable package is rooted at `src/soulmap/`, and the current distribution contract produces `dist/soulmap-ai.zip`, `dist/soulmap-ai.skill`, and the generated Library manifest.

The project now needs a reusable foundation that can support more than one opinionated AI framework without duplicating low-level capabilities. The intended relationship is analogous to a library and a framework: **Soulmate provides reusable primitives and contracts; SoulMap composes those primitives into a complete reflective-companion framework with its own doctrine, routing policy, voice, safety posture, and web surface.** The analogy to React and NextJS is architectural, not an instruction to copy their APIs or runtime model.

This distinction matters because the current repository has several intentionally different meanings for the word "framework." The Python package is an executable runtime, `skills/frameworks/` contains SoulMap response-framework knowledge, and the root `library/` directory contains distribution metadata. A future Soulmate layer must not collapse those meanings or silently change the existing package boundary.

The current packaging implementation also imposes a direct constraint. The Skill builder includes every file below `skills/` and `reference/` in both public AI artifacts unless a path is excluded by `.distignore`. Therefore, content placed under a future `skills/library/` directory would be shipped with SoulMap by default. That behavior is acceptable only for knowledge intentionally shared with SoulMap; Soulmate-only content must not be placed there without an explicit artifact decision.

The current knowledge audit and Markdown loaders are also scoped to `src/soulmap/runtime/` and to the repository's existing knowledge roots. A sibling package cannot be assumed to participate in those checks automatically. Any extraction must extend the tooling deliberately and must preserve one authoritative source for each knowledge group.

## Decision

### Establish a one-way Library-Framework relationship

Soulmate is the foundation layer and SoulMap is the first opinionated framework built on it.

```text
soulmate library
    │
    │ public contracts, reusable primitives, resource resolution,
    │ knowledge-loading interfaces, and framework-neutral lifecycle support
    ▼
soulmap framework
    │
    │ doctrine, routing, safety policy, voice, synthesis,
    │ SoulMap-specific frameworks, packaging, and web surface
    ▼
AI tools, static artifacts, and the SoulMap website
```

The dependency direction is strict:

```text
soulmap  ───────────────►  soulmate
soulmate ───────────────►  standard library / approved generic dependencies
soulmate ────────X──────►  soulmap
```

`src/soulmate/` must never import `src/soulmap/`, `skills/frameworks/`, SoulMap brand doctrine, SoulMap routing state, or SoulMap-specific safety policy. SoulMap may consume Soulmate only through documented public contracts rather than private implementation imports.

### Add Soulmate as a sibling bounded context, not a rename or rewrite

The target source layout is:

```text
src/
├── soulmate/
│   ├── __init__.py
│   ├── contracts/
│   ├── knowledge/
│   ├── pipeline/
│   ├── resources/
│   └── errors.py
└── soulmap/
    ├── runtime/
    ├── devtools/
    └── web/
```

This is a target architecture, not an instruction to copy the existing package. The first implementation should create only a minimal, independently testable Soulmate surface. Generic code may be extracted from SoulMap only after usage, ownership, and behavior have been audited.

The existing `src/soulmap/` import paths, CLI entry point, website routes, runtime safety behavior, and artifact names remain supported. If a module is eventually moved into Soulmate, a compatibility re-export may preserve the old SoulMap import path for a defined deprecation period. Compatibility shims must remain thin and must not create a reverse dependency.

### Separate reusable library capability from SoulMap opinion

Soulmate may own framework-neutral capabilities such as:

- typed request, context, result, and error contracts;
- deterministic resource and Markdown resolution interfaces;
- schema validation and lifecycle primitives;
- provider-neutral knowledge interfaces;
- reusable test protocols and integration boundaries.

SoulMap continues to own opinionated behavior such as:

- the SoulMap identity and anti-dependency doctrine;
- framework selection priority and routing policy;
- voice, response structure, session rituals, and brand language;
- SoulMap-specific safety policy and protected crisis behavior;
- synthesis behavior, public website behavior, and SoulMap distribution metadata.

Soulmate must not become a hidden second source of SoulMap doctrine. Python remains an enforcement, routing, validation, and packaging layer; response content and knowledge remain canonical Markdown unless an existing protected-module policy explicitly allows a Python source.

### Define the knowledge namespaces without moving current content

The following namespace meanings are adopted:

| Namespace | Owner | Meaning | Initial rule |
| --- | --- | --- | --- |
| `skills/library/` | Shared library layer | Reusable, framework-neutral Markdown resources intentionally consumable by Soulmate and/or SoulMap | New namespace; no automatic routing; every entry needs ownership and compatibility metadata |
| `skills/frameworks/` | SoulMap | SoulMap-specific response frameworks and routing targets | Keep the current files and paths stable |
| `skills/meta/` | SoulMap | Orchestration, execution pipeline, response structures, and framework mapping | Remains SoulMap-owned |
| `skills/safety/` | SoulMap | SoulMap safety doctrine and boundaries | Remains SoulMap-owned; protected crisis modules are not casually extracted |
| `skills/voice/` | SoulMap | SoulMap voice and calibration | Remains SoulMap-owned |
| `skills/brand/` | SoulMap | SoulMap brand and positioning | Remains SoulMap-owned |
| `library/catalog.json` | SoulMap distribution | Versioned catalog metadata for the current SoulMap artifacts | Do not repurpose as a knowledge directory or Soulmate catalog |
| `reference/languages/` | Repository knowledge boundary | Human-authored locale evidence for explicitly consuming runtime detectors | Keep its current narrow evidence-only role |

`skills/library/` is not a dynamic plugin directory and must not be scanned to alter SoulMap routing implicitly. A library entry becomes active only through an explicit consumer contract, a documented loader, and tests that prove the expected behavior.

The existing `skills/frameworks/` directory is not moved into Soulmate. Its current files are part of SoulMap's public knowledge identity and their detector/routing references must remain stable during the initial extraction phases.

### Preserve the current SoulMap artifact contract

The following artifacts remain unchanged during the foundation and extraction phases:

```text
dist/soulmap-ai.zip
dist/soulmap-ai.skill
dist/soulmap-ai-library.json
```

A future Soulmate artifact, if required, must have a separate builder, explicit allow-list, manifest, and contract tests. A proposed target may be:

```text
dist/soulmate-ai.zip
dist/soulmate-ai.skill
dist/soulmate-library.json
```

The current SoulMap builder must not be reused with an implicit "include everything" rule for a separate Soulmate artifact. Conversely, adding `src/soulmate/` as local Python implementation must not cause that code to leak into the AI-facing SoulMap Skill artifact. Artifact inclusion must be explicit and testable.

The existing `pyproject.toml` wheel boundary also remains unchanged until a separate implementation decision is approved. Adding a sibling source directory does not automatically mean that it belongs in the current `soulmap-ai` wheel.

### Require explicit contracts at the integration seam

The initial public seam between the layers should be small and stable. It may expose protocols for:

- resolving a named Markdown resource;
- loading validated knowledge metadata;
- representing framework input context and lifecycle state;
- returning deterministic routing or validation results;
- reporting typed, inspectable errors.

The seam must not expose SoulMap's private detector constants, global routing state, protected crisis packs, web templates, or brand copy. The contract should be dependency-light, deterministic, type-checkable under the repository's Python 3.11 baseline, and usable without an LLM or network access.

### Use staged extraction with compatibility protection

Implementation must proceed in small, independently reviewable steps:

1. Create an ADR-approved Soulmate skeleton and import smoke tests without changing SoulMap behavior.
2. Inventory candidate generic modules and confirm ownership with `soulmap audit-knowledge`, repository search, and import analysis.
3. Extract only one generic capability at a time, preserving the original SoulMap import path through a compatibility shim when necessary.
4. Add contract, unit, integration, type-checking, and coverage evidence before changing the next boundary.
5. Add `skills/library/` entries only when their schema, owner, consumers, and shipping behavior are explicit.
6. Design a separate Soulmate builder and catalog only after the shared contracts and content boundary are stable.
7. Update repository documentation and release contracts together with each accepted boundary change.

No phase may require a flag day, a repository-wide rename, a simultaneous migration of all detectors, or a change to SoulMap's current public artifact names.

## Rationale

This decision provides a reusable base without weakening SoulMap's established identity. It follows the user's intended relationship: Soulmate is the general-purpose library, while SoulMap is a complete framework that gives the base layer a specific worldview, behavior, and product surface.

A sibling bounded context is safer than copying or renaming the current package. Copying would create two implementations that drift; renaming would break imports, CLI expectations, documentation, and release consumers. An explicit one-way dependency allows generic capability to be shared while keeping SoulMap's opinionated behavior visible and auditable.

A dedicated `skills/library/` namespace gives reusable Markdown a clear home, but the packaging constraint makes it important to distinguish shared knowledge from Soulmate-only knowledge. The namespace is therefore intentionally non-routing and contract-driven. This prevents a new directory from silently changing the current framework selector or expanding the SoulMap artifact without review.

Separate artifacts are a later consequence of identity and packaging isolation, not a prerequisite for the first skeleton. Keeping that decision explicit avoids leaking Python internals into AI-facing packages and avoids turning the current two-artifact release contract into an accidental multi-product bundle.

The staged extraction strategy protects the most sensitive parts of the repository. In particular, crisis detection, response-safety enforcement, SoulMap routing priority, and canonical framework content are not generic merely because another package might want to call them. Their ownership must be demonstrated before any migration is considered.

## Alternatives Considered

### Rename `src/soulmap/` to `src/soulmate/`

Rejected. This would invert the intended relationship, break the existing `soulmap` package and CLI contract, make SoulMap's identity less explicit, and require a high-risk migration before a reusable foundation has been defined.

### Copy `src/soulmap/` into `src/soulmate/`

Rejected. Duplication would immediately create divergent loaders, safety behavior, tests, and bug fixes. It would also make ownership and artifact provenance unclear.

### Keep both products as unrelated sibling applications

Rejected for the intended model. This would lose the library-framework relationship and encourage duplicated primitives. Separate identities and artifacts remain useful, but they must sit on top of a one-way foundation rather than become two unrelated implementations.

### Put all Soulmate content into `skills/library/` and ship it with SoulMap

Rejected. The current builder automatically includes all `skills/**` content in SoulMap's public artifacts. This would blur identity and make Soulmate-only knowledge part of SoulMap without an explicit release decision.

### Make Soulmate a runtime plugin discovered dynamically from `skills/`

Rejected. Dynamic discovery would make routing, safety, packaging, and audit behavior harder to reproduce. The repository uses explicit ownership and source paths; an implicit plugin registry would introduce a new source of drift.

### Extract protected safety and crisis modules into the generic library immediately

Rejected. The repository intentionally treats crisis detection and related safety configuration as protected. Any future migration would require a separate ADR or superseding decision, independent evidence, and a full safety evaluation.

## Consequences

### Positive consequences

SoulMap can reuse generic capabilities without duplicating them, while its public identity and doctrine remain stable. Future framework products can depend on a small, deterministic foundation instead of importing SoulMap internals. The one-way dependency makes architectural ownership and test scope easier to understand.

The namespace and artifact rules make it possible to distinguish shared knowledge, SoulMap-specific frameworks, and local implementation. This improves reviewability and makes future release provenance more explicit.

### Costs and trade-offs

The repository will temporarily contain compatibility layers and duplicate-looking paths while extraction is staged. Maintainers must define and test public interfaces before moving code. Build and manifest tooling will eventually need explicit support for a second artifact family, and the additional contract surface will require more tests and documentation.

Soulmate will not automatically inherit every SoulMap safety or voice behavior. That is intentional: generic library capability and opinionated framework policy must remain separate. A future framework that needs a SoulMap safety policy must declare that dependency explicitly rather than assuming it through shared imports.

### Required safeguards

Before any implementation PR that changes the boundary, the following evidence is required:

| Safeguard | Required evidence |
| --- | --- |
| Import direction | A test or static check proving `soulmate` does not import `soulmap` |
| Backward compatibility | Existing SoulMap unit, contract, eval, browser, and build gates remain green |
| Knowledge ownership | Audit output and independent repository search identify one canonical source per knowledge group |
| Artifact boundary | Extraction tests prove SoulMap artifacts contain only their allow-listed files |
| Safety preservation | Protected crisis and response-safety behavior is unchanged unless separately approved |
| Type/toolchain support | Ruff, Pyright, Python 3.11, and the repository lock state remain supported |
| Documentation parity | `AGENTS.md`, `SKILL.md`, `docs/ROADMAP.md`, repo contract, catalogs, and release notes match the implementation |

## Non-goals

This ADR does not authorize a live AI chat service, a database, accounts, memory storage, an LLM dependency, semantic safety classification, automatic translation, a new provider connector, or a change to the Python-only website boundary.

It does not move the existing SoulMap framework files, rewrite SoulMap's doctrine, make `skills/library/` a dynamic routing source, or change the current SoulMap artifact names. It also does not require Soulmate to generate responses; response generation remains outside the deterministic Python layer.

## References

- [Repository contract](../repo-contract.md)
- [Knowledge architecture](../knowledge-architecture.md)
- [Known architectural limitations](../known-limitations.md)
- [SoulMap root manifest](../../../SKILL.md)
- [SoulMap contributor and package contract](../../../AGENTS.md)
- [Library source catalog](../../../library/catalog.json)
- [Skill artifact builder](../../../src/soulmap/devtools/packaging/build_skill.py)
- [Library manifest builder](../../../src/soulmap/devtools/packaging/library.py)
- [ADR index](README.md)
