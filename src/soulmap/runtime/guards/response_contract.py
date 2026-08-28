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
# international resources in AGENTS.md), and a localized one carries a query
# string. Counting that "?" flagged a valid crisis response as asking a
# question, which would send the response back for a rewrite it does not need.
# Only the "?" inside the matched link is removed, so a real question before or
# after a link still counts.
_URL_RE = re.compile(
    r"\b(?:https?://|www\.)\S+|\b[\w.-]+\.[a-z]{2,}/\S*", re.IGNORECASE
)


def grade_response_contract(
    response: str,
    selection: dict[str, object],
) -> dict[str, object]:
    """Check generated response text against the structural response rules.

    Enforces the structure rules in ``AGENTS.md``: at most one question, and
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
