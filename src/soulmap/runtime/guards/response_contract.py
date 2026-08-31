"""Check response-level SoulMap contract rules."""

from __future__ import annotations

import json
import re
import sys

from soulmap.runtime.io.cli_payload import (
    parse_json_object,
    require_dict_field,
    require_str_field,
)

BULLET_RE = re.compile(r"^\s*[-*]\s", re.MULTILINE)
QUESTION_RE = re.compile(r"\?")
# A question mark inside a link is punctuation, not a question. Crisis
# responses are exactly where links appear (findahelpline.com is one of the two
# international resources in SOULMAP.md), and a localized one carries a query
# string. Counting that "?" flagged a valid crisis response as asking a
# question, which would send the response back for a rewrite it does not need.
# Only the "?" inside the matched link is removed, so a real question before or
# after a link still counts.
_URL_RE = re.compile(
    r"\b(?:https?://|www\.)\S+|\b[\w.-]+\.[a-z]{2,}/\S*", re.IGNORECASE
)

# SOULMAP.md's length rules, as ceilings only. The emotional-versus-intellectual
# register split inside Mirror mode is a content judgment this layer cannot
# make, so Mirror is held to the higher of the two doctrine bounds (4
# paragraphs) rather than guessed at. Sanctuary covers acute grief, which the
# selector already routes to Sanctuary mode.
_SENTENCE_CEILINGS: dict[str, int] = {"CRISIS": 2, "SANCTUARY": 4}
_PARAGRAPH_CEILINGS: dict[str, int] = {"MIRROR": 4}

_SENTENCE_SPLIT_RE = re.compile(r"[.!?]+(?:\s|$)")
_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")

# A crisis response must carry helpline resources, and doctrine's "1-2
# sentences" counts SoulMap's own prose, not the resource block it is required
# to deliver first. Every listed line ("988", "0865 044 400", "13 11 14")
# carries at least three digits, and reflective prose effectively never does, so
# digit-bearing fragments are excluded before counting. Without this the
# canonical correct crisis response would be flagged for rewrite, which is the
# most damaging false positive this guard could produce.
#
# Counted rather than pattern-matched. This was `(?:\D*\d){3}`, whose nested
# quantifier backtracks polynomially: given a long run of non-digits it retries
# every split point, which measured 2.9 seconds at 20,000 characters and 45
# seconds at 80,000. That is reachable from generated response text and from
# whatever `main()` reads on stdin, so it was a denial-of-service path rather
# than a style problem. A bare `\d` has nothing to backtrack over, and counting
# its matches is exactly what the old pattern asked: are there three or more
# digits anywhere in this fragment.
#
# `str.isdigit()` is deliberately not used. It accepts characters `\d` rejects,
# such as the superscript "2", so it would silently widen what counts as a
# resource listing.
_MIN_RESOURCE_DIGITS = 3
_DIGIT_RE = re.compile(r"\d")


def _is_resource_fragment(fragment: str) -> bool:
    """Report whether a fragment is a helpline listing rather than prose.

    Args:
        fragment: One sentence fragment, already stripped.

    Returns:
        True when the fragment carries at least three digits.
    """
    return len(_DIGIT_RE.findall(fragment)) >= _MIN_RESOURCE_DIGITS


def _count_sentences(text: str, *, drop_resources: bool) -> int:
    """Count prose sentences, optionally excluding resource listings.

    Args:
        text: Response text with URLs already removed.
        drop_resources: When True, skip fragments carrying three or more
            digits, which are helpline listings rather than prose.

    Returns:
        The number of non-empty sentence fragments.
    """
    fragments = [part.strip() for part in _SENTENCE_SPLIT_RE.split(text)]
    return sum(
        1
        for fragment in fragments
        if fragment and not (drop_resources and _is_resource_fragment(fragment))
    )


def _count_paragraphs(text: str) -> int:
    """Count non-empty blank-line-separated blocks."""
    return sum(1 for block in _PARAGRAPH_SPLIT_RE.split(text) if block.strip())


def grade_response_contract(
    response: str,
    selection: dict[str, object],
) -> dict[str, object]:
    """Check generated response text against the structural response rules.

    Enforces the structure rules in ``SOULMAP.md``: at most one question, and
    that question last, never first; no semicolons; no bullet points; and no
    question at all in crisis or sanctuary mode, where the response must hold
    rather than ask.

    This detects violations only. It never rewrites the response.

    Args:
        response: The generated response text.
        selection: The framework selector's output. Its ``primary_framework``
            and ``mode`` decide whether the no-question rules apply.

    Returns:
        A dict with ``ok`` and a ``violations`` list of rule names. The list is
        empty when ``ok`` is True.
    """
    violations: list[str] = []
    stripped = response.strip()

    countable = _URL_RE.sub("", stripped)
    question_count = len(QUESTION_RE.findall(countable))
    if question_count > 1:
        violations.append("multiple_questions")
    if question_count == 1 and not stripped.endswith("?"):
        violations.append("question_not_last")
    if stripped.startswith("?"):
        violations.append("starts_with_question")
    if ";" in stripped:
        violations.append("semicolon")
    if BULLET_RE.search(stripped):
        violations.append("bullets")

    primary = str(selection.get("primary_framework", ""))
    mode = str(selection.get("mode", ""))
    if primary == "CRISIS" and question_count:
        violations.append("crisis_no_question")
    if mode == "SANCTUARY" and question_count:
        violations.append("sanctuary_no_question")

    sentence_ceiling = _SENTENCE_CEILINGS.get(mode)
    if sentence_ceiling is not None:
        sentences = _count_sentences(countable, drop_resources=mode == "CRISIS")
        if sentences > sentence_ceiling:
            violations.append("exceeds_sentence_ceiling")

    paragraph_ceiling = _PARAGRAPH_CEILINGS.get(mode)
    if (
        paragraph_ceiling is not None
        and _count_paragraphs(stripped) > paragraph_ceiling
    ):
        violations.append("exceeds_paragraph_ceiling")

    return {"ok": not violations, "violations": violations}


def main() -> int:
    """Grade a response from a JSON payload on standard input.

    Returns:
        The process exit code, 0 on success.

    Raises:
        ValueError: If the payload is not a JSON object or is missing a
            required field.
    """
    data = parse_json_object(sys.stdin.read())
    response = require_str_field(data, "response")
    selection = require_dict_field(data, "selection")
    result = grade_response_contract(response, selection)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        raise SystemExit(1) from error
