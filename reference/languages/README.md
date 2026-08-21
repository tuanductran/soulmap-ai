---
name: "language-reference"
description: "Runtime-only language evidence and optional localized references for SoulMap."
---

# Language reference

This directory contains language-specific runtime evidence and optional localized
references that do not belong in the shipped SoulMap Skills package.

## Ownership boundary

The `skills/` directory remains the canonical English knowledge package for AI tools.
It owns doctrine, framework guidance, voice rules, safety guidance, and response
structure. This directory does not define SoulMap doctrine and must not become a second
source of truth for behavioral guidance.

Language evidence belongs here only when Python needs explicit, human-authored phrases
for deterministic detection. Each locale file must keep the same schema across
languages, include a locale code, and identify its source policy. Machine translation,
LLM-generated safety evidence, and external API calls are not accepted as substitutes
for human review.

## Current files

| File | Purpose | Consumer |
| --- | --- | --- |
| `<locale>/spiritual-bypass.json` | Human-authored spiritual-bypass and genuine-integration phrases | `spiritual_bypass_detector.py` |
| `vi/resources.json` | Optional Vietnamese resource recommendations | Future locale-aware tooling |

## Supported runtime evidence

The spiritual-bypass detector currently combines the English canonical phrases from
`skills/spiritual/spiritual-discernment.md` with reviewed locale evidence for `vi`, `es`,
`fr`, `zh`, and `ko`. The crisis detector has its separate protected language packs.
These two mechanisms must not be conflated: locale evidence is not a translation engine,
and matching a phrase does not prove the user's intent.

## Response language

Python does not translate generated responses. The underlying AI tool should answer in
the user's language while preserving the English SoulMap behavioral contract. Runtime
language data supports detection and tooling only. It does not add a response-writing
layer or a translation dependency.

## Adding a locale

Add a locale directory with a stable language code, use the existing JSON schema, write
human-authored phrases, add positive and near-miss tests, update the consuming runtime
loader, and run the full knowledge, safety, packaging, and evaluation gates. Do not add
localized doctrine copies under this directory.
