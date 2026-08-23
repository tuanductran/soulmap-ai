# Soulmate AI

Soulmate is the framework-neutral foundation library for SoulMap and future AI frameworks. It provides small, deterministic contracts and utilities without owning product doctrine, routing policy, voice, crisis handling, or web behavior.

## Current public surface

The first release-preparation package exposes:

- `soulmate.contracts`: explicit resource-reference contracts.
- `soulmate.data`: JSON parsing and mapping field validation.
- `soulmate.knowledge`: Markdown keyword and labeled-group parsing.
- `soulmate.text`: deterministic text normalization.

The pre-release AI-facing foundation skill set is maintained separately under
`packages/soulmate/skills/`. Its current foundation entries document contracts, resource
boundaries, Markdown knowledge resolution, text normalization, bounded data validation,
capability lifecycle, skill-manifest semantics, composition ownership, compatibility,
artifact provenance, and reproducibility. These skills are framework-neutral references; they
do not contain SoulMap routing, safety doctrine, voice, brand, or spiritual behavior.

Developers creating custom Soulmate foundation skills should follow [`CONTRIBUTING.md`](CONTRIBUTING.md). It defines ownership, neutral content rules, manifest registration, tests, artifact boundaries, and the PR review checklist.

SoulMap consumes these capabilities through public namespaces and an explicit adapter at `soulmap.runtime.knowledge`. The adapter may load only the five manifest entries that declare `soulmap-compatible`: contracts, resource boundaries, knowledge resolution, text normalization, and data validation. It accepts the canonical package-owned skill directory or a verified Soulmate ZIP/SKILL artifact, and it never discovers or activates undocumented files. Soulmate must never import `soulmap`, and SoulMap-specific framework behavior remains in the main SoulMap package.

## Release status

This package is prepared for a monorepo-managed GitHub Release artifact. It is not published to a public package registry by default. A release must pass the dedicated artifact boundary checks and require an explicit maintainer-triggered workflow input.
