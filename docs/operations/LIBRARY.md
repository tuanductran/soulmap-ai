# SoulMap AI Library

SoulMap AI Library v1 is the repository's versioned catalog and distribution index for the SoulMap knowledge skills. It gives every release a stable identity, compatibility description, release URL, and cryptographic record for the two shipped archives.

> The Library is a **versioned catalog and distribution contract**, not an automatic installer or a public marketplace registration.

## Source catalog

The source catalog is [`../../library/catalog.json`](../../library/catalog.json). It is intentionally small and human-reviewable. The catalog owns Library identity, skill entries, source-of-truth paths, compatibility surfaces, and the manual-upload boundary. It does not duplicate the runtime phrase lists owned by Python or rewrite `.claude-plugin/marketplace.json`.

The catalog has six entries: Brand, Core Frameworks, Safety Guardrails, Meta Guidance, Spiritual Layer, and Voice System. Each entry points to one directory under `skills/`, while [`SKILL.md`](../../SKILL.md) and [`AGENTS.md`](../../AGENTS.md) remain the governing root documents.

## Generate a release manifest

Run the following command from any directory inside the repository:

```bash
uv run soulmap library-manifest
```

The command builds both distribution archives and writes `dist/soulmap-ai-library.json`. The generated manifest takes the project version from `pyproject.toml`, resolves the corresponding GitHub Release URL, and records the byte size and SHA-256 digest of each archive.

Verify those exact files before upload with:

```bash
uv run python scripts/verify_artifact_hashes.py
```

The verifier is local-only and does not contact GitHub. It fails with a non-zero exit code if the manifest is missing or invalid, an artifact is missing, its byte size differs, or its SHA-256 digest differs. A successful run prints one `PASS` line per artifact.

The three files have distinct roles:

| File | Role |
| --- | --- |
| `dist/soulmap-ai-library.json` | Versioned catalog, compatibility metadata, release URL, artifact sizes and SHA-256 digests |
| `dist/soulmap-ai.zip` | Standard knowledge archive without `.claude-plugin/` |
| `dist/soulmap-ai.skill` | Skill-oriented archive with `.claude-plugin/` preserved |

The manifest is generated after the archives, so its hashes describe the exact files produced by that command. Do not hand-edit generated artifact metadata. Re-run the command after a build or version change.

## Installation boundary

Library v1 supports **manual upload** to compatible tools. The manifest does not claim automatic installation, background synchronization, or platform acceptance. Use [`UPLOAD.md`](UPLOAD.md) for platform-specific instructions.

For a compatible Skills runtime, upload or unpack `dist/soulmap-ai.skill` without changing internal paths. For document-based project knowledge, use `dist/soulmap-ai.zip` or extract it and upload the supported Markdown files. Keep `.claude-plugin/marketplace.json` opaque during packaging and upload.

Platform behavior must be recorded separately in the internal launch checklist. Repository tests verify package structure and metadata; they do not claim to prove a third-party platform's live behavior.

## Release procedure

Before a release, run the repository workflow described in [`../../docs/engineering/DEV.md`](../engineering/DEV.md), then run `uv run soulmap library-manifest`. The release workflow should publish all three files under the matching Git tag:

```text
https://github.com/tuanductran/soulmap-ai/releases/tag/v{version}
```

A release reviewer should verify that the manifest version equals the tag, both artifact paths exist, the recorded sizes match the downloaded files, and the SHA-256 values recompute successfully. The release workflow runs `scripts/verify_artifact_hashes.py` before upload. Any mismatch is a release failure, not a reason to edit the manifest manually.

## Non-goals

Library v1 does not add a hosted service, a database, an LLM dependency, a semantic safety classifier, a one-click installer, or an unreviewed public marketplace adapter. Those capabilities require separate platform ownership and acceptance evidence under Phase 11 of the roadmap.
