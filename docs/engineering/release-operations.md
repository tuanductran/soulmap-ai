# Release operations

This document defines the operational contract for SoulMap releases. It is deliberately separate from shipped SoulMap knowledge and runtime response behavior.

## Release provenance

The release workflow creates two machine-readable summaries:

- `dist/release-verification.json` - artifact and integration contract results.
- `dist/release-provenance.json` - release version, exact source commit, UTC timestamp, and SHA-256 hashes for every published artifact.

The provenance source commit is the exact commit produced by the version bump step, not the workflow's original dispatch SHA. The provenance file is retained as a workflow artifact and published with the GitHub Release.

Manual verification:

```bash
uv run soulmap release-verify --root . --output dist/release-verification.json
uv run soulmap release-provenance --root . --verification dist/release-verification.json
uv run soulmap release-health --root . --provenance dist/release-provenance.json
```

A release must not be promoted if either verification or health fails.

## Health check

`release-health` rebuilds the release verification state and then checks that provenance:

1. has schema version `1` and status `pass`;
2. matches the checked-out package version;
3. identifies a full Git commit SHA matching the checked-out commit;
4. contains exactly the three published package artifacts; and
5. matches each artifact's size and SHA-256 digest.

The check does not access user conversations, memory, or other sensitive data.

## Rollback

Rollback means selecting a previously published, known-good version rather than rewriting a release tag. Never force-move an existing release tag.

Before switching consumers back to a previous version, run the **Rollback Verification** workflow and supply the previous release tag, for example `v0.11.0`. The workflow checks out that immutable tag and verifies the package version, repository contracts, release artifacts, and tag/version correspondence.

The rollback procedure is:

1. Identify the last known-good release tag.
2. Run `Rollback Verification` for that tag.
3. Proceed only when the workflow reports `rollback_ready: true`.
4. Point the affected distribution/consumer surface at that existing release.
5. Do not modify the old tag or release contents.
6. After recovery, investigate the failed release independently; do not weaken the release contracts to make it pass.

## Promotion boundary

The release workflow verifies repository contracts, package artifacts, integration guides, provenance, and health **before** pushing the version bump/tag and creating the GitHub Release. Operational metadata is not included in `SOULMAP.md`, runtime memory, safety logic, or response-generation knowledge.
