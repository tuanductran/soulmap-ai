---
name: knowledge-base-maintainer
description: Add, update, and normalize Markdown knowledge files in this repository so they stay structurally correct, discoverable, and aligned with SoulMap AI conventions.
---

# Knowledge Base Maintainer

Use this skill when creating or editing Markdown knowledge files under:

- `skills/`
- `templates/`
- `docs/`

## Mission

Keep the content layer of the repo healthy.

That means:

- correct front matter
- consistent naming
- clean internal links
- accurate cross-references
- content that matches the actual repo structure

## Sources Of Truth

Always check:

- `docs/DEV.md`
- `docs/content-contract.md`
- `README.md`
- relevant files in `skills/` and `templates/`

## What To Maintain

### Structural Correctness

Ensure that Markdown files:

- use kebab-case filenames where expected
- keep valid YAML front matter
- use the correct `name` value for the filename stem
- preserve heading structure and link targets

### Content Accuracy

Ensure that docs and knowledge files:

- do not reference deleted files
- do not omit important new modules or guides
- do not describe behavior the repo does not implement

### Cross-File Consistency

Check for drift between:

- docs and tests
- README and internal guides
- templates and brand doctrine
- safety docs and implementation modules

## Workflow

1. Read the target file.
2. Identify nearby source-of-truth files.
3. Update the content with the smallest correct change.
4. Preserve existing tone and structure unless the file is clearly inconsistent.
5. Prefer repo-wide consistency over local phrasing preference.

## Expected Output

When using this skill for review, respond with:

### Findings

List broken links, structural issues, stale references, or consistency gaps.

### Proposed Update

Provide the corrected content or summarize the change.

### Notes

Mention any repo-wide impacts such as docs that should also be kept in sync.

## Writing Rules

- Do not invent metadata fields the repo no longer uses.
- Keep edits ASCII unless the file already uses non-ASCII intentionally.
- Prefer concise descriptions in front matter.
- Do not over-refactor content that is already correct.

## Definition Of Done

The updated knowledge file should be:

- structurally valid
- linked correctly
- aligned with repo conventions
- consistent with adjacent docs and templates
