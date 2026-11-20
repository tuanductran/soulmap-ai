# Korean crisis language pack: initial coverage and limitations

Status: initial deterministic phrase coverage; not a clinically validated Korean
risk classifier. A fluent Korean reviewer with suicide-prevention expertise
should review the wording and test cases before this pack is treated as complete.

## Design

The Korean pack follows the existing language-pack contract:

- LANGUAGE_CODE = ko (BCP 47 language subtag).
- CRISIS_TIER1: direct first-person suicidal-ideation and self-harm expressions.
- CRISIS_TIER2: high-distress, hopelessness, entrapment, and abuse expressions.
- GRANDIOSITY_SIGNALS: explicit grandiose identity or mission claims.

The phrases are literal, human-authored Korean. They are not translations of
English substrings, and no runtime machine translation is involved. The pack is
combined with the existing language packs by
soulmap.runtime.knowledge.crisis_language_packs.

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
  https://www.mohw.go.kr/menu.es?mid=a10716040000
- A 2026 Korean-language study analysed 1,984 online counselling posts
  containing the expression 죽고 싶다 and found multiple co-occurring
  psychosocial contexts, supporting context-aware, layered evaluation rather
  than reliance on one phrase:
  https://doi.org/10.4306/jknpa.2026.65.3.234
- Research on cross-lingual suicidal-ideation detection notes the scarcity of
  validated Korean lexicons and the need for expert-created dictionaries:
  https://www.suicideinfo.ca/resource/cross-lingual-suicidal-oriented-word-embedding-toward-suicide-prevention/

## Release gate

Before enabling broader Korean coverage, add native-reviewed positive,
negative, colloquial, spacing, quotation, and mixed-clause examples; verify
Korean negation behavior; and confirm region-specific crisis-resource wording
in a separate safety-reviewed change. Do not modify the legacy
src/soulmap/runtime/config/safety.py stub to store these phrases.
