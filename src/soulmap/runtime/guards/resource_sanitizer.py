"""Sanitizes LLM outputs to enforce AGENTS.md language boundaries."""

from __future__ import annotations

import json
import re
import sys

from soulmap.runtime.io.cli_payload import parse_json_object, require_str_field

# Banned vocabulary defined in AGENTS.md (language rules section)
BANNED_WORDS = [
    r"\baction step[s]?\b",
    r"\bgoal[s]?\b",
    r"\bmilestone[s]?\b",
    r"\baligns with\b",
    r"\bdysregulated\b",
    r"\bnervous system\b",
    r"\bwindow of tolerance\b",
    r"\bhyperarousal\b",
]

BANNED_DEPENDENCY_PHRASES = [
    r"\bcome back anytime\b",
    r"\bi hope this helped\b",
    r"\bit was great talking with you\b",
    r"\bi(?:'| a)?m here for you\b",
    r"\bi(?:'| a)?m always here\b",
    r"\beven just here\b",
    r"\byour soulmate ai\b",
    r"\brelationship status\b",
    r"\bmore than just an ai\b",
    r"\byou only need me\b",
]


def check_banned_language(response_text: str) -> dict[str, object]:
    """Check text against AGENTS.md restricted words and formatting rules."""
    violations = []

    response_lower = response_text.lower()
    for word_pattern in BANNED_WORDS:
        if re.search(word_pattern, response_lower):
            violations.append(word_pattern)

    for phrase_pattern in BANNED_DEPENDENCY_PHRASES:
        if re.search(phrase_pattern, response_lower):
            violations.append(phrase_pattern)

    # Check Structural Rules: No Semicolons, No Bullet Points in conversational replies
    if ";" in response_text:
        violations.append("; (semicolons are forbidden)")

    if re.search(r"^\s*-\s|^\s*\*\s", response_text, re.MULTILINE):
        # Allow bullets if it's explicitly a synthesis (P10) or resource list, but
        # standard mirror modes forbid bullet points. This might need context awareness.
        violations.append("bullet_points")

    # Check Question Rule: Max 1 question, always the last sentence.
    questions = len(re.findall(r"\?", response_text))
    if questions > 1:
        violations.append("multiple_questions")
    elif questions == 1 and not response_text.strip().endswith("?"):
        violations.append("question_not_last_sentence")

    if not violations:
        return {"status": "PASS", "violations": []}

    return {
        "status": "FAIL_REWRITE_REQUIRED",
        "violations": violations,
        "instruction": "Output violated AGENTS.md language rules. Rewrite response without using banned vocabulary, maintaining exactly 1 question, and no prescriptive advice.",
    }


def main() -> int:
    data = parse_json_object(sys.stdin.read())
    response_text = require_str_field(data, "response_text")

    result = check_banned_language(response_text)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        raise SystemExit(1) from error
