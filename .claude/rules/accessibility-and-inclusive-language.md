---
paths:
  - docs/**/*.md
  - skills/**/*.md
  - templates/**/*.md
  - src/**/*.py
  - scripts/**/*.sh
---

# Accessibility and inclusive language rules

Use these rules when changing user-facing copy, Markdown knowledge files, Python
surfaces that emit text, or shell scripts that produce human-facing output.

SoulMap is a Markdown-and-Python project, so accessibility here means:

- inclusive, respectful language
- low cognitive load
- clear structure
- readable output

## Rule precedence

If this rule conflicts with a stronger repo-local contract, follow the stronger source:

1. `AGENTS.md`
2. `docs/engineering/content-contract.md`
3. `language-and-grammar.md`
4. this file

## Core standard

Make the result easier to understand, navigate, and use.

Prefer:

- plain language over jargon
- stable structure over clever formatting
- explicit labels over implied meaning
- text that works without color, tone, or shared context

Do not claim that any output is "fully accessible". Accessibility still needs human
review.

## Inclusive language

- Use respectful, inclusive, people-first language in user-facing text.
- Do not make assumptions about ability, cognition, literacy, or technical fluency.
- Do not frame confusion, slowness, forgetfulness, or emotional intensity as moral
  failure.
- Avoid stereotypes about disability, mental health, age, or expertise.
- Keep SoulMap language calm and non-humiliating, especially in safety or refusal
  flows.

## Cognitive load and readability

- Prefer plain language.
- Keep structure consistent and easy to scan.
- Use short paragraphs and stable section ordering.
- Avoid unnecessary visual or rhetorical intensity.
- If a concept can be said directly, do not wrap it in jargon, mystical phrasing, or
  implementation vocabulary.
- When writing helper text, errors, CLI output, or instructions, explain what
  happened and what the reader can do next.

## Markdown and content structure

- Use headings to introduce real sections.
- Do not skip heading levels without reason.
- Keep one clear top-level topic per document.
- Use meaningful link text rather than vague phrases like `click here`.
- Keep lists parallel and easy to scan.
- If images are added to tracked Markdown or HTML, they need meaningful alt text when
  informative, or empty alt text when decorative.

## Python and CLI text

- Error output should be plain, specific, and actionable.
- Do not rely on color alone to communicate success, warning, or failure.
- Machine-readable output should stay machine-readable, but any human-facing companion
  text should remain concise and understandable.
- If a Python surface emits prompts, labels, or status text, use visible wording that
  a non-expert can understand quickly.
- Avoid messages that sound mocking, dramatic, or insider-only.

## SoulMap-specific adaptation

In this repository, accessibility also means the text does not push people away through
tone.

Always keep language:

- grounded
- non-clinical unless precision requires it
- low-shame
- non-performative
- easy to re-read

Avoid:

- guru certainty
- support-bot filler
- corporate euphemisms
- emotionally sticky dependency language
- overly dense explanations when one direct sentence would do

## Verification

After meaningful accessibility-sensitive edits, run the smallest checks that match the
surface:

```bash
uv run soulmap markdown-contract --root .
uv run soulmap lint --skip-tests
```
