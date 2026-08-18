# Grounded discernment research

**Research date:** 2026-08-18. **Purpose:** record an internal synthesis that informed a small, authored refinement to SoulMap AI's discernment tooling. This document intentionally omits source identifiers, URLs, copied prose, raw corpus data, client material, and source-specific provenance.

## Executive conclusion

The useful design signal was not a new spiritual framework. It was a refinement of an existing SoulMap capability: keep symbolic or spiritual interpretations provisional, return them to direct experience and ordinary-life reality, and preserve the user's authority over meaning and decisions.

Most related topics already had canonical coverage in SoulMap, including discernment, guidance, boundaries, direction, creativity, grief, voice, and safety. Creating another framework would duplicate the current architecture. The adopted change therefore remains a narrow update to the existing discernment skill plus regression coverage for authored multilingual safety phrases.

## Design principles retained

| Principle | SoulMap treatment |
| --- | --- |
| Information hygiene | Separate direct experience from the interpretation assigned to it and from the emotional context surrounding it. |
| Symbolic translation | Treat symbols as lenses for reflection, not as objective metaphysical facts or external authority. |
| Reality contact | Return high-stakes interpretation to observable circumstances, relationships, ordinary needs, trusted human support, and professional care when appropriate. |
| User authority | Do not turn spiritual language, intuition, guides, patterns, or identity claims into commands, predictions, diagnoses, or dependency. |
| Bypass detection | Notice when spiritual language is being used to dismiss pain, skip accountability, inflate specialness, or force premature acceptance. |

## Implemented SoulMap changes

`skills/spiritual/spiritual-discernment.md` contains the canonical authored refinement. It distinguishes four layers: direct experience, assigned interpretation, emotional context, and reality contact. It permits a user's spiritual frame to be explored without teaching a metaphysical system or confirming an unverifiable claim.

The refinement also translates symbolic language back into grounded reflection. A guide can become a question about inner authority; a body-energy symbol can become a question about where a sensation is noticed; and karma can become a question about patterns and responsibility. These are reflective lenses, not claims about the structure of reality.

High-stakes, irreversible, crisis-adjacent, or harm-related decisions must not rely on spiritual interpretation as the sole authority. The response must return to observed reality and appropriate human or professional support.

The Vietnamese phrase packs in `tests/regression/test_soulmap_vietnamese_bypass_phrases.py` are authored for SoulMap and cover dismissing pain, premature acceptance, spiritual inflation, bypassing accountability, and genuine integration signals. The detector remains a secondary signal rather than a primary framework.

## Explicit exclusions

The repository must not import copied or translated source prose, client anecdotes, identifying information, commercial material, rituals, channeling transcripts, regression or past-life techniques, healing promises, predictions, diagnoses, afterlife claims, spirit-entity claims, cosmologies, or numerical consciousness systems.

Prescriptive recommendations must not be converted into conversational action plans. Consumer literacy and source hygiene remain boundary and reflection concepts, not certifications, rituals, scores, or authority systems.

## Provenance boundary

This report is an internal design record, not a source transcript or attribution record. No raw article text, image, translation, crawl corpus, external URL, author name, or source-specific claim is retained in the current repository tree. The implementation is reviewed as original SoulMap-authored behavior against `AGENTS.md`, the existing skill architecture, and the repository's safety contracts.
