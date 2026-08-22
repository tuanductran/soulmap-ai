---
name: "soulmate-foundation-text-normalization"
description: "Deterministic lexical normalization for comparable text without translation or semantic inference."
license: "MIT"
---

# Text normalization

## Purpose

This skill defines conservative lexical normalization for text that must be compared, indexed, or passed to another deterministic capability. The operation makes superficial formatting more consistent while preserving the user's words and language.

Normalization is a mechanical preprocessing step. It is not translation, transliteration, stemming, lemmatization, sentiment analysis, intent detection, safety classification, or language identification.

## Use this skill when

Use this skill when a foundation or consumer needs stable handling of case, smart apostrophes, backticks, and repeated whitespace. It is useful before exact phrase comparison, deterministic lookup, or test fixture preparation when those operations explicitly require normalized text.

Use it when the same textual input may arrive with typographic punctuation or inconsistent spacing and the consumer needs a reproducible lexical representation.

## Do not use this skill for

Do not use this skill to decide what a message means, translate content, remove diacritics, replace one language with another, infer a user's emotional state, or classify risk. Do not use normalized output as a substitute for the original text when punctuation, capitalization, spacing, or exact user wording carries meaning.

Do not assume that normalization makes two languages comparable or that a normalized string is safe to display back to a user. Keep the original text available whenever a consumer needs faithful presentation, auditability, or user attribution.

## Default operation

The conservative normalization operation performs these transformations in order:

| Order | Transformation | Purpose |
| --- | --- | --- |
| 1 | Lowercase the text | Make case-only differences comparable |
| 2 | Replace the right single quotation mark with an ASCII apostrophe | Unify a common typographic variant |
| 3 | Replace backticks with an ASCII apostrophe | Keep a small set of quote-like input variants comparable |
| 4 | Collapse runs of whitespace to one space | Remove layout-only spacing differences |
| 5 | Strip leading and trailing whitespace by default | Produce a clean comparison value |

The operation is deterministic. The same input and the same `strip` option produce the same output.

Conceptually:

```text
raw text
    ↓
lowercase
    ↓
quote normalization
    ↓
whitespace collapse
    ↓
optional edge trimming
    ↓
normalized text
```

## Preservation rules

Normalization intentionally preserves Unicode letters, numbers, diacritics, punctuation other than the documented quote variants, word order, and internal meaning. Vietnamese accents, Korean characters, Spanish punctuation, and other language-specific characters are not removed or translated by this operation.

Normalization also preserves empty content as empty content. A consumer that requires non-empty input must validate that requirement explicitly rather than assuming that normalization creates content.

When `strip` is disabled, leading and trailing whitespace are retained after internal whitespace has been collapsed. This option exists for consumers that need to distinguish edge layout from internal spacing; it does not disable lowercase or quote normalization.

## Authoring and integration workflow

When using normalized text in a foundation workflow:

1. Preserve the original input for presentation, logging, or audit needs.
2. Declare why the consumer needs normalization and which comparisons depend on it.
3. Normalize at the boundary immediately before the lexical operation.
4. Use the default edge trimming unless preserving edge whitespace is an explicit requirement.
5. Keep matching or validation rules separate from normalization.
6. Add tests for ordinary text, repeated whitespace, smart apostrophes, backticks, Unicode/diacritics, empty text, and the `strip` option.
7. Never claim semantic equivalence solely because two strings normalize to similar forms.

## Interaction with phrase data

A consumer may normalize both a message and a phrase list before an exact lexical comparison, but that comparison remains a consumer rule. The foundation normalization operation does not decide whether a phrase matches, whether a match is meaningful, or what action follows.

If a consumer uses phrase data extracted from Markdown, it should document whether phrases are authored in normalized form or normalized at comparison time. Mixing policies can create silent drift. A manifest or consumer contract should make the choice visible.

## Locale boundaries

This capability is locale-neutral but not locale-aware. It does not perform locale-specific casing policy, transliteration, accent folding, tokenization, morphology, or script conversion. A consumer that needs one of those transformations must name it separately, define its compatibility behavior, and test it for every supported language.

In particular, removing accents is not a harmless default. It can improve recall for a narrowly reviewed detector while reducing precision or changing meaning. Any such transformation belongs to an explicitly owned consumer capability, not to this conservative foundation operation.

## Common anti-patterns

**Semantic normalization** changes text based on inferred meaning and is outside this skill.

**Silent transliteration** replaces a user's script or language representation and can make audit and display behavior unsafe.

**Destructive punctuation removal** can change boundaries, code, URLs, or quoted language.

**Using normalized output as display text** hides what the user actually supplied.

**Treating normalization as classification** confuses preprocessing with a policy decision.

**Unbounded normalization changes** make existing phrase contracts drift without a versioned consumer decision.

## Review checklist

Before approving a normalization use:

- the original text remains available where fidelity matters;
- the required transformations are listed explicitly;
- no translation, transliteration, stemming, or semantic inference is implied;
- Unicode and diacritic behavior is tested rather than assumed;
- empty input and `strip` behavior are defined;
- matching/classification remains a separate consumer decision;
- the operation is deterministic and offline;
- a change to normalization is treated as a compatibility decision.

## Expected outcome

A completed normalization contract gives consumers a stable lexical preprocessing step while protecting language, meaning, and user-visible text from hidden transformations. Frameworks can add their own matching or policy layer without making the foundation responsible for interpretation.
