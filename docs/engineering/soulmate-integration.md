# Soulmate integration contract

## Purpose

Soulmate is the independent library with two AI-facing layers: reusable foundation skills and a Soulmate-owned companion skill family. SoulMap is the opinionated consumer framework. This document defines the explicit seam by which SoulMap may consume a reviewed subset of Soulmate foundation skills without turning the Soulmate directory into an implicit plugin registry.

The adapter is consumer-owned and lives at `soulmap.runtime.knowledge`. Soulmate does not import SoulMap, read SoulMap configuration, or decide routing, safety, voice, brand, spiritual, or presentation policy.

## Approved skill scope

Only the following five neutral foundation entries are currently approved for SoulMap consumption:

| Stable ID | Foundation concern | Consumer declaration |
| --- | --- | --- |
| `soulmate.foundation.contracts` | Shared input/result/failure contract vocabulary | `soulmate-only`, `soulmap-compatible` |
| `soulmate.foundation.resource-boundaries` | Explicit resource references and loader seams | `soulmate-only`, `soulmap-compatible` |
| `soulmate.foundation.knowledge-resolution` | Deterministic Markdown section resolution | `soulmate-only`, `soulmap-compatible` |
| `soulmate.foundation.text-normalization` | Conservative lexical normalization | `soulmate-only`, `soulmap-compatible` |
| `soulmate.foundation.data-validation` | Bounded JSON parsing and basic field validation | `soulmate-only`, `soulmap-compatible` |

Lifecycle, manifest, composition, compatibility, provenance, and reproducibility entries remain `soulmate-only` until a separate ownership and integration review approves them. The new `companion/` entries are also `soulmate-only`: they define Soulmate's transparent, warm, non-exclusive companion posture and are not part of the SoulMap approval projection. SoulMap crisis policy, response safety, routing, voice, brand, spiritual content, and framework behavior remain SoulMap-owned.

## Soulmate companion skill family

The independent Soulmate AI artifact now contains an explicit `companion/` family alongside the generic `foundation/` family. Companion entries cover identity, presence, reflective listening, emotional attunement, gentle inquiry, boundaries and consent, grounded companionship, human connection, repair, and session closure. They are written for Soulmate users and are not generic clinical advice, spiritual authority, or a replacement for the host tool's safety policy.

The companion family must remain transparent about being AI, avoid exclusivity and emotional manipulation, preserve human relationships and user agency, accept correction, and make it easy to pause or leave. Its manifest entries use `kind: companion` and `consumers: ["soulmate-only"]`. SoulMap's adapter does not load these entries because its generated projection contains only the five explicitly approved neutral foundation IDs.

## Explicit loading API

The adapter accepts either the canonical package-owned source directory or a generated Soulmate ZIP/SKILL artifact. In an external AI host, the artifact's top-level `SKILL.md` is the orientation and reading-order entrypoint; nested foundation and companion files remain explicit references. The Python adapter still loads only a caller-provided stable ID; it does not scan for Markdown files and does not infer activation from filenames.

```python
from pathlib import Path

from soulmap.runtime.knowledge import SoulmateSkillLoader

loader = SoulmateSkillLoader(
    Path("packages/soulmate/skills")
)
contracts = loader.load("soulmate.foundation.contracts")
```

To load the complete approved set in the adapter's fixed, reviewable order:

```python
approved = SoulmateSkillLoader(
    Path("dist/soulmate-skills/soulmate-ai.zip")
).load_approved()
```

The `SoulMapSoulmateAdapter` facade is available when a consumer wants an explicitly named framework seam rather than using the loader directly:

```python
from pathlib import Path

from soulmap.runtime.knowledge import (
    SoulMapSoulmateAdapter,
    SoulmateSkillLoader,
)

adapter = SoulMapSoulmateAdapter(
    SoulmateSkillLoader(Path("packages/soulmate/skills"))
)
skill = adapter.load_foundation_skill(
    "soulmate.foundation.knowledge-resolution"
)
```

The returned value contains the stable ID, content version, compatibility range, canonical source path, and UTF-8 Markdown content. The adapter returns knowledge; SoulMap owns interpretation, composition, routing, policy, and presentation.

### Foundation bundle composition

When SoulMap needs the reviewed foundation set rather than one skill, it may use the explicit bundle seam:

```python
bundle = adapter.load_foundation_bundle()
contracts = bundle.get("soulmate.foundation.contracts")
```

The bundle is immutable, contains exactly the five approved IDs in the adapter's fixed reviewable order, and exposes one shared content version and compatibility range. Bundle construction fails closed if a loader returns an incomplete set or if approved entries disagree on version or compatibility. The bundle does not select a framework, route a message, apply safety policy, or activate AI-tool behavior.

## Fail-closed rules

Before returning a skill, the loader validates the manifest identity, schema, source-of-truth path, artifact contract, entry ownership, compatibility metadata, consumer vocabulary, source path, Markdown front matter, UTF-8 content, NUL-byte absence, and selected file size. For ZIP/SKILL sources it also enforces archive member and uncompressed-size bounds, verifies deterministic provenance, manifest digest, file list, and selected-entry list, and rejects unsafe paths, symlink-like members, duplicate members, missing selected files, extra archive members, malformed archives, and an archive file set that disagrees with its manifest.

A request for an unapproved ID, including a valid Soulmate-only entry, fails with `SoulmateSkillLoadError`. An undocumented Markdown file remains inert. A malformed manifest or artifact is never converted into an empty or partial success.

## Manifest sync and consumer approval contract

The canonical Soulmate manifest declares which consumers may use an entry, but that capability metadata is not an activation signal. SoulMap's reviewed consumer decision is a separate, SoulMap-owned contract at `src/soulmap/runtime/knowledge/soulmate_consumer_scope.json`. It records the consumer identity, library identity, required package compatibility, and the exact ordered approval entries with their IDs, versions, compatibility ranges, and source paths.

The committed `_soulmate_consumer_scope.py` file in the same SoulMap-owned directory is a deterministic generated projection of that approval JSON. Runtime code imports the projection rather than scanning the Soulmate package or deriving approval from the library manifest at runtime. To update the approved set, a maintainer must edit the JSON approval file explicitly, review the diff, regenerate the projection, and run the fail-closed verifier:

```bash
uv run python scripts/verify_soulmate_consumer_sync.py --write-projection --report
uv run python scripts/verify_soulmate_consumer_sync.py --check
```

The verifier rejects malformed or unknown fields, unsupported consumer values, duplicate IDs or sources, unsafe paths, missing or extra approvals, ID/source/version/compatibility mismatches, order drift, package compatibility drift, stale projections, and non-Soulmate foundation entries. It never silently grants `soulmap-compatible`; the approval JSON remains the explicit human-reviewed decision. The Soulmate skills CI runs `--check` before building or verifying the `.zip` and `.skill` artifacts.

The approval JSON and generated projection are excluded from Soulmate artifacts. They are SoulMap consumer metadata, not generic Soulmate or companion content, and must never be copied into `packages/soulmate/skills/` or the Soulmate artifact allow-list.

## Artifact and release boundary

The canonical source remains `packages/soulmate/skills/`. The independent Soulmate skills builder continues to use an explicit manifest allow-list and produces the private pre-release `soulmate-ai.zip` and `soulmate-ai.skill` artifacts. The adapter consumes those artifacts for review or local framework composition; it does not authorize a release, registry publication, automatic AI-tool activation, or a GitHub Release.

The root SoulMap artifact builder remains separate. It must not absorb the Soulmate package-owned skill tree merely because a Python adapter exists. For AI-facing use, the explicit `soulmap-with-soulmate-ai` composition builder creates a third artifact that materializes the reviewed Soulmate skills under `soulmate/` and adds a top-level precedence contract. This composed artifact is separate from both `soulmap-ai` and `soulmate-ai`; it is the import surface for an external AI tool when SoulMap should run on top of Soulmate. Any future change to its scope requires a composition manifest change, contract tests, artifact review, and confirmation that the content remains appropriately owned. The standalone root SoulMap artifact remains backward-compatible and does not include Soulmate content.

## Validation

The integration contract is protected by `tests/contract/test_soulmate_adapter_contract.py`, `tests/contract/test_soulmate_consumer_sync_contract.py`, `tests/contract/test_soulmate_foundation_skills_contract.py`, `tests/contract/test_soulmate_companion_skills_contract.py`, `tests/contract/test_soulmap_soulmate_composition_contract.py`, `tests/contract/test_soulmap_soulmate_workflow_contract.py`, the Soulmate artifact verifier tests, the one-way dependency contract, and the normal repository static and artifact checks. The recommended local commands are:

```bash
uv run python scripts/verify_soulmate_consumer_sync.py --check
uv run soulmap build-composed --output-dir dist/soulmap-with-soulmate-ai
uv run python scripts/verify_soulmap_with_soulmate.py \\
  --zip dist/soulmap-with-soulmate-ai/soulmap-with-soulmate-ai.zip \\
  --skill dist/soulmap-with-soulmate-ai/soulmap-with-soulmate-ai.skill
uv run pytest -q tests/contract/test_soulmate_adapter_contract.py
uv run pytest -q tests/contract/test_soulmate_consumer_sync_contract.py
uv run pytest -q tests/contract/test_soulmate_foundation_skills_contract.py
uv run pytest -q tests/contract/test_soulmate_companion_skills_contract.py
uv run python scripts/build_soulmate_skills.py
uv run python scripts/verify_soulmate_skills.py \
  --zip dist/soulmate-skills/soulmate-ai.zip \
  --skill dist/soulmate-skills/soulmate-ai.skill \
  --version 0.1.0 \
  --checksums dist/soulmate-skills/SHA256SUMS
```
