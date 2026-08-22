# ADR 0004: Soulmate-only Skills as a Separate Library Layer

## Status

Accepted

This ADR records the architectural direction requested for Soulmate-only skills. It does not, by itself, create the new skill tree, migrate existing SoulMap content, publish a new registry package, or authorize a live release. Those changes require separate implementation pull requests with characterization tests, explicit artifact contracts, and maintainer review.

## Context

SoulMap AI is intentionally split between a reusable Python foundation and an opinionated reflective-companion framework. The foundation source now lives under `src/soulmate/`, while the SoulMap runtime, developer tooling, website, and framework knowledge remain under `src/soulmap/` and `skills/`. The one-way dependency is already enforced: SoulMap may consume public Soulmate APIs, but Soulmate must not import SoulMap or depend on SoulMap private state.[^1]

The desired product relationship is analogous to React and NextJS:

> Soulmate is the reusable library and foundation. SoulMap is the opinionated framework built on that foundation.

The analogy describes ownership and dependency direction, not API compatibility or a requirement to reproduce the React or NextJS runtime model. Soulmate should provide stable, framework-neutral capabilities. SoulMap should provide the worldview, orchestration, routing, safety policy, voice, synthesis, and product behavior that turn those capabilities into SoulMap AI.

The repository currently has three different concepts that can be confused by the word `library`:

| Surface | Current meaning | Owner |
| --- | --- | --- |
| `src/soulmate/` | Framework-neutral Python foundation library | Soulmate |
| `skills/` | AI-facing knowledge and instruction content | SoulMap Framework |
| `library/catalog.json` | Distribution metadata for SoulMap artifacts | SoulMap distribution |
| `packages/soulmate/` | Release metadata for an isolated `soulmate-ai` Python package | Soulmate release boundary |

The current SoulMap skill builder includes the contents of root `skills/` and `reference/` in SoulMap AI artifacts. Therefore, placing Soulmate-only knowledge under a new root `skills/library/` directory would ship that knowledge with SoulMap by default. This would blur product identity and make a directory addition change the public SoulMap artifact without an explicit release decision.[^1]

The current `packages/soulmate/` directory contains only `pyproject.toml`, `README.md`, and `LICENSE`. Its builder stages the canonical `src/soulmate/` source into a temporary clean tree before producing an isolated Python wheel and source distribution. It is not yet a Soulmate AI skill bundle and must not be treated as one.

## Decision

### Adopt an explicit library-framework relationship

Soulmate is the foundation library. SoulMap is the first opinionated framework built on Soulmate.

```text
Soulmate Library
    │
    │ public contracts, generic data/text/knowledge utilities,
    │ resource boundaries, and framework-neutral lifecycle primitives
    ▼
SoulMap Framework
    │
    │ doctrine, routing, safety, voice, synthesis,
    │ SoulMap frameworks, web surface, and distribution policy
    ▼
SoulMap AI artifacts and supported AI-tool instructions
```

The dependency direction remains strict:

```text
soulmap  ───────────────►  soulmate
Soulmate-only skills ───► Soulmate skill artifact builder
Soulmate ────────X──────► soulmap
SoulMap skills ────X────► Soulmate-only skill artifact
```

Soulmate-only skills may describe reusable foundation behavior, contracts, resource semantics, lifecycle concepts, or other content that is meaningful without SoulMap's worldview. They must not become a hidden copy of SoulMap's doctrine.

### Give Soulmate-only skills a package-owned source boundary

Soulmate-only skills will be authored under a package-owned knowledge boundary rather than under root `skills/`:

```text
packages/
└── soulmate/
    ├── pyproject.toml
    ├── README.md
    ├── LICENSE
    └── skills/
        ├── README.md
        ├── manifest.json
        └── foundation/
            ├── contracts.md
            ├── knowledge-resolution.md
            ├── lifecycle.md
            └── resource-boundaries.md
```

This is the package-owned target layout. The initial P0 foundation entries now live in
this subtree as a separate implementation change; the layout must still grow only through
manifested, reviewed entries and must not be inferred from this ADR alone.

Root `skills/` remains SoulMap-owned:

```text
skills/
├── frameworks/       SoulMap response frameworks and routing targets
├── meta/             SoulMap orchestration and response structures
├── safety/           SoulMap safety doctrine and protected policy
├── voice/            SoulMap voice and calibration
├── brand/            SoulMap identity and positioning
└── spiritual/        SoulMap spiritual frameworks and discernment
```

The previously defined root `skills/library/` namespace remains reserved for explicitly shared, framework-neutral Markdown. It is not the source location for Soulmate-only skills, is not a plugin directory, and must not be scanned to alter SoulMap routing implicitly.[^1]

### Keep Soulmate-only skills separate from SoulMap distribution

Soulmate-only skill content must have an independent allow-listed builder and artifact family:

```text
dist/soulmate-ai.zip
dist/soulmate-ai.skill
dist/soulmate-library.json
```

The separate builder must include only the approved Soulmate skill manifest, Soulmate-only Markdown, required package metadata, and any explicitly approved neutral resources. It must reject or exclude:

- `src/soulmap/` and SoulMap-specific Python modules;
- root `skills/` content unless an individual shared entry is explicitly approved;
- SoulMap `reference/` locale evidence;
- SoulMap brand, voice, routing, crisis policy, response-safety policy, website, and internal maintainer content;
- undocumented files, symlinks, generated caches, and private repository metadata.

The existing SoulMap artifacts remain unchanged:

```text
dist/soulmap-ai.zip
dist/soulmap-ai.skill
dist/soulmap-ai-library.json
```

A Soulmate package artifact and a Soulmate AI skill artifact are related but distinct products. The Python package contains executable foundation code. The AI skill artifact contains explicitly authored Soulmate knowledge and instruction content. Neither artifact may be produced by reusing an implicit include-everything rule from the SoulMap builder.

### Require an explicit integration seam

SoulMap will use Soulmate through documented public Python namespaces and, where skill content is involved, through an explicit loader or manifest contract. The integration must be deterministic and inspectable.

SoulMap must not dynamically discover every file in `packages/soulmate/skills/` and silently add it to routing. A Soulmate skill becomes active for SoulMap only when all of the following are true:

1. its manifest entry declares an owner, stable identifier, version, compatibility range, and allowed consumer;
2. a documented loader or integration adapter names it explicitly;
3. contract tests prove its schema, artifact inclusion, and consumer behavior; and
4. the SoulMap release review confirms that the content is genuinely shared rather than SoulMap doctrine in disguise.

### Define the minimum skill metadata contract

Before the first Soulmate-only skill is implemented, its manifest schema must define at least:

| Field | Purpose |
| --- | --- |
| `id` | Stable, namespace-qualified skill identifier |
| `version` | Independent content compatibility version |
| `owner` | Responsible library/product owner |
| `kind` | Foundation, contract, resource, lifecycle, or another approved neutral category |
| `source` | Repository-relative canonical Markdown path |
| `consumers` | Explicit consumers such as Soulmate-only or SoulMap-compatible |
| `compatibility` | Minimum Soulmate package/API compatibility |
| `artifact` | Allowed artifact family and inclusion rule |

The schema must reject undeclared consumers and ambiguous ownership. Versioning the manifest does not replace versioning the Python package or the SoulMap framework; each product retains its own release identity.

### Migrate only proven-neutral content

No existing file under `skills/frameworks/`, `skills/meta/`, `skills/safety/`, `skills/voice/`, `skills/brand/`, or `skills/spiritual/` is considered Soulmate-owned merely because another framework could technically read it. Migration requires an inventory, an ownership decision, a neutral rewrite where necessary, and tests showing that SoulMap behavior remains unchanged.

The first Soulmate-only skills should be small and foundational. Candidates may include explanations of public contracts, resource resolution semantics, lifecycle boundaries, and knowledge representation. Crisis detection, response-safety enforcement, SoulMap routing priority, anti-dependency doctrine, brand language, spiritual positioning, and SoulMap response templates remain framework-owned unless a separate ADR supersedes this decision.

## Rationale

This decision gives the repository the intended React/NextJS-style relationship without pretending that AI skills and web frameworks have identical runtime behavior. The most important property is that SoulMap depends on a smaller foundation, while the foundation remains usable without SoulMap.

A package-owned skill boundary prevents the existing SoulMap builder from accidentally shipping Soulmate-only knowledge. It also gives Soulmate a future independent distribution path without forcing a package-registry publication today. Keeping the canonical Python implementation in `src/soulmate/` avoids duplicate source trees, while keeping package metadata and skill content under `packages/soulmate/` makes the release boundary visible.

The explicit manifest and loader rules preserve reproducibility. A future contributor cannot add a Markdown file and silently alter framework routing, safety behavior, or a public artifact. The same rules also make it possible for SoulMap to consume a carefully approved neutral capability without making all Soulmate content part of SoulMap.

## Alternatives Considered

### Put Soulmate-only skills in root `skills/library/`

Rejected as the default. The current root builder includes root `skills/` content in SoulMap AI artifacts. This would make Soulmate-only content part of SoulMap and would make artifact identity depend on an implicit directory convention.

Root `skills/library/` remains available only for content explicitly classified as shared, with an owner, consumer list, loader contract, and artifact decision.

### Move all current SoulMap skills into Soulmate

Rejected. The current framework, meta, safety, voice, brand, and spiritual content expresses SoulMap's opinionated behavior. Moving it would turn Soulmate into a renamed or diluted SoulMap and would make future frameworks depend on assumptions they did not choose.

### Copy root `skills/` into a Soulmate directory

Rejected. Copying would create two sources of truth, invite content drift, and make security and release review harder. Only reviewed, neutral content may be rewritten or moved one entry at a time.

### Dynamically discover Soulmate skills as plugins

Rejected. Implicit plugin discovery would make routing, artifact composition, compatibility, and audit behavior difficult to reproduce. Activation must remain explicit and contract-tested.

### Merge Soulmate and SoulMap into one package and one artifact

Rejected. The user-facing identities, dependency direction, release cadence, and content ownership differ. A single bundle would make it difficult to use Soulmate independently and would increase the chance of leaking SoulMap-specific material.

### Publish Soulmate to a public registry immediately

Rejected for this ADR. Publication requires an approved distribution name and namespace, version and tag policy, credentials or trusted publishing, ownership, rollback procedure, and explicit maintainer approval. The architectural boundary must be stable before public distribution is enabled.

## Consequences

### Positive consequences

Soulmate can evolve as an independently reusable foundation and can eventually ship its own AI skill bundle. SoulMap remains a complete, opinionated framework rather than becoming a generic library with hidden brand assumptions. The package-owned skill boundary makes artifact review and future registry publication safer.

The explicit relationship also clarifies documentation and onboarding. Contributors can ask whether a capability is a reusable foundation primitive or a SoulMap product decision, then place it in the corresponding source and artifact boundary.

### Costs and trade-offs

The repository will have more than one manifest and artifact family. Maintainers must keep Python package versions, skill content versions, compatibility declarations, and SoulMap framework versions understandable. The first implementation will require new builders, manifests, extraction tests, and documentation.

Some capabilities will remain duplicated at the conceptual level during migration because a neutral Soulmate explanation and a SoulMap-specific application may both be useful. This is acceptable only when each has a distinct owner and purpose; mechanical copies are not allowed.

Soulmate-only skills will not automatically provide SoulMap's safety, voice, spiritual, or routing behavior. That limitation is intentional and is necessary for Soulmate to remain framework-neutral.

## Required Safeguards

| Safeguard | Required evidence before implementation is considered complete |
| --- | --- |
| Dependency direction | Static checker and tests prove `soulmate` never imports `soulmap`; SoulMap uses only public Soulmate namespaces |
| Source ownership | Every Soulmate-only skill has one canonical Markdown path, owner, identifier, and consumer declaration |
| Artifact isolation | Independent ZIP/.skill/catalog tests prove no SoulMap runtime, root skills, reference, web, or internal files leak into Soulmate artifacts |
| SoulMap preservation | Existing SoulMap ZIP/.skill/catalog artifacts remain compatible and retain their current names and content contract |
| Explicit activation | No directory-wide dynamic routing; loaders and consumers are named and tested |
| Version parity | Manifest, package metadata, artifact filenames, catalog entries, and compatibility declarations agree |
| Clean extraction | Artifacts build and extract successfully in a clean environment without repository-relative assumptions |
| Safety boundary | Crisis, response-safety, dependency, routing, and brand behavior remain SoulMap-owned unless separately approved |
| Cross-platform support | Python 3.11 CI, Ruff, Pyright, contract tests, and artifact checks pass on supported operating systems |
| Release governance | No registry publication or live release occurs without namespace, credentials/trusted publishing, rollback plan, and explicit approval |

## Implementation Sequence

This ADR establishes the direction; the following sequence is the recommended implementation order:

1. Define and contract-test the Soulmate skill manifest and ownership metadata.
2. Create the package-owned `packages/soulmate/skills/` tree with one or two genuinely neutral foundation entries.
3. Implement a separate Soulmate AI artifact builder and verifier with an explicit allow-list.
4. Generate and validate `soulmate-library.json` without changing the existing SoulMap catalog.
5. Add an explicit SoulMap consumer adapter only for approved shared entries, preserving current SoulMap behavior.
6. Add clean extraction, version-parity, dependency, no-leakage, and regression tests in CI.
7. Document import/use instructions and perform manual review of the generated artifacts.
8. Consider a GitHub Release or public registry only after the release gate in this ADR is satisfied.

Each step should be delivered as a small pull request. No step requires moving `skills/frameworks/`, renaming `src/soulmap/`, changing current SoulMap artifact names, or introducing a runtime API, database, account system, LLM dependency, or semantic safety classifier.

## Non-goals

This ADR does not:

- move or rename the existing SoulMap skills;
- create `packages/soulmate/skills/` immediately;
- make root `skills/library/` a plugin or dynamic routing directory;
- make Soulmate responsible for SoulMap safety, voice, doctrine, spiritual content, or brand identity;
- require Soulmate to generate AI responses;
- authorize a public package-registry publication or live GitHub Release;
- introduce an LLM, network dependency, database, account system, or runtime web API;
- copy SoulMap content into Soulmate without an ownership and neutrality review.

## References

[^1]: [ADR 0003: Soulmate Library as the Foundation for the SoulMap Framework](0003-soulmate-library-soulmap-framework.md)

- [Repository contract](../repo-contract.md)
- [Soulmate package metadata](../../../packages/soulmate/pyproject.toml)
- [Soulmate package README](../../../packages/soulmate/README.md)
- [Soulmate package builder](../../../scripts/build_soulmate.py)
- [Soulmate package verifier](../../../scripts/verify_soulmate_package.py)
- [SoulMap Library catalog](../../../library/catalog.json)
- [SoulMap Skill artifact builder](../../../src/soulmap/devtools/packaging/build_skill.py)
- [ADR index](README.md)
