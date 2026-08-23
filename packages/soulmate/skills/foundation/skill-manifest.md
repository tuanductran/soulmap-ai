---
name: "soulmate-foundation-skill-manifest"
description: "Manifest rules for identifying, versioning, validating, and packaging explicit Soulmate foundation skills."
license: "MIT"
---

# Skill manifest

## Purpose

This skill defines the metadata contract for an AI-facing Soulmate foundation skill. A manifest makes ownership, identity, compatibility, source location, consumer scope, and artifact eligibility inspectable before a skill is loaded or shipped.

The manifest is an inventory and an allow-list. It is not a prompt router, dynamic plugin registry, safety policy, or permission system. A manifest entry describes what a skill is and where it may be distributed; it does not silently activate behavior.

## Use this skill when

Use this skill when adding a new foundation skill, changing a skill's public meaning, changing its compatibility range, or preparing a Soulmate skill artifact. Use it when a consumer needs to distinguish canonical source from generated output and when a reviewer needs to verify that every shipped entry has an owner and an explicit consumer.

Use it before building a separate artifact family. The artifact builder should read a validated manifest or an equivalent checked allow-list, not infer inclusion from every file present in a directory.

## Do not use this skill for

Do not use the manifest to define how an AI provider routes prompts, how a framework selects a response mode, or whether a user request is safe. Do not use it to grant filesystem, network, account, or publication permission. Those are separate operational or consumer contracts.

Do not add an entry for every incidental README, test fixture, generated file, cache, or private maintainer note. A manifest describes intentionally authored, reviewable skill content only.

## Manifest identity

The manifest itself has a schema version and a library identity. Each entry has an independent stable identifier and content version.

```text
manifest schema version
    → library identity
    → distribution policy
    → compatibility baseline
    → explicit skill entries
```

A stable skill identifier must be namespace-qualified and must not depend on a local filename alone. Renaming a file should not silently create a new identity if the content remains the same; changing the content's public meaning may require a new version or a new identifier according to the compatibility policy.

## Required top-level fields

The Soulmate foundation manifest uses these top-level fields:

| Field | Requirement | Meaning |
| --- | --- | --- |
| `schema_version` | Required | Version of the manifest structure itself |
| `library_id` | Required | Stable identity of the skill library |
| `display_name` | Required | Human-readable library name |
| `source_of_truth` | Required | Canonical repository-relative skill root |
| `distribution` | Required | Artifact family and publication state |
| `compatibility` | Required | Baseline compatibility for the skill collection |
| `entries` | Required, non-empty for a distributable library | Explicit skill entries |

The manifest schema version is not the same as a skill content version or Python package version. A schema change can affect every entry even when no skill text changes.

## Required entry fields

Every distributable skill entry must declare:

| Field | Requirement | Meaning |
| --- | --- | --- |
| `id` | Required and unique | Stable namespace-qualified skill identifier |
| `version` | Required | Version of the skill content contract |
| `owner` | Required and non-empty | Accountable maintainer or product boundary |
| `kind` | Required | Approved category such as `foundation` |
| `source` | Required and repository-relative | Canonical Markdown path inside the manifest source root |
| `consumers` | Required and non-empty | Explicit allowed consumers |
| `compatibility` | Required | Soulmate API/package compatibility range |
| `artifact` | Required | Artifact family allowed to include the entry |

The foundation entries may use `kind: "foundation"`, the `soulmate-ai` artifact family, and an explicit consumer list. The current neutral P0 entries approved for SoulMap use declare `consumers: ["soulmate-only", "soulmap-compatible"]`; the remaining P1/P2 entries remain `consumers: ["soulmate-only"]`. A shared entry must be reviewed separately and must name every allowed consumer rather than relying on a broad wildcard.

## Source and path rules

The `source` field points to one canonical authored Markdown file relative to `source_of_truth`. It must use portable repository-relative notation and must not be absolute, URL-based, generated, or outside the declared source root.

The manifest does not make a source path executable. A builder must read it as data, validate that the file exists, reject symlinks or forbidden paths according to its artifact contract, and copy only approved content into a clean staging tree.

A source path must not point into private maintainer configuration, generated caches, an unrelated product's skill tree, or a test-only fixture. If a skill needs an example, the example should be authored inside the skill as non-executable data or placed in a separately governed documentation area.

## Consumer and artifact semantics

`consumers` answers who is allowed to use the content. `artifact` answers which generated artifact family may ship it. These fields are related but not interchangeable.

For example, an entry may be Soulmate-only even though the package has several output formats. Conversely, a neutral entry might later be approved for both Soulmate and a framework consumer, but that approval must be explicit and tested. A consumer list does not automatically grant inclusion in another product's artifact.

The artifact builder must fail closed when an entry has an unknown consumer, unsupported artifact family, missing source, duplicate identifier, or incompatible version. It must not silently skip a malformed entry and produce a plausible-looking partial library.

## Versioning rules

Version the smallest public unit that can change independently:

| Change | Default review level |
| --- | --- |
| Typo or non-semantic wording correction | Content review; version impact assessed explicitly |
| Clarified rule that changes interpretation | Compatibility review and content version change |
| Changed accepted consumer or artifact | Distribution and ownership review |
| Changed manifest field or validation rule | Manifest schema review |
| Changed public foundation API referenced by the skill | Package compatibility review |
| Removed or renamed skill ID | Deprecation/migration review |

A version increment must not be used to conceal an ownership change or an artifact-boundary change. The manifest, skill front matter, release catalog, and generated filename/version metadata should agree when all are present.

## Validation workflow

Validate a manifest before any skill is loaded or packaged:

1. Parse the manifest as strict JSON.
2. Validate top-level required fields and schema version.
3. Validate that entry identifiers are unique and namespace-qualified.
4. Validate owner, kind, consumers, compatibility, and artifact values against approved vocabularies.
5. Resolve each source path beneath the declared source root.
6. Confirm that each source file exists, is regular data, and has the expected Markdown contract.
7. Confirm that the source set contains no undocumented extra entry intended for shipment.
8. Confirm version and artifact parity with the release operation.
9. Generate a deterministic file list and digest only after validation passes.
10. Record validation results in tests or release evidence.

Validation should fail before packaging begins. A builder must not repair a malformed manifest by guessing defaults, renaming entries, or discovering nearby files.

## Relationship to loading and routing

A manifest can describe a skill available to a consumer, but it does not decide when the skill is used. Activation requires an explicit consumer contract, loader, or integration adapter.

A consumer may select an entry by its stable ID after validating compatibility and confirming that its own adapter approves the consumer scope. SoulMap's adapter uses a fixed allow-list of approved IDs. A consumer must not scan the directory and treat every Markdown file as active behavior. A new file should be inert until it is intentionally added to the manifest, reviewed, and explicitly selected by the consumer adapter.

The manifest also does not override a consumer's policy. A skill marked compatible with a consumer still must be interpreted within that consumer's documented boundary. Compatibility means the entry can be consumed according to the declared contract; it does not mean the skill inherits the consumer's identity or policy.

## Distribution and provenance

A distributable artifact should preserve enough metadata to answer:

- which manifest schema was used;
- which library and skill versions were included;
- which canonical source files were selected;
- which artifact family was built;
- which compatibility baseline was declared; and
- which digest or verification evidence covers the output.

Generated files, archives, catalogs, and hashes are outputs. They are not new canonical skill sources. A release process must never edit generated artifacts by hand to make them appear consistent with a manifest.

The manifest may declare a pre-release or non-public distribution state. That state prevents a release from being mistaken for a public registry package, but it does not replace access control, secret governance, or maintainer approval.

## Common anti-patterns

**Directory-as-registry** treats every file in a folder as active without ownership or review.

**Filename identity** assumes a path is a stable skill ID and makes renames look like unrelated products.

**Wildcard consumer access** hides which frameworks are permitted to use a skill.

**Builder repair** fills missing fields or skips invalid entries so an artifact can still be produced.

**Version conflation** uses the Python package version, skill content version, and framework version as if they were one release identity.

**Generated-source drift** edits an archive, catalog, or generated copy instead of changing canonical Markdown and rebuilding.

**Manifest as policy** assumes metadata can replace routing, safety, authorization, or product governance.

## Review checklist

Before approving a manifest or entry, confirm that:

- the manifest schema version is supported;
- library and entry identifiers are stable and unique;
- every entry has one accountable owner;
- every source path is canonical, relative, regular, and inside the approved root;
- consumers and artifact family are explicit;
- compatibility ranges are meaningful and testable;
- unknown values fail closed;
- no directory-wide discovery is required for activation;
- version changes are explained by the public compatibility impact;
- clean-build file lists and hashes can be reproduced;
- the manifest does not contain private credentials or operational secrets.

## Expected outcome

A completed skill-manifest contract gives Soulmate a controlled inventory of foundation knowledge. It allows independent artifact building and future consumer integration without turning a directory into an implicit plugin system or allowing undocumented content to alter behavior.
