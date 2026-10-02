# SoulMap AI Library

SoulMap is the **Library**: a reusable, versioned knowledge and response-framework foundation that can be embedded into compatible AI tooling.

The Library is the product-level concept. It is not represented by a special root `library/` source directory. Shipped knowledge lives under `skills/`, while runtime implementation lives under `src/soulmap/runtime/`.

## Library structure

The Library is organized by semantic capability rather than by domain directories:

- `skills/meta/` - orchestration, execution pipeline, calibration, and epistemic guidance
- `skills/frameworks/` - the canonical reflective framework set
- `skills/safety/` - safety, scope, dependency, and crisis boundaries
- `skills/spiritual/` - symbolic and spiritual knowledge
- `skills/soulmate/` - soulmate and partnership-specific knowledge built on SoulMap
- `skills/voice/` - persona and response calibration
- `skills/brand/` - identity and positioning
- `skills/writing/` - reflection-to-writing guidance

Domains such as inner work, relationships, spirituality, wellbeing, and life and meaning are **classification dimensions**, not filesystem boundaries. The framework index owns the domain map so one framework can participate in multiple domains without duplication.

## Skill inventory

`.claude-plugin/marketplace.json` is the machine-readable inventory of shipped skill packages. It is the source used to derive the Library distribution manifest; there is no second root catalog to keep synchronized.

The root documents remain authoritative:

- `SKILL.md` - top-level Skill entry point
- `SOULMAP.md` - behavioral contract and non-negotiable safety rules
- `.claude-plugin/marketplace.json` - shipped skill inventory and package metadata

## Generate the Library manifest

Run:

```bash
uv run soulmap library-manifest
```

This builds:

- `dist/soulmap-ai.zip` - standard knowledge archive
- `dist/soulmap-ai.skill` - skill-oriented archive with `.claude-plugin/`
- `dist/soulmap-ai-library.json` - generated Library manifest containing project version, skill inventory, release URL, compatibility metadata, and SHA-256 digests

The manifest is derived from the shipped skill inventory and `pyproject.toml`. Do not hand-edit it.

Verify the exact artifacts with:

```bash
uv run python scripts/verify_artifact_hashes.py
uv run python scripts/verify_extracted_artifacts.py
```

## Installation boundary

Library distribution supports **manual upload** to compatible tools. The generated manifest does not claim automatic installation, background synchronization, or platform acceptance.

For upload instructions, see [UPLOAD.md](UPLOAD.md).

## Library vs Framework

SoulMap is the reusable Library layer. A future `Soul...` product should be treated as a Framework only when it adds a coherent application-level architecture, conventions, orchestration, integrations, and lifecycle on top of SoulMap rather than merely adding another collection of knowledge.

This distinction keeps SoulMap reusable while allowing future products to build on it without turning the Library into a product-specific application.

## Release procedure

Before release, build and verify the artifacts from the exact release tree. The release workflows perform the same build, verification, extraction, provenance, and publication checks.

A release reviewer should confirm:

1. the manifest version matches the release tag;
2. both archives exist;
3. recorded sizes and SHA-256 digests match the generated files;
4. extracted archives contain only the intended shipped boundary.

The Library is therefore the reusable distribution layer, not a separate source tree.
