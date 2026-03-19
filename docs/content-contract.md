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
name: "Human-Readable Document Title"
description: "One short sentence describing the full file."
id: <stable-id>
kind: skills|templates
version: 1
---
```

Rules:

- `name` should match the file's top-level `#` heading.
- `description` must be short and describe the whole document, not just the first
  section.
- `id` should be stable. Prefer `skills-<area>-<file-stem>` or `templates-<file-stem>`.
- Keep a blank line between the closing `---` and the first `#` heading.

The repository enforces this via `python -m modules.markdown_contract`.

## Formatter safety (avoid YAML breakage)

Some Markdown formatters can rewrite or relocate YAML front matter.

To avoid structural damage:

- Use `python -m tools.format` / `python -m tools.lint` or `bash scripts/format.sh` /
  `bash scripts/lint.sh`.
- Do not run auto-formatters over `skills/` and `templates/` unless they are known to
  preserve YAML front matter exactly.
