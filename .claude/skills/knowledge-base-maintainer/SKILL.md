---
name: knowledge-base-maintainer
description: Add, update, and normalize Markdown knowledge files in this repository so they stay structurally correct, discoverable, and aligned with SoulMap AI conventions.
---

# Knowledge base maintainer

Use this skill when creating or editing Markdown knowledge files under:

- `skills/`
- `templates/`
- `docs/`

## Do not use this skill for

- Writing or updating technical docs such as `docs/engineering/API.md` and `docs/engineering/DEV.md`, use
  [`docs-and-api-writer`](../docs-and-api-writer/SKILL.md) for those
- Reviewing public-facing brand copy, use
  [`brand-copy-review`](../brand-copy-review/SKILL.md)
- Reviewing prompt engineering or response safety, use
  [`ai-prompt-engineering-safety-review`](../ai-prompt-engineering-safety-review/SKILL.md)

## Mission

Keep the content layer of the repo healthy.

That means:

- correct front matter
- consistent naming
- clean internal links
- valid local anchors
- canonical SoulMap-specific term casing
- accurate cross-references
- content that matches the actual repo structure

## Sources of truth

Always check:

- `docs/engineering/DEV.md`
- `docs/engineering/content-contract.md`
- `README.md`
- relevant files in `skills/` (shipped) and, for internal-only copy, `templates/`

## What to maintain

### Structural correctness

Ensure that Markdown files:

- use kebab-case filenames where expected
- keep valid YAML front matter
- use the correct `name` value for the filename stem
- preserve heading structure and link targets
- keep local Markdown links and anchors resolvable
- keep canonical product and tool names cased correctly where the repo enforces them

### Content accuracy

Ensure that docs and knowledge files:

- do not reference deleted files
- do not omit important new modules or guides
- do not describe behavior the repo does not implement
- do not leak source-specific names, local paths, or temporary working markers into
  tracked Markdown

### Cross-file consistency

Check for drift between:

- docs and tests
- README and internal guides
- templates and brand doctrine
- safety docs and implementation modules

## Workflow

1. Read the target file.
2. Identify nearby source-of-truth files.
3. Update the content with the smallest correct change.
4. Run the Markdown contract and local Markdown QA checks for touched files when relevant.
5. If the edit changes public URLs, run the opt-in external link check as well.
6. Preserve existing tone and structure unless the file is clearly inconsistent.
7. Prefer repo-wide consistency over local phrasing preference.

## Expected output

When using this skill for review, respond with:

### Findings

List broken links, structural issues, stale references, or consistency gaps.

### Proposed update

Provide the corrected content or summarize the change.

### Notes

Mention any repo-wide impacts such as docs that should also be kept in sync.

### Verification

Mention which Markdown QA commands were run and whether any existing repo issues remain.
If public URLs changed, mention whether the opt-in external link check was run and
whether any warnings came from anti-bot or rate-limit responses.

## Writing rules

- Do not invent metadata fields the repo no longer uses.
- Keep edits ASCII unless the file already uses non-ASCII intentionally.
- Prefer concise descriptions in front matter.
- Do not over-refactor content that is already correct.
- Do not use Python constant names, module paths, or code identifiers in prose.
  Write what a concept means, not what it is called in the implementation.
  Wrong: `ACUTE_GRIEF` (phrase list in `src/soulmap/runtime/config/safety.py`)
  Right: Acute grief, loss just happened or recently named

## Definition of done

The updated knowledge file should be:

- structurally valid
- linked correctly
- aligned with repo conventions
- consistent with adjacent docs and templates
