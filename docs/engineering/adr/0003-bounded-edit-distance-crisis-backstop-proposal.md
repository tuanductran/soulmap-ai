# ADR 0003: Bounded Edit-Distance Backstop for Crisis Phrase Matching (Proposal)

## Status

Proposed. This ADR authorizes nothing. Per
[`docs/engineering/adr/README.md`](README.md), an ADR is documentation-only,
and this one specifically records a proposal for maintainer review, not an
already-implemented or already-agreed decision. No code, test, or CI change
should reference this ADR as authorization until its status changes to
Accepted through the normal contribution process.

## Context

`detect_crisis()` (`src/soulmap/runtime/detectors/crisis_detector.py`) scans
a message for crisis signals using literal substring matching against
curated phrase packs (`src/soulmap/runtime/config/safety_<lang>.py`) plus a
small set of regex patterns for the highest-severity Tier 1 phrasings. This
is deterministic by design: [ADR 0002](0002-deterministic-response-safety-enforcement.md)
requires all response-safety enforcement, crisis detection included per its
"all other response-safety enforcement" scope, to stay free of semantic or
model-based classification.

External research on keyword-only crisis detection (gathered during a
2026-08 repo audit; not repo-verified beyond citation) describes a
consistent failure mode: literal phrase matching misses paraphrase,
misspelling, and spacing variants that a person in real distress plausibly
types, and the gap between benchmark pass rates and real-session miss rates
can be large. Sources reviewed:

- <https://www.medrxiv.org/content/10.64898/2026.01.12.26343914v1.full>
- <https://arxiv.org/pdf/2510.12083>
- <https://journals.plos.org/digitalhealth/article?id=10.1371%2Fjournal.pdig.0001383>
- <https://fpf.org/blog/mandating-evidence-based-suicide-detection-in-chatbots/>

This is a real gap worth addressing. The question this ADR exists to answer
is whether a bounded edit-distance ("fuzzy") layer is an acceptable way to
close part of it, given that ADR 0002's own "Alternatives Considered"
section already rejected "broad heuristic scoring without a model" for the
response-safety validator, specifically because "opaque scores and
thresholds would be harder to audit than explicit patterns." A naive fuzzy
layer is architecturally the same shape as that rejected alternative, so
this proposal cannot simply be added as an incremental hardening change
under ADR 0002's existing "narrowly scoped regex or substring pattern"
allowance. It needs its own decision record.

## Decision (proposed)

Add a bounded edit-distance backstop to the Tier 1 crisis check only, with
these constraints, chosen specifically to stay auditable rather than
becoming an opaque score:

1. **Per-phrase, not per-message.** The backstop does not compute one
   confidence score for a message. It asks a single yes/no question per
   existing literal Tier 1 phrase: "does the message contain a token
   sequence within edit distance <= 1 of this exact phrase?" Every match
   result is attributable to one specific phrase from the existing curated
   pack, the same attribution `signals_found` already returns today.
2. **Fixed, small distance budget.** Distance 1 (a single insertion,
   deletion, substitution, or transposition) only. No sliding scale, no
   distance-proportional-to-length scoring. This is a constant, not a
   tunable heuristic weight.
3. **Length floor.** Only phrases (or, if implemented at word level, only
   words) at or above roughly 5-6 characters are eligible. Below that
   floor, distance-1 matching produces too many unrelated real words (for
   example, distance 1 from "die" reaches "dye," "dies," "did," and "tie")
   to stay narrow enough to audit by inspection.
4. **Opt-in per phrase, not blanket.** Not every Tier 1 phrase should
   necessarily get fuzzy coverage automatically merely by existing. The
   pack maintainer marks which literal phrases are fuzzy-eligible, the same
   curation posture ADR 0002 already requires for the literal patterns
   themselves. This keeps the backstop's surface area reviewable phrase by
   phrase rather than applying uniformly and invisibly.
5. **No confidence output.** The detector's return contract does not
   change. A fuzzy match still resolves to the same `CRISIS_TIER1` level,
   `signals_found` label, and `response_guidance` block as a literal match.
   There is no new "maybe crisis" tier and no numeric score surfaced to
   callers.

This differs from the rejected "broad heuristic scoring" alternative in
kind, not just degree: that alternative concerned a multi-category
probability-like score across six response-safety categories for
`response_safety_contract.py`, where "opaque" meant a reviewer could not
easily reconstruct why a given score crossed a threshold. A bounded
edit-distance check against one named literal phrase is fully
reconstructable by a reviewer: given a matched message and a signal label,
the exact character-level edit that produced the match can be printed
alongside it.

## Rationale

Layering a narrow, literal-phrase-anchored fuzzy check on top of the
existing literal match preserves the properties ADR 0002 protects
(reproducibility, no external dependency, inspectable pattern set) while
closing a documented, specific gap (misspelling and minor phrasing drift)
that literal-only matching cannot close by definition. It does not attempt
to close the harder gap (indirect or metaphorical crisis language, which
genuinely requires semantic understanding) - that gap stays explicitly out
of scope and is not what this proposal claims to solve.

Keeping the match attributable to one curated phrase, rather than scoring
the whole message, is what keeps this proposal inside the deterministic,
auditable posture ADR 0002 requires, rather than reopening the
"heuristic scoring" alternative it already rejected.

## Alternatives Considered

**Broad message-level heuristic or probability scoring.**
Rejected, for the same reason ADR 0002 already rejected it: opaque,
threshold-tuned scores are harder to audit than explicit per-phrase
patterns, and this proposal exists specifically to stay on the auditable
side of that line.

**LLM or embedding-based semantic backstop.**
Rejected for this proposal's scope. This is the alternative ADR 0002's
"Future Maintenance Guidance" already anticipates and explicitly requires
its own superseding ADR for, with an explicit accounting of safety benefit,
deterministic fallback, privacy handling, reproducibility limits, operating
cost, failure reporting, and rollback behavior. Nothing in this proposal
should be read as clearing that bar; a semantic backstop remains a
separate, larger decision.

**Curated misspelling variants as additional literal patterns (no fuzzy
matching at all).**
Not rejected - this is a complementary, lower-risk, immediately available
option that needs no new ADR, since it is exactly the "narrowly scoped
regex or substring pattern... for a documented violation phrasing"
maintenance path ADR 0002 already allows. It should proceed independently
of whether this proposal is accepted, as specific real-world misspellings
are identified and reviewed. It does not, on its own, generalize to
variants a maintainer has not yet thought to add, which is the specific
gap this proposal targets.

**Do nothing beyond the existing known-limitations note.**
Not rejected outright - remains the default until this ADR is accepted.
Leaves the documented gap open but adds no new failure surface.

## Consequences (if accepted)

**Positive:**

- Closes a documented, cited gap (misspelling/minor-variant misses) in the
  highest-priority safety check in the pipeline, without introducing a
  model dependency or message-level opaque scoring.
- Every match stays attributable to one curated phrase and one small,
  fixed edit-distance budget, preserving ADR 0002's auditability
  requirement.

**Negative / open risks a real implementation must resolve before this ADR
can move to Accepted:**

- **False-positive risk is not zero.** Distance-1 matching against common
  words, even above the length floor, can still produce unintended matches
  (for example, a distance-1 neighbor of a legitimate long phrase that
  happens to be an unrelated real phrase). A real implementation needs a
  reviewed exclusion list and a much larger regression corpus of
  known-safe near-miss messages across all five supported languages before
  this can ship, not just the existing Tier 1 positive-case tests.
- **Multilingual scope multiplies the review burden.** Edit-distance
  behavior does not transfer cleanly across languages with different
  script and tokenization properties (compare English/Vietnamese/Spanish/
  French word-based text to Chinese, which this repo also supports).
  Chinese in particular needs a distinct, separately reviewed approach
  rather than reusing the same character-edit-distance budget, or explicit
  exclusion from this backstop with the gap documented instead.
- **This still does not close the "indirect/metaphorical language" gap**
  the cited research also names. That gap needs different tooling (if any
  deterministic tooling can address it at all) and is explicitly out of
  scope here.
- **Maintenance cost.** Marking phrases fuzzy-eligible, maintaining the
  exclusion list, and keeping the regression corpus current is ongoing
  curation work, not a one-time change.

This ADR does not change `detect_crisis()`, any config pack, any test, or
any CI gate on its own. Moving to Accepted requires a follow-up
implementation proposal (PR) that resolves the open risks above with
concrete code, a full multilingual regression corpus (positive matches,
known-safe near misses, and exclusion-list coverage), and sign-off through
the repo's normal review process.

## References

- [AGENTS.md](../../../AGENTS.md#non-negotiable-safety-rules)
- [ADR 0001](0001-layered-crisis-detection.md)
- [ADR 0002](0002-deterministic-response-safety-enforcement.md)
- [Known architecture limitations](../known-limitations.md#safety-enforcement-boundaries)
- [Safety enforcement matrix](../safety-enforcement-matrix.md)
