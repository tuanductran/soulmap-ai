"""Validate generated response text against SoulMap safety contracts.

This is the response contract validation layer requested in Issue #132. It is
a lightweight, deterministic, regex/substring-based validator run on
LLM-generated response text before it is returned to the user. It does not
generate, rewrite, or regenerate the response — Python remains routing,
safety enforcement, validation, and packaging only, per SOULMAP.md and the
SoulMap architecture constraints. Wording generation stays the LLM's job.

This sits alongside the existing response-level guards
(``response_contract.py`` for structural/style rules, ``resource_sanitizer.py``
for banned vocabulary) as a third, independent check focused specifically on
the safety-boundary categories from SOULMAP.md's non-negotiable safety rules:

- ``diagnosis``: presenting a clinical diagnosis or mental health label to the
  user (Rule 4, diagnosis prohibition)
- ``prediction_as_fact``: presenting the future, fate, destiny, or a karmic
  outcome as a certainty (Rule 5, prediction prohibition)
- ``dependency_reinforcement``: reinforcing the user's reliance on SoulMap
  instead of real-world support (Rule 3, dependency). Reuses
  ``resource_sanitizer.BANNED_DEPENDENCY_PHRASES`` rather than duplicating it,
  so the two guards cannot silently drift apart.
- ``guru_positioning``: SoulMap presenting itself as an authority to be
  followed rather than a mirror (never positioned as the user's primary place
  for inner life)
- ``excessive_certainty``: absolute, unhedged claims about the user's inner
  life or situation
- ``loss_of_independence``: language that discourages the user from thinking,
  deciding, or acting for themselves
- ``spiritual_claim_as_fact``: spiritual language that assigns certainty,
  identity, or destiny, which is Category 3 of
  ``skills/meta/epistemic-guardrails.md``. Targets the assertion rather than
  the vocabulary: the doctrine permits chakra, numerology, and karma language
  freely as a reflective lens, so "what you might call a throat theme" stays
  safe while "your throat chakra is blocked" does not

Adding a new category is a two-step change: add a `_PATTERNS` tuple of plain
regexes, then add it to `_CATEGORY_PATTERNS` below. No other file needs to
change.
"""

from __future__ import annotations

import json
import re
import sys

from soulmap.runtime.guards.resource_sanitizer import BANNED_DEPENDENCY_PHRASES
from soulmap.runtime.io.cli_payload import parse_json_object, require_str_field

DIAGNOSIS_PATTERNS: tuple[str, ...] = (
    r"\byou (?:have|'ve got) (?:a |an )?(?:clinical )?depression\b",
    r"\byou (?:have|'ve got) (?:an )?anxiety disorder\b",
    r"\byou(?:'re| are) bipolar\b",
    r"\byou(?:'re| are) diagnosed with\b",
    r"\byou meet the criteria for\b",
    r"\bthis is a symptom of\b",
    r"\byou have (?:adhd|ptsd|ocd|bpd)\b",
    r"\byou suffer from\b",
    r"\byou have a (?:disorder|syndrome|condition)\b",
    r"\bthat sounds like (?:a |an )?(?:disorder|syndrome)\b",
    r"\bi(?:'d| would) diagnose you with\b",
)

PREDICTION_AS_FACT_PATTERNS: tuple[str, ...] = (
    r"\byou will definitely\b",
    r"\bthis will (?:definitely |certainly )?happen\b",
    r"\bi predict\b",
    r"\byour destiny is\b",
    r"\byour fate is\b",
    r"\bthis is your destiny\b",
    r"\byou are going to end up\b",
    r"\bin the future you will\b",
    r"\bi (?:can )?guarantee (?:that )?you will\b",
    r"\bit is (?:certain|inevitable) that you will\b",
    r"\byour karma (?:means|guarantees)\b",
    r"\byour future is (?:already )?(?:written|set)\b",
)

GURU_POSITIONING_PATTERNS: tuple[str, ...] = (
    r"\btrust me completely\b",
    r"\bi am (?:always right|never wrong)\b",
    r"\bi am the only one who (?:can help you|understands you|understands your path)\b",
    r"\bonly i (?:understand|can guide) you\b",
    r"\bas your guide, i\b",
    r"\byou must listen to me\b",
    r"\bfollow my guidance without question\b",
    r"\bi know the truth\b",
    r"\bi know what(?:'s| is) best for you\b",
    r"\bas your (?:teacher|master), i\b",
)

EXCESSIVE_CERTAINTY_PATTERNS: tuple[str, ...] = (
    r"\bi am 100% certain\b",
    r"\bi am completely certain\b",
    r"\bwithout (?:a |any )?doubt\b",
    r"\bthis always works\b",
    r"\bthis never fails\b",
    r"\bi am absolutely certain\b",
    r"\bthere is no other explanation\b",
    r"\bthis is the only possible reason\b",
    r"\bthere can be no doubt\b",
)

# Category 3 of `skills/meta/epistemic-guardrails.md`: spiritual language that
# assigns certainty, identity, or destiny. The doctrine permits this vocabulary
# freely as a reflective lens, so these patterns target the assertion, not the
# subject matter. "What you might call a throat theme" is safe and must stay
# safe; "your throat chakra is blocked" is not.
#
# `PREDICTION_AS_FACT_PATTERNS` already covers `your destiny is` and
# `your karma means`. These add what the safety matrix recorded as missing:
# numerology, tarot, chakra, guide, and spiritual-identity framing.
#
# Identity confirmation is the highest-consequence item here. `scope_classifier`
# already blocks a user *asking* "am i a starseed"; this blocks SoulMap
# *answering* that they are. Reported harms from companion systems affirming a
# chosen-one or messianic self-image are the reason this category exists.
SPIRITUAL_CLAIM_AS_FACT_PATTERNS: tuple[str, ...] = (
    # Identity installation, doctrine Check 5
    (
        r"\byou(?:'re| are) (?:definitely |truly |clearly )?(?:a |an )?"
        r"(?:starseed|lightworker|twin flame|chosen one|old soul)\b"
    ),
    r"\byou(?:'re| are) (?:one of the )?chosen\b",
    r"\byour soul(?:'s)? (?:purpose|mission|contract) is\b",
    r"\byou were (?:chosen|sent here|put here) to\b",
    r"\byou have a special (?:purpose|mission|calling|gift)\b",
    # Numerology as destiny, doctrine numerology-specific rule
    r"\byour \d+ means you\b",
    r"\byour (?:life path |destiny |soul )?number means\b",
    r"\byou(?:'re| are) destined to\b",
    # Tarot as prediction, doctrine tarot-specific rule
    r"\bthe cards? (?:say|says|show|shows|reveals?) (?:that )?you will\b",
    r"\byour (?:tarot )?card means you (?:will|are going to)\b",
    r"\bi (?:pulled|drew) a card for you\b",
    # Chakra as diagnosis, doctrine chakra-specific rule
    r"\byour \w+ chakra is (?:blocked|closed|imbalanced|misaligned|weak|open)\b",
    r"\bchakra (?:blockage|imbalance) is (?:causing|why)\b",
    # Metaphysical agency confirmed as fact
    (
        r"\byour (?:spirit )?guides are (?:clearly |definitely )?"
        r"(?:communicating|telling|guiding|speaking)\b"
    ),
    r"\bthat(?:'s| is) (?:definitely|clearly|certainly) a sign\b",
    r"\bthe universe is (?:telling|showing|sending) you\b",
    r"\byour past life\b",
    # Karma and spiritual truth asserted as fact
    r"\bthis is your karma\b",
    r"\byour karmic debt\b",
    r"\bthis is (?:a |an )?(?:absolute |universal )?spiritual truth\b",
)

LOSS_OF_INDEPENDENCE_PATTERNS: tuple[str, ...] = (
    r"\byou don'?t need to think for yourself\b",
    r"\byou don'?t need anyone else'?s opinion\b",
    r"\bjust do what i say\b",
    r"\bonly follow my advice\b",
    r"\byou should only listen to me\b",
    r"\blet me decide for you\b",
    r"\bi'?ll tell you exactly what to do\b",
    r"\byou don'?t need to decide, i will\b",
    r"\bdo not question my (?:decision|guidance)\b",
)

# (category, patterns) — order only affects which category is listed first
# when a response triggers more than one.
_CATEGORY_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("diagnosis", DIAGNOSIS_PATTERNS),
    ("prediction_as_fact", PREDICTION_AS_FACT_PATTERNS),
    ("dependency_reinforcement", tuple(BANNED_DEPENDENCY_PHRASES)),
    ("guru_positioning", GURU_POSITIONING_PATTERNS),
    ("excessive_certainty", EXCESSIVE_CERTAINTY_PATTERNS),
    ("loss_of_independence", LOSS_OF_INDEPENDENCE_PATTERNS),
    ("spiritual_claim_as_fact", SPIRITUAL_CLAIM_AS_FACT_PATTERNS),
)


def check_response_safety_contract(response_text: str) -> dict[str, object]:
    """Detect safety-contract violations in a generated response.

    This only detects violations; it never rewrites or regenerates the
    response. Detection is deterministic substring/regex matching over the
    lowercased response text, with no external calls and no LLM involvement,
    so results are auditable and reproducible. Minimal overhead: a single
    lowercase pass plus a fixed, small set of regex scans.
    """
    lowered = response_text.lower()
    violations: list[dict[str, str]] = []

    for category, patterns in _CATEGORY_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, lowered):
                violations.append({"category": category, "pattern": pattern})

    if not violations:
        return {"status": "PASS", "violations": [], "categories": []}

    categories = sorted({violation["category"] for violation in violations})
    return {
        "status": "FAIL_REWRITE_REQUIRED",
        "violations": violations,
        "categories": categories,
        "instruction": (
            "Response violated SoulMap safety contract categories: "
            f"{', '.join(categories)}. Rewrite the response so it neither "
            "diagnoses, presents prediction as fact, reinforces dependency on "
            "SoulMap, positions SoulMap as a guru/authority, states excessive "
            "certainty, discourages the user's own independent thinking, nor "
            "presents a spiritual claim as certainty, identity, or destiny."
        ),
    }


def main() -> int:
    """Check a response for content-safety violations from standard input.

    Returns:
        The process exit code, 0 on success.

    Raises:
        ValueError: If the payload is not a JSON object or is missing a
            required field.
    """
    data = parse_json_object(sys.stdin.read())
    response_text = require_str_field(data, "response_text")
    result = check_response_safety_contract(response_text)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        raise SystemExit(1) from error
