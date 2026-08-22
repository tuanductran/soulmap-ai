---
name: "soulmate-foundation-knowledge-resolution"
description: "Deterministic resolution of explicitly selected Markdown sections and labeled phrase groups."
license: "MIT"
---

# Knowledge resolution

## Purpose

This skill defines a small, deterministic way to resolve structured knowledge from explicitly selected Markdown text. It covers section boundaries, quoted phrases, labeled groups, duplicate handling, and absent-section behavior.

Knowledge resolution is a parsing capability, not a decision engine. It extracts declared data from a known document. It does not decide which document to use, infer a user's intent, activate a framework, rank a route, or interpret the meaning of the extracted phrases.

## Use this skill when

Use this skill when a consumer owns Markdown resources whose sections contain structured phrase data. It is suitable for keyword lists, labeled phrase groups, lightweight metadata, and other human-readable resources where Markdown remains the source format.

Use it when the consumer needs a stable result from the same text and heading request across runs and operating systems. The input text or resource must be selected explicitly before parsing begins.

## Do not use this skill for

Do not use this skill as a full Markdown renderer, semantic document model, natural-language parser, search index, or routing system. Do not infer headings from approximate matches, scan unrelated sections for phrases, or treat extracted phrases as a complete safety or domain policy.

Do not move product-specific response templates, brand instructions, safety doctrine, or framework activation rules into this parser. The parser can carry neutral data; the consumer decides how that data is used.

## Supported resolution forms

The foundation parser supports two deliberately narrow forms:

| Form | Input shape | Result |
| --- | --- | --- |
| Keyword section | An exact heading followed by bullet lines containing quoted phrases | An ordered tuple of lowercased, de-duplicated phrases |
| Labeled groups | An exact heading followed by labels ending in `:` and quoted bullet phrases | A mapping from normalized label to an ordered tuple of phrases |

The parser searches for the first exact heading match. Heading matching is based on the heading text after the Markdown marker and surrounding whitespace are removed. It does not perform fuzzy matching or case-insensitive heading selection unless a consumer normalizes the requested heading before calling it.

## Section boundary rules

A section begins immediately after its requested heading. Parsing stops at the next heading whose level is less than or equal to the requested heading's level. Deeper headings remain inside the selected section.

For example:

```markdown
## Signals
- "one phrase"

### Detail
- "another phrase"

## Next section
- "not included"
```

A request for `Signals` returns the phrases under `Signals` and its `Detail` subsection, but stops before `Next section`.

The heading level is determined from one to six leading `#` characters followed by whitespace. Lines that are not headings do not change the current section boundary.

## Keyword sections

A keyword section collects quoted phrases from bullet items. A bullet may wrap across multiple lines; the parser joins the continuation lines before extracting quoted text. Phrases are lowercased in the returned result and duplicate values are removed while preserving first-seen order.

An absent heading returns an empty tuple. A present heading with no quoted bullet phrases also returns an empty tuple. The consumer must distinguish those cases if that distinction matters to its own schema; the neutral parser does not invent an error for an empty extraction.

Example:

```markdown
## Detection signals
- "first phrase"
- "Second phrase" with a note
- "first phrase" repeated
```

The neutral result is conceptually:

```text
("first phrase", "second phrase")
```

Unquoted prose is not returned as a phrase. A quoted phrase is data only; the parser does not classify it as safe, unsafe, important, or active.

## Labeled groups

A labeled group section uses a non-empty line ending in `:` as a label. Quoted phrases in subsequent bullet lines belong to the most recent label. The normalized group key is the label text before the first comma, lowercased and trimmed.

Example:

```markdown
## Categories

Primary, high confidence:
- "first phrase"

Secondary:
- "second phrase"
```

The neutral result is conceptually:

```text
{
  "primary": ("first phrase",),
  "secondary": ("second phrase",),
}
```

A bullet appearing before any label does not belong to a group. A label without phrases creates an empty group. Duplicate phrases within a group are removed while preserving first-seen order.

## Authoring workflow

When authoring a Markdown resource for this parser:

1. Choose an exact heading that names the data section.
2. Put structured phrases in simple bullet items.
3. Quote only the text intended to become data.
4. Use labels ending in `:` when grouping is necessary.
5. Keep unrelated prose outside the extraction section or in a deeper explanatory subsection.
6. Add a focused parser test for section boundaries, wrapped bullets, duplicates, absent headings, and empty groups.
7. Let the consumer validate domain-specific meaning after extraction.

## Determinism rules

The result depends only on the supplied Markdown text and requested heading. It must not depend on the current working directory, locale, network, file order, timestamps, random state, or an application-wide registry.

Extraction preserves first-seen order. De-duplication is stable rather than sorted so that an author can control the order in which a consumer receives values. Lowercasing is lexical normalization, not translation or transliteration.

The parser reads text; it does not write back to the source document. If a consumer needs schema validation, provenance, or version checks, those checks belong around the parser and must be explicit.

## Limits and failure handling

The parser is intentionally not a complete Markdown implementation. It does not support arbitrary table schemas, HTML interpretation, nested quote semantics, front-matter evaluation, or semantic section inference.

Malformed or unexpected content may produce an empty or partial neutral extraction according to the documented rules. A consumer that requires a non-empty or schema-complete result must validate that requirement after parsing and report it as its own contract failure.

A parser result must not be treated as proof that a resource is authoritative. Authority, ownership, compatibility, and artifact inclusion belong to the resource manifest and consumer contract.

## Review checklist

Before approving a knowledge resource, confirm that:

- the resource is selected explicitly;
- the requested heading is exact and stable;
- section boundaries are unambiguous;
- quoted phrases are intentional data;
- labels are stable and meaningful;
- duplicate behavior is understood;
- missing or empty sections have an explicit consumer policy;
- no routing, safety, brand, or provider decision is hidden in the parser;
- parser behavior is covered by deterministic tests.

## Expected outcome

A completed knowledge-resolution contract lets a foundation consumer load structured Markdown without coupling the parser to any product's directory layout or worldview. The consumer receives predictable data and remains responsible for ownership, interpretation, validation, activation, and presentation.
