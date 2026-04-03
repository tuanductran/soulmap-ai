# Content Contract (Markdown)

This repository is content-first. Many automated tools (including AI tooling) can
accidentally damage structure if they rewrite files without respecting the repo's
conventions. This document defines the non-negotiable constraints that keep the
knowledge base stable.

## File naming

- Use kebab-case for Markdown filenames.
- Do not use underscores (`_`) in Markdown filenames.

Examples:

- ✅ `numerology-profile.md`
- ❌ `numerology_profile.md`

## Required metadata (YAML front matter)

All Markdown files under `skills/` and `templates/` must begin with YAML front matter:

```yaml
---
name: "file-stem"
description: "One short sentence describing the full file."
---
```

Rules:

- `name` should match the filename stem in kebab-case.
- `description` must be short and describe the whole document, not just the first
  section.
- Keep a blank line between the closing `---` and the first `#` heading.

The repository enforces this via `uv run soulmap markdown-contract`.

## Source hygiene

Tracked Markdown must not contain:

- absolute local filesystem paths
- source-specific bundle names
- temporary working paths
- metadata markers copied from import or extraction output

If source material is sensitive or source-specific, rewrite it into abstractions and
reusable patterns before it enters `skills/`, `templates/`, or `docs/`.

The repository enforces this via `uv run soulmap markdown-contract`.

## Ordered lists

This repo uses sequential ordered-list numbering:

```md
1. first
2. second
3. third
```

Do not normalize ordered lists to repeated `1.` markers. Repo checks and release tooling
expect sequential numbering.

## Formatter safety (avoid YAML breakage)

Some Markdown formatters can rewrite or relocate YAML front matter.

To avoid structural damage:

- Use `uv run soulmap format` / `uv run soulmap lint` or `bash scripts/format.sh` /
  `bash scripts/lint.sh`.
- Do not run auto-formatters over `skills/` and `templates/` unless they are known to
  preserve YAML front matter exactly.
