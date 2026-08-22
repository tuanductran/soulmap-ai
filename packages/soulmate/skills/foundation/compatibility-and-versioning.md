---
name: "soulmate-foundation-compatibility-and-versioning"
description: "Compatibility and versioning rules for Soulmate package APIs, foundation skill content, manifests, and explicit consumers."
license: "MIT"
---

# Compatibility and versioning

## Purpose

This skill defines how Soulmate records and evaluates compatibility across executable library APIs, AI-facing foundation skill content, manifests, artifacts, and consumers. It prevents unrelated version identities from being collapsed into one number and makes compatibility decisions reviewable.

Compatibility is a statement about an observable contract. It is not a promise that every consumer workflow, provider, domain policy, or product presentation will remain unchanged.

## Use this skill when

Use this skill when changing a public input or result shape, error category, resource rule, lifecycle guarantee, Markdown skill meaning, manifest field, artifact inclusion rule, or consumer adapter.

Use it before publishing a new package or skill artifact, widening the consumer list, deprecating a skill ID, or changing a compatibility range.

## Do not use this skill for

Do not use one version number to represent the Soulmate Python package, Soulmate AI skill content, SoulMap framework, website, or provider integrations. Do not use a version increment to hide an ownership transfer, a safety-policy change, or an artifact-boundary change.

Do not infer compatibility from similar filenames, passing imports, or the fact that a consumer happens to work in one local checkout. Compatibility must be tied to documented and testable behavior.

## Independent version identities

Soulmate has several version identities:

| Version identity | Owner | What it covers |
| --- | --- | --- |
| Package version | Soulmate Python package | Public executable modules, types, protocols, accepted values, and failure behavior |
| Skill content version | Individual foundation skill | Meaning and instructions of one AI-facing Markdown skill |
| Manifest schema version | Skill manifest owner | Structure and validation rules of the manifest itself |
| Artifact version | Release operation | Selected content and output metadata for one generated artifact family |
| Consumer framework version | Consumer owner | Consumer routing, policy, presentation, and product behavior |

A consumer may record all of these identities in release evidence, but a change to one does not automatically change the others.

## Compatibility dimensions

Evaluate compatibility across at least these dimensions:

| Dimension | Question |
| --- | --- |
| Input | Can existing valid inputs still be accepted with the same meaning? |
| Result | Can consumers read the result shape and interpret it the same way? |
| Failure | Are failure categories, codes, and stopping behavior preserved? |
| Resource | Are references, encodings, limits, and loader seams unchanged? |
| Lifecycle | Are stage order, omission rules, side effects, and cancellation guarantees preserved? |
| Content | Does the skill still teach the same contract and boundaries? |
| Manifest | Can existing validators read and validate the metadata? |
| Artifact | Does the same artifact family include the same approved content? |
| Consumer | Does the declared consumer still satisfy the entry's requirements? |

A change can be compatible in one dimension and breaking in another. Record the affected dimension instead of reducing the decision to a vague "minor update."

## Change classification

The following classification is a default starting point, not a substitute for review:

| Change | Typical impact |
| --- | --- |
| Typo or formatting-only correction with unchanged meaning | Patch-level content review |
| Clarification that changes a reasonable interpretation | Content compatibility review; version change likely required |
| New optional field or operation with preserved defaults | Additive package/content review |
| New required input, new required manifest field, or removed accepted value | Breaking compatibility review |
| New failure category or changed failure stopping point | Contract compatibility review |
| Changed source ownership or consumer permission | Ownership/distribution review, even if code is unchanged |
| Changed artifact inclusion or exclusion | Artifact and release review |
| Removed or renamed public ID | Deprecation and migration review |

When uncertain, prefer the narrower compatibility range and require an explicit migration note.

## Range rules

A compatibility range states which versioned contract a consumer can use. It should be specific enough to reject known incompatible combinations and broad enough to avoid unnecessary pinning.

A range must not be widened merely because a local test passes. Widen it only after tests cover the public behavior across the claimed range or the range is otherwise justified by a stable contract.

A skill entry's compatibility range refers to the Soulmate package/content contract it requires. It does not authorize the skill for an unlisted framework or guarantee compatibility with a provider's prompt behavior.

## Deprecation and migration

Deprecate before removal when consumers need time to migrate. A deprecation record should name the stable ID or API, explain the replacement, state the last compatible range, and define when removal may occur.

Do not silently alias two semantic identities forever. An alias is appropriate only when the old and new contracts are demonstrably equivalent and the alias has an owner and a removal plan.

A migration should update canonical source, manifest, tests, artifact evidence, and consumer documentation together. Editing generated output alone does not complete a migration.

## Consumer compatibility

A consumer is compatible only when it uses public foundation contracts and respects their failure semantics, resource limits, lifecycle ordering, and content boundaries.

A consumer may add stricter validation or product policy after the foundation result. It must not claim that a foundation version includes its own routing, safety, voice, brand, or domain rules.

Compatibility should be checked before activation or packaging. A consumer that cannot satisfy a required range should fail clearly rather than activate a partial or guessed integration.

## Manifest and artifact parity

For a generated artifact, record enough identity to reproduce what was selected:

```text
manifest schema
    + library/package compatibility
    + skill IDs and content versions
    + consumer scope
    + artifact family
    = release selection
```

The artifact filename, manifest, release catalog, and verification report should agree where they express the same identity. A mismatch is a release failure, not a cosmetic warning.

## Test matrix

Compatibility work should include focused tests for:

| Case | Expected evidence |
| --- | --- |
| Existing valid input | Previous meaning and result remain stable |
| Existing invalid input | Failure category and stopping behavior remain inspectable |
| Added optional field | Old consumers continue with documented defaults |
| Removed/renamed field or ID | Migration test or intentional breaking-change evidence exists |
| Manifest schema change | Old and new validators behave according to migration policy |
| Package/content mismatch | Validation rejects incompatible selection |
| Consumer outside allow-list | Activation or packaging fails closed |
| Artifact version mismatch | Release verification rejects the artifact |

## Common anti-patterns

**Single-version thinking** treats all repository surfaces as one product release.

**Range inflation** widens compatibility without evidence.

**Hidden breaking change** changes failure, resource, or interpretation semantics under a patch-level label.

**Ownership laundering** treats a new consumer or product policy as a harmless compatibility update.

**Generated-file versioning** edits an archive or catalog without changing canonical source.

**Permanent aliasing** keeps old and new semantic identities indistinguishable without a migration plan.

## Review checklist

Before approving a compatibility change, confirm that:

- the affected version identity is named;
- input, result, failure, resource, lifecycle, content, manifest, and artifact dimensions were considered;
- the compatibility range is supported by tests or explicit evidence;
- ownership and consumer scope remain explicit;
- deprecation and migration are documented when needed;
- generated outputs will be rebuilt from canonical source;
- package, skill, manifest, artifact, and consumer versions are not conflated;
- no product policy has been smuggled into the foundation contract.

## Expected outcome

A completed compatibility and versioning contract lets Soulmate evolve without making every consumer adopt the same release cadence. It protects the one-way library-framework relationship by making each public boundary and its compatibility evidence explicit.
