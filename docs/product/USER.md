# User Guide

## What SoulMap is

SoulMap is a reflective companion designed to help people understand themselves more
clearly. It is built to avoid prediction, diagnosis, and dependency. It offers reflective
knowledge and structured guidance; it is not a therapist, clinician, or substitute for
professional care.

## What this repository provides

- A Markdown knowledge base under [`skills/`](../../skills/), with
  [`SOULMAP.md`](../../SOULMAP.md) as the baseline doctrine and
  [`SKILL.md`](../../SKILL.md) as the skill entrypoint.
- Local Python tooling for deterministic selection, normalization, validation,
  safety enforcement, and packaging.
- Distribution artifacts for compatible AI platforms; platform-specific support and
  upload requirements vary.

This repository is not a hosted chat application, network API, account service, or
conversation-history database. The host AI platform generates the response and controls
its own conversation processing and retention. SoulMap does not independently store or
retrieve prior sessions. If the host explicitly supplies relevant prior-session context
with a request, the knowledge may use that context; otherwise it must not infer a
conversation history.

## Using the knowledge base

The canonical knowledge base lives under [`skills/`](../../skills/). Build the
distribution artifacts locally with:

```bash
uv run soulmap build
```

Use the [platform integration guide](../integrations/README.md) to choose the appropriate
deployment path. Do not assume every platform accepts the same archive or file format:
some require individual Markdown files, a transformed Skill folder, or a platform-specific
instruction field. Check the current platform lifecycle, file limits, and upload workflow
before deploying.

If you do not want to run code locally, you can still read the knowledge base directly
under [`skills/`](../../skills/), together with the baseline
[`SOULMAP.md`](../../SOULMAP.md).
