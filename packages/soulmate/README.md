# Soulmate AI

Soulmate is the framework-neutral foundation library for SoulMap and future AI frameworks. It provides small, deterministic contracts and utilities without owning product doctrine, routing policy, voice, crisis handling, or web behavior.

## Current public surface

The first release-preparation package exposes:

- `soulmate.contracts`: explicit resource-reference contracts.
- `soulmate.data`: JSON parsing and mapping field validation.
- `soulmate.knowledge`: Markdown keyword and labeled-group parsing.
- `soulmate.text`: deterministic text normalization.

The pre-release AI-facing Soulmate skill artifact is maintained separately under
`packages/soulmate/skills/`. It contains two explicit groups: `foundation/` entries for
contracts, resource boundaries, Markdown knowledge resolution, text normalization, bounded
data validation, lifecycle, composition, compatibility, provenance, and reproducibility; and
`companion/` entries for Soulmate's transparent, warm, autonomy-preserving companion posture.
The companion entries are Soulmate-owned and `soulmate-only`; they are not SoulMap routing,
crisis policy, voice, brand, or spiritual doctrine, and they must not replace a host tool's
safety or domain policy.

Developers creating custom Soulmate foundation or companion skills should follow [`CONTRIBUTING.md`](CONTRIBUTING.md). It defines ownership, companion boundaries, manifest registration, tests, artifact boundaries, and the PR review checklist.

SoulMap consumes these capabilities through public namespaces and an explicit adapter at `soulmap.runtime.knowledge`. The adapter may load only the five manifest entries that declare `soulmap-compatible`: contracts, resource boundaries, knowledge resolution, text normalization, and data validation. It accepts the canonical package-owned skill directory or a verified Soulmate ZIP/SKILL artifact, and it never discovers or activates undocumented files. Soulmate must never import `soulmap`, and SoulMap-specific framework behavior remains in the main SoulMap package.

## Release status

This package is prepared for a monorepo-managed GitHub Release artifact. It is not published to a public package registry by default. A release must pass the dedicated artifact boundary checks and require an explicit maintainer-triggered workflow input.
