---
paths:
  - AGENTS.md
  - SKILL.md
  - README.md
  - docs/**/*.md
  - skills/**/*.md
  - templates/**/*.md
  - .agents/**/*.md
---

# SoulMap language and grammar rules

Use these rules when writing or editing Markdown or prose-heavy local workflow files.

This rule is adapted from Atlassian Design's "Style, grammar, and punctuation"
guidance and rewritten for SoulMap's doctrine, tone, and repo portability needs.

Reference:

- <https://atlassian.design/foundations/content/language-and-grammar/>

## Rule precedence

If this rule conflicts with a stronger repo-local contract, follow the stronger source:

1. `AGENTS.md`
2. `docs/engineering/content-contract.md`
3. `markdown-portability.md`
4. `source-character-safety.md`
5. this file

Important local override:

- Atlassian recommends curly apostrophes for readability.
- SoulMap repo portability and source-safety rules override that.
- In this repository, use straight ASCII quotes and apostrophes in Markdown and
  local workflow files unless a file truly requires Unicode.

## Core standard

Write so the text is:

- clear before clever
- calm before dramatic
- specific before expansive
- easy to scan
- easy to localize
- consistent with SoulMap as "mirror, not guide"

## Sentence and heading style

- Use sentence case for headings, titles, labels, and section names.
- Do not add periods to headings.
- Prefer statement headings over question headings.
- In procedural docs, prefer action-led headings.
- Avoid gerund-heavy headings when a direct verb is clearer.
- Prefer descriptive headings over numbered internal labels such as `Section 12, shift markers`.
- Use numbering in headings only when the number itself is meaningful to the reader,
  not just to the writer's outline.

Preferred:

- `Build the skill archive`
- `Returning user onboarding`
- `Shift markers`

Avoid:

- `Building The Skill Archive`
- `What should you upload?`
- `Section 12, shift markers`

## Word choice

- Use full words instead of abbreviations in user-facing or cross-functional docs.
- Do not use `e.g.`, `i.e.`, `etc.`, or `&` in prose.
- Rewrite with `for example`, `that is`, `and so on`, or plain `and`.
- Expand feature, product, or framework names unless the shortened form is the
  established literal name.

Preferred:

- `For example, upload AGENTS.md and SKILL.md.`

Avoid:

- `Upload AGENTS.md, SKILL.md, etc.`

## Grammar

- Prefer active voice.
- Prefer present tense for rules, product behavior, instructions, and system facts.
- Use past tense only for completed events or results.
- Keep subjects explicit when passive voice hides responsibility.

Preferred:

- `The safety gate blocks prediction language.`
- `Run the eval suite after detector changes.`

Avoid:

- `Prediction language is blocked by the safety gate.`
- `The eval suite should be run after detector changes.`

## Pronouns and point of view

- Minimize pronouns when they make a sentence vague.
- Use `you` and `your` when speaking directly to the user or reader improves clarity.
- Use `we` only for genuine repo, team, or product statements.
- Do not use `we` to anthropomorphize SoulMap.
- Do not use `I` in product copy unless the surface is intentionally first-person.

Preferred:

- `Use this file when reviewing onboarding copy.`
- `SoulMap answers honestly when asked whether it is an AI.`

Avoid:

- `We are always here to help you explore yourself.`
- `I know what you need next.`

## Contractions

- Use contractions when they make user-facing copy sound natural and calm.
- Do not force contractions into doctrine, checklists, or technical docs when the
  expanded form is clearer.
- Keep contractions simple and standard.

Preferred:

- `You don't need certainty to notice what is true.`

Acceptable in technical docs:

- `Do not run packaging commands from the extracted archive.`

## Lists

- Use lists to improve scanability, not to inflate structure.
- Keep lists to 6 items or fewer when possible. Split long lists when needed.
- Keep list items parallel in grammar and shape.
- Use a lead-in sentence before the list when it improves context.
- For fragment lists, use lowercase starts unless a proper noun requires caps.
- Do not add end punctuation to fragment list items.
- For full-sentence list items, keep punctuation consistent across the list.

Preferred:

- `Run these checks after detector changes:`
- `- format the repo`
- `- run lint`
- `- run the targeted tests`

Avoid:

- `You should do the following things.`
- `- Run lint.`
- `- testing.`
- `- Then you should build the skill archive.`

## Punctuation and formatting

- Use straight ASCII apostrophes and quotes.
- Avoid exclamation marks unless they are inside a literal user quote or example.
- Avoid semicolons in SoulMap-facing copy and examples. Split the sentence instead.
- Do not use spaced hyphen punctuation such as `word, word` or `word -- word` as a sentence joiner.
- Rewrite those joins with commas, or split them into separate sentences.
- Use colons to introduce lists, examples, and lead-ins when needed.
- Use bold sparingly for scan anchors, warnings, and short labels.
- Do not use italics for links.
- Do not stack emphasis styles unless the file already has an established pattern.

## Articles

- Omit articles in terse labels or short action headings when clarity improves.
- Keep articles in natural-language sentences when they make the sentence easier to read.
- Do not strip articles so aggressively that the copy sounds robotic.

Preferred:

- `Create password`
- `The user needs a clear explanation of the mechanism.`

## Numbers

- Use numerals for steps, limits, counts, priorities, and structured references.
- Spell out a number only when it starts a sentence or reads more naturally in prose.
- Keep number formatting consistent inside the same section.

Preferred:

- `Run 3 checks.`
- `Stage 2 allows gentle framework use.`

## SoulMap-specific adaptation

Atlassian's guidance helps with clarity and consistency. SoulMap adds stronger tone
constraints on top of that.

Always keep language:

- grounded
- non-clinical
- non-performative
- non-corporate
- non-mystifying
- non-dependent

Do not let "clear and friendly" drift into:

- startup jargon
- support-bot phrasing
- therapist-speak
- guru language
- inflated spiritual certainty

Avoid phrases like:

- `we're here for you anytime`
- `let's unpack this together`
- `your nervous system`
- `action steps`
- `aligned with your goals`
- `this proves`
- `you are meant to`

Prefer language that returns ownership:

- `something in this feels alive`
- `what feels true to you`
- `the insight is yours`
- `SoulMap reflects, it does not decide`

## Editing check

Before finishing a prose edit, check:

- Is the heading in sentence case?
- Is the sentence active and present where possible?
- Did I avoid `e.g.`, `i.e.`, `etc.`, and `&`?
- Did I keep smart punctuation out of the file?
- Is the list short, parallel, and easy to scan?
- Does the wording stay faithful to SoulMap doctrine?
