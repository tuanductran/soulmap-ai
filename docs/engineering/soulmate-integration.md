# Soulmate integration contract

## Purpose

Soulmate is the framework-neutral foundation library. SoulMap is the opinionated consumer framework. This document defines the explicit seam by which SoulMap may consume a reviewed subset of Soulmate AI foundation skills without turning the Soulmate directory into an implicit plugin registry.

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

Lifecycle, manifest, composition, compatibility, provenance, and reproducibility entries remain `soulmate-only` until a separate ownership and integration review approves them. SoulMap crisis policy, response safety, routing, voice, brand, spiritual content, and framework behavior remain SoulMap-owned.

## Explicit loading API

The adapter accepts either the canonical package-owned source directory or a generated Soulmate ZIP/SKILL artifact. The caller must provide a stable ID; the adapter does not scan for Markdown files and does not infer activation from filenames.

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

The returned value contains the stable ID, content version, canonical source path, and UTF-8 Markdown content. The adapter returns knowledge; SoulMap owns interpretation, composition, routing, policy, and presentation.

## Fail-closed rules

Before returning a skill, the loader validates the manifest identity, schema, source-of-truth path, artifact contract, entry ownership, compatibility metadata, consumer vocabulary, source path, Markdown front matter, UTF-8 content, NUL-byte absence, and selected file size. For ZIP/SKILL sources it also enforces archive member and uncompressed-size bounds, verifies deterministic provenance, manifest digest, file list, and selected-entry list, and rejects unsafe paths, symlink-like members, duplicate members, missing selected files, extra archive members, malformed archives, and an archive file set that disagrees with its manifest.

A request for an unapproved ID, including a valid Soulmate-only entry, fails with `SoulmateSkillLoadError`. An undocumented Markdown file remains inert. A malformed manifest or artifact is never converted into an empty or partial success.

## Artifact and release boundary

The canonical source remains `packages/soulmate/skills/`. The independent Soulmate skills builder continues to use an explicit manifest allow-list and produces the private pre-release `soulmate-ai.zip` and `soulmate-ai.skill` artifacts. The adapter consumes those artifacts for review or local framework composition; it does not authorize a release, registry publication, automatic AI-tool activation, or a GitHub Release.

The root SoulMap artifact builder remains separate. It must not absorb the Soulmate package-owned skill tree merely because an adapter exists. Any future shared entry requires a manifest change, contract tests, artifact review, and confirmation that the entry is genuinely framework-neutral.

## Validation

The integration contract is protected by `tests/contract/test_soulmate_adapter_contract.py`, `tests/contract/test_soulmate_foundation_skills_contract.py`, the Soulmate artifact verifier tests, the one-way dependency contract, and the normal repository static and artifact checks. The recommended local commands are:

```bash
uv run pytest -q tests/contract/test_soulmate_adapter_contract.py
uv run pytest -q tests/contract/test_soulmate_foundation_skills_contract.py
uv run python scripts/build_soulmate_skills.py
uv run python scripts/verify_soulmate_skills.py \
  --zip dist/soulmate-skills/soulmate-ai.zip \
  --skill dist/soulmate-skills/soulmate-ai.skill \
  --version 0.1.0 \
  --checksums dist/soulmate-skills/SHA256SUMS
```
