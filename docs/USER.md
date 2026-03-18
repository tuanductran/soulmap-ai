# User Guide

## What SoulMap AI is

SoulMap AI is a reflective companion designed to help people understand themselves more
clearly. It is built to avoid prediction, diagnosis, and dependency.

## What this repository provides

- A Markdown knowledge base (brand, voice, frameworks, safety posture).
- A local framework selector that chooses an appropriate response mode based on message
  content.

## Using `skills/AGENTS.md`

`skills/AGENTS.md` is a single-file bundle of the SoulMap AI knowledge base. It is
intended to be pasted into an AI tool's "instructions" or "system prompt" field.

The file begins with a Table of contents so you can quickly navigate and audit the
policies and frameworks.

## Quick demo (local)

```bash
python -m modules.soulmap_demo --message "I feel lost and numb lately."
```

If you do not want to run code locally, you can still read the knowledge base directly
in `skills/AGENTS.md`.
