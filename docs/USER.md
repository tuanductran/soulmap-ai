# User Guide

## What SoulMap AI is

SoulMap AI is a reflective companion designed to help people understand themselves more
clearly. It is built to avoid prediction, diagnosis, and dependency.

## What this repository provides

- A Markdown knowledge base under [../skills/](../skills/) and
  [../templates/](../templates/).
- A local framework selector that chooses an appropriate response mode based on message
  content.

## Using the knowledge base

The knowledge base lives under [../skills/](../skills/) and
[../templates/](../templates/). Most AI tools can ingest multiple files directly, or
you can upload the packaged archive built into `dist/`.

## Quick demo (local)

```bash
python -m modules.soulmap_demo --message "I feel lost and numb lately."
```

If you do not want to run code locally, you can still read the knowledge base directly
under [../skills/](../skills/) and [../templates/](../templates/).
