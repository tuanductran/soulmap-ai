---
name: "soulmate-foundation-artifact-provenance"
description: "Provenance rules for selecting, building, verifying, and reviewing independent Soulmate foundation skill artifacts."
license: "MIT"
---

# Artifact provenance

## Purpose

This skill defines how an independent Soulmate foundation skill artifact is traced from canonical source to generated output. Provenance makes the selected content, manifest, builder, compatibility, file list, and verification evidence visible to reviewers.

An artifact is a generated distribution boundary. It is not a new source of truth and it must not silently inherit files from the SoulMap Framework artifact.

## Use this skill when

Use this skill when building or reviewing a Soulmate AI-facing archive, skill package, catalog, or other generated distribution. Use it when changing the artifact allow-list, source root, manifest, builder, verifier, or release workflow.

Use it before a release review even when the artifact is private or pre-release. A private artifact can still leak unrelated source, generated files, credentials, or product-only doctrine.

## Do not use this skill for

Do not use this skill to authorize a public release, grant registry credentials, define a package owner's legal policy, or replace access control. Provenance demonstrates what was built; it does not grant permission to publish.

Do not treat a generated archive, extracted directory, release page, or catalog copy as canonical source. Corrections must be made in the authored source and rebuilt.

## Provenance chain

The minimum provenance chain is explicit and ordered:

```text
canonical source
    → manifest validation
    → explicit allow-list
    → clean staging tree
    → generated artifact
    → extraction and boundary verification
    → manual release review
```

Each arrow should be reproducible or inspectable. A builder must fail before output when the manifest is invalid, a source is missing, a path escapes the source root, or a forbidden product surface is selected.

## Canonical source

For Soulmate foundation skills, canonical Markdown source lives under the package-owned skill boundary. The manifest identifies the approved source root and each selected file. The Python implementation remains canonical in its own source boundary; a Markdown skill may explain a public capability but does not replace its executable contract.

Canonical source must be authored, reviewable, and free from generated caches, local machine paths, private configuration, credentials, and unrelated product content. A source file must not be selected merely because a directory scan found it.

## Allow-list selection

Artifact selection is fail-closed. The builder should include only entries that:

- are present in the validated manifest;
- have a supported kind, owner, consumer scope, compatibility range, and artifact family;
- resolve to regular files beneath the declared source root;
- pass the Markdown/content contract; and
- are approved for the artifact being built.

Unknown files may remain in the working tree for development, but they must not enter the artifact without an explicit manifest entry. Unknown manifest entries must not be silently ignored.

A Soulmate artifact must not include the root SoulMap `skills/` tree, `src/soulmap/`, `reference/`, website output, `.claude/`, tests, local configuration, or generated build state unless a future ADR explicitly changes that boundary.

## Clean staging

Build from a clean staging tree rather than packaging the repository root. A staging tree should contain only the selected metadata, canonical Soulmate skill source, required license/readme files, and any explicitly approved manifest or provenance file.

The staging directory must be newly created or emptied before use. Reusing a dirty staging directory risks shipping deleted, stale, or locally generated files. The builder must not follow symlinks outside the approved root or copy paths that resolve outside the staging boundary.

## Generated artifact records

A provenance record should identify:

| Record | Required meaning |
| --- | --- |
| Library identity | Which Soulmate library produced the artifact |
| Artifact family | Which output family was built |
| Manifest schema | Which manifest structure was validated |
| Selected entries | Skill IDs and content versions included |
| Source list | Canonical relative paths selected |
| Compatibility | Package/content compatibility baseline |
| Build input | Builder version or source commit used |
| File digests | Hashes for selected files or final artifact |
| Verification result | Boundary and parity checks that passed |

The record must not include secrets or complete untrusted payloads. If a build is not reproducible yet, state that limitation rather than presenting a timestamp or local path as reproducibility evidence.

## Extraction verification

Verification must inspect the artifact after generation, not only the staging tree before generation. Extract into a fresh temporary directory and confirm:

- expected files are present;
- forbidden paths and extensions are absent;
- no path traversal entries exist;
- file names and versions agree with the manifest;
- selected content matches canonical source where parity is required;
- archive entries are regular files within the expected root; and
- no credentials, private paths, or generated repository state are present.

A successful build is not a successful release until the generated artifact and its extracted form pass the boundary checks.

## Soulmate and SoulMap artifact separation

Soulmate and SoulMap have different artifact identities:

| Artifact | Owns | Must not inherit |
| --- | --- | --- |
| Soulmate foundation skill artifact | Framework-neutral foundation Markdown and its manifest/provenance | SoulMap doctrine, routing, safety, voice, brand, spiritual content, web output, or Python source |
| Soulmate Python package | `src/soulmate/` executable foundation library | SoulMap package modules and product-only runtime |
| SoulMap AI artifact | Root SoulMap Skills and its package metadata | Soulmate-only skill content unless an explicit compatibility decision approves a shared entry |

A package dependency does not automatically authorize content inheritance. The one-way Python dependency and the AI artifact boundary are related but separately validated decisions.

## Release review

A maintainer release review should confirm the manifest, source list, staging log, artifact verification, digest record, version/tag choice, and publication authorization. The review should be possible without trusting a generated archive's own claims.

A manual GitHub Release or registry publication is a separate decision from a successful local build. It requires an approved namespace, credentials or trusted publishing arrangement, ownership, rollback plan, and explicit approval.

## Common anti-patterns

**Repository-root packaging** ships unrelated SoulMap source or local files because the build context is too broad.

**Directory scan inclusion** makes a new file shippable without review.

**Dirty staging** carries stale files from a previous build.

**Pre-build-only verification** assumes the archive matches the staging tree without inspecting extraction.

**Hash-only provenance** proves bytes but not that the selected bytes belong to the intended artifact boundary.

**Generated-source editing** changes an archive or catalog rather than canonical source.

**Release conflation** treats successful build, GitHub Release creation, and public registry publication as one authorization.

## Review checklist

Before approving an artifact, confirm that:

- canonical source and manifest root are named;
- selection uses an explicit allow-list;
- the staging tree is clean and symlink/path safe;
- only approved Soulmate content is present;
- the artifact is extracted and scanned after build;
- file list, versions, compatibility, and digests are consistent;
- no SoulMap-only surface leaked into Soulmate output;
- provenance contains no secrets or private machine paths;
- publication authorization is separate from build verification;
- generated output can be deleted and recreated from canonical source.

## Expected outcome

A completed provenance contract makes an independent Soulmate artifact auditable from source to output. It protects the foundation library from accidental SoulMap inheritance and gives future consumers confidence about what they are installing or importing.
