---
name: "soulmate-ai-skills-artifact-contract"
description: "The canonical contract for independently built Soulmate AI foundation and companion ZIP and SKILL artifacts."
license: "MIT"
---

# Soulmate AI skills artifact contract

## Status

This contract defines the pre-release `soulmate-ai` AI-facing artifact containing explicit foundation and companion skill entries. It is a build and verification contract, not a public registry or release authorization. The current distribution remains private until a maintainer approves a namespace, release policy, and publication mechanism.

## Artifact identity

The artifact family is `soulmate-ai`. Its content may contain framework-neutral foundation knowledge and explicitly Soulmate-owned companion behavior. Companion behavior must remain transparent, non-exclusive, non-manipulative, and compatible with host safety controls. The artifact is separate from the executable Soulmate Python package and separate from every SoulMap Framework artifact.

The artifact version is the shared version declared by the selected foundation skill entries. A future release may introduce a collection-level version, but the builder must not silently combine entries with different content versions.

## Canonical source

Canonical source is the package-owned directory `packages/soulmate/skills/`. The canonical manifest is `packages/soulmate/skills/manifest.json`. The artifact builder receives an explicit manifest and selects only its declared files.

The package README and license are sourced from the package boundary. Generated archives, extracted directories, checksum files, and provenance records are outputs; they must never become source inputs for a later build.

## Allowed artifact file set

The initial artifact has this layout. `SKILL.md` is the top-level AI-facing entrypoint; the remaining `skills/` files are explicit companion and foundation references selected by the manifest:

```text
SKILL.md
README.md
LICENSE
artifact-contract.md
manifest.json
PROVENANCE.json
skills/foundation/<manifest-selected Markdown files>
skills/companion/<manifest-selected Markdown files>
```

The exact `skills/foundation/` and `skills/companion/` sets are the manifest's ordered entry set. No file is included merely because it exists below the source directory.

Allowed file types are UTF-8 Markdown for skills and the explicitly named UTF-8 metadata files. The artifact contains no Python source, package build metadata, lockfile, test, website, private configuration, or generated repository state. `SKILL.md` is the only top-level behavioral entrypoint; the nested skills remain explicit references and are not dynamically activated.

## Formats

The builder creates two reviewable files:

```text
soulmate-ai.zip
soulmate-ai.skill
```

Both files are ZIP containers with byte-identical content for the initial contract. The `.skill` extension is a distribution projection for AI tooling; it does not change the canonical content or grant automatic activation.

The builder may also write `manifest.json`, `PROVENANCE.json`, and `SHA256SUMS` beside the artifacts for review. These sidecars are not automatically included in the archive unless this contract explicitly lists them.

## Manifest projection

The archive manifest is a projection of the canonical manifest. It contains the schema version, library identity, display name, source-of-truth declaration, artifact family, artifact contract metadata, artifact version, compatibility object, and normalized selected entries.

The projection must not invent entries, change source paths, widen consumer scope, or change compatibility. Its source paths are archive-relative paths under `skills/`, while its `source_of_truth` retains the canonical repository boundary.

## Allow-list and fail-closed behavior

The builder and verifier must fail closed when:

- the manifest is absent, malformed, unsupported, or missing required fields;
- a selected source path is absolute, traverses a parent, uses backslashes, or leaves the canonical root;
- an entry has a duplicate ID or source, an unsupported owner/kind/consumer/artifact, or a mismatched version;
- a selected Markdown file is missing, not UTF-8, missing required front matter, or contains a NUL byte;
- an unexpected file appears in the archive;
- an archive member is unsafe, duplicated, symlink-like, oversized, or outside the expected layout; or
- manifest, provenance, checksum, ZIP, and SKILL projections disagree.

An error must not be converted into an empty artifact or a successful partial build.

## Boundary exclusions

The Soulmate AI artifact must not contain the root SoulMap `skills/` tree, `src/soulmap/`, executable Python source, `reference/`, `.claude/`, `.github/`, tests, website exports, package lockfiles, or local build state. SoulMap-specific routing, crisis policy, safety doctrine, voice, brand, spiritual content, and provider behavior remain outside this artifact. Soulmate companion behavior must not be treated as a replacement for a host's safety or domain policy.

A boundary exclusion applies even when a file appears useful to a consumer. Inclusion requires a separate contract and explicit manifest entry; similarity of subject matter is not permission to cross ownership boundaries.

## Determinism

The ZIP writer sorts archive member names, uses fixed timestamps and regular-file metadata, and writes the same bytes for `.zip` and `.skill`. The builder must not depend on filesystem traversal order, current time, current working directory, local cache, or ambient environment except for an explicitly recorded source commit.

The first reproducibility gate compares the two projections byte-for-byte and compares repeated-build bytes. If a future toolchain prevents byte identity, the contract must name the lower evidence level rather than silently weakening verification.

## Provenance

`PROVENANCE.json` records the schema version, library identity, artifact family and version, manifest digest, source commit or `local`, selected entry IDs, ordered artifact file list, deterministic-build declaration, and verification status. It must not contain credentials, complete untrusted payloads, or private machine paths.

The provenance file list describes archive members, including `PROVENANCE.json` itself. The manifest digest covers the archive's projected `manifest.json` bytes.

## Integrity sidecar

`SHA256SUMS` records SHA-256 digests for `soulmate-ai.zip` and `soulmate-ai.skill` using the conventional two-space separator. The checksum sidecar does not include its own digest. Verification must reject missing records, malformed records, unexpected names, or mismatched bytes.

## Verification boundary

Verification occurs after generation and after extraction. A successful Python script exit alone is not sufficient evidence. The verifier must inspect both ZIP projections, compare their manifests and bytes, validate the expected file set, validate Markdown and JSON metadata, and check checksum records when supplied.

## Release boundary

Local build and CI artifact upload are permitted for review. Creating a GitHub Release, creating a tag, publishing a package registry artifact, or enabling automatic AI-tool activation requires a separate maintainer decision. The current contract does not authorize any of those actions.

## Review checklist

A Soulmate AI skills artifact is ready for review only when:

1. the canonical manifest and artifact contract validate;
2. the builder uses the explicit allow-list and clean output directory;
3. `.zip` and `.skill` are byte-identical;
4. the extracted file set contains only approved content;
5. provenance and manifest digests agree;
6. checksum verification passes;
7. repeated builds have the claimed deterministic parity; and
8. negative security tests cover path, content, metadata, archive, and integrity failures.

## Expected outcome

This contract gives Soulmate an independently reviewable AI skills artifact without making root SoulMap Skills, Python implementation, or product policy part of the same distribution boundary.
