# Korean crisis language pack: initial coverage and limitations

Status: draft-only phrase inventory; it is deliberately excluded from the active
crisis detector aggregates. It is not a clinically validated Korean risk
classifier. A fluent Korean reviewer with suicide-prevention expertise must
review the wording and test cases before activation.

## Activation boundary

The Korean inventory is kept in `DRAFT_LANGUAGE_PACKS` and is not included in
`SUPPORTED_LANGUAGES` or the active Tier 1, Tier 2, and grandiosity aggregates.
This prevents unreviewed Korean substring matches from changing production
routing. Do not activate it until the review gate below is satisfied.

The current automated review identified three concrete gaps that require
native-language review: a self-harm disclosure without an object particle can
be missed; a denial such as `죽고 싶다는 생각은 안 해요` can contain a positive
substring; and the everyday fatigue phrase `너무 지쳤어` can trigger Tier 2.
These are documented as limitations, not treated as solved by this draft.

## Design

The Korean pack follows the existing language-pack contract:

- LANGUAGE_CODE = ko (BCP 47 language subtag).
- CRISIS_TIER1: direct first-person suicidal-ideation and self-harm expressions.
- CRISIS_TIER2: high-distress, hopelessness, entrapment, and abuse expressions.
- GRANDIOSITY_SIGNALS: explicit grandiose identity or mission claims.

The phrases are literal, human-authored Korean. They are not translations of
English substrings, and no runtime machine translation is involved. The pack is
combined with the existing language packs by
SoulMap runtime knowledge language-pack aggregator.

## Detection limitations

The current detector uses substring matching for phrase tuples. Korean is
agglutinative and allows variation in particles, spacing, honorific endings,
tense, colloquial spelling, and omitted subjects. A short phrase list cannot
cover all such forms. This initial pack intentionally avoids very broad stems
such as 죽고 싶 or standalone nouns such as 자살, which would create
obvious false-positive risks in denials, educational discussion, and quoted
content.

The existing detector has explicit first-person denial masking for English,
Vietnamese, Spanish, French, and Chinese, but not Korean. The initial Korean
phrases are chosen so tested forms such as 죽고 싶지 않아요 and
자살하고 싶지 않아요 do not contain the positive literal phrases. This is
a narrow near-miss check, not general Korean negation understanding. Korean
morphology, spacing, slang, quotations, and mixed statements still need a
larger reviewed regression corpus.

A detected phrase is a signal for a supportive response, not a diagnosis or a
prediction. A missed phrase must not be interpreted as evidence that a person
is safe. The detector's response guidance and resource selection are unchanged
by this pack; region-specific resources must continue to be verified against
the user's actual location.

## Research references

- Korea's Ministry of Health and Welfare describes its suicide-prevention
  response system and the 24-hour suicide-prevention counselling line 109:
  [Ministry of Health and Welfare](https://www.mohw.go.kr/menu.es?mid=a10716040000)
- A 2026 Korean-language study analysed 1,984 online counselling posts
  containing the expression 죽고 싶다 and found multiple co-occurring
  psychosocial contexts, supporting context-aware, layered evaluation rather
  than reliance on one phrase:
  [Korean-language study](https://doi.org/10.4306/jknpa.2026.65.3.234)
- Research on cross-lingual suicidal-ideation detection notes the scarcity of
  validated Korean lexicons and the need for expert-created dictionaries:
  [Cross-lingual suicide-prevention research](https://www.suicideinfo.ca/resource/cross-lingual-suicidal-oriented-word-embedding-toward-suicide-prevention/)

## Release gate

Before enabling broader Korean coverage, add native-reviewed positive,
negative, colloquial, spacing, quotation, and mixed-clause examples; verify
Korean negation behavior; and confirm region-specific crisis-resource wording
in a separate safety-reviewed change. Do not modify the legacy safety configuration stub to store these phrases.
