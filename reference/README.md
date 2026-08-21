# Repository reference data

This directory contains Markdown reference data used by SoulMap runtime and AI
Skills. It is packaged in the AI-facing `dist/soulmap-ai.zip` and
`dist/soulmap-ai.skill` artifacts alongside `skills/`.

## Languages

The [`languages/`](languages/) directory contains human-authored locale evidence and
optional localized references. It does not define SoulMap doctrine, framework guidance,
voice, safety policy, or generated response content.

The shipped Skills package remains canonical English for doctrine and behavior. The
Markdown locale references are packaged resources, not translated doctrine. Python may
use them for deterministic detection where an explicit consumer and regression coverage
exist. Python does not translate generated responses and no external translation API is
required.
