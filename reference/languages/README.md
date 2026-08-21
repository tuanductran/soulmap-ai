---
name: "language-reference"
description: "Packaged Markdown language evidence and optional localized references for SoulMap."
---

# Language reference

This directory contains packaged Markdown language evidence and optional localized
references that are loaded alongside the shipped SoulMap Skills package.

## Ownership boundary

The `skills/` directory remains the canonical English knowledge package for AI tools.
It owns doctrine, framework guidance, voice rules, safety guidance, and response
structure. This directory provides signal evidence and optional resource references only;
it does not define SoulMap doctrine and must not become a second source of truth for
behavioral guidance.

Language evidence belongs here only when a supported detector needs explicit,
human-authored phrases for deterministic detection. Each locale file must keep the same
schema across languages, include a locale code, and identify its source policy. Machine
translation and LLM-generated safety evidence are not accepted as substitutes for human
review.

## Current files

| File | Purpose | Consumer |
| --- | --- | --- |
| `<locale>/spiritual-bypass.md` | Human-authored spiritual-bypass and genuine-integration phrases | Spiritual-bypass runtime detector |
| `vi/resources.md` | Optional Vietnamese resource recommendations | Future locale-aware tooling |

## Supported runtime evidence

The spiritual-bypass detector currently combines the English canonical phrases from
`skills/spiritual/spiritual-discernment.md` with reviewed locale evidence for `vi`, `es`,
`fr`, `zh`, and `ko`. The crisis detector has its separate protected language packs.
These two mechanisms must not be conflated: locale evidence is not a translation engine,
and matching a phrase does not prove the user's intent.

## Response language

These references do not translate generated responses. The underlying AI tool should
answer in the user's language while preserving the English SoulMap behavioral contract.
Language data supports narrow detection only; it does not add a response-writing layer.

## Adding a locale

Add a locale directory with a stable BCP 47-style language code, use the existing
Markdown front matter and heading schema, write human-authored phrases, add positive and
near-miss tests, update the consuming runtime loader when a new signal domain is added,
and run the full knowledge, safety, packaging, and evaluation gates. Do not add localized
doctrine copies under this directory.
