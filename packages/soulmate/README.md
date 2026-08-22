# Soulmate AI

Soulmate is the framework-neutral foundation library for SoulMap and future AI frameworks. It provides small, deterministic contracts and utilities without owning product doctrine, routing policy, voice, crisis handling, or web behavior.

## Current public surface

The first release-preparation package exposes:

- `soulmate.contracts`: explicit resource-reference contracts.
- `soulmate.data`: JSON parsing and mapping field validation.
- `soulmate.knowledge`: Markdown keyword and labeled-group parsing.
- `soulmate.text`: deterministic text normalization.

SoulMap consumes these capabilities through public namespaces. Soulmate must never import `soulmap`, and SoulMap-specific framework behavior remains in the main SoulMap package.

## Release status

This package is prepared for a monorepo-managed GitHub Release artifact. It is not published to a public package registry by default. A release must pass the dedicated artifact boundary checks and require an explicit maintainer-triggered workflow input.
