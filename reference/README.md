# Repository reference data

This directory contains local source data used by runtime and maintenance tooling. It is
not part of the AI-facing `dist/soulmap-ai.zip` or `dist/soulmap-ai.skill` artifacts.

## Languages

The [`languages/`](languages/) directory contains human-authored locale evidence and
optional localized references. It does not define SoulMap doctrine, framework guidance,
voice, safety policy, or generated response content.

The shipped Skills package remains canonical English. Python may use the locale evidence
for deterministic detection where an explicit consumer and regression coverage exist.
Python does not translate generated responses and no external translation API is
required.
