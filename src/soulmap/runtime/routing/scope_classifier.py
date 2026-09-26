"""Classify requests against SoulMap scope and safety boundaries."""

from __future__ import annotations

import json
import re
import sys
from functools import cache

from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_non_empty_str_field,
)
from soulmap.runtime.io.text_normalization import normalize_message_text

from soulmap.runtime.knowledge.scope_source import load_scope_rules

_RULES = load_scope_rules()
WHITELIST_TIER1 = _RULES.whitelist_tier1
WHITELIST_TIER2 = _RULES.whitelist_tier2
BLACKLIST_LAYER1 = _RULES.blacklist_layer1
BLACKLIST_PROHIBITED = _RULES.blacklist_prohibited


@cache
def _keyword_pattern(keyword: str) -> re.Pattern[str]:
    escaped = re.escape(keyword)
    pattern = escaped.replace(r"\ ", r"\s+")
    return re.compile(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])")


def _contains_keyword(message: str, keyword: str) -> bool:
    return bool(_keyword_pattern(keyword).search(message))


def classify_message(message: str) -> dict:
    """Classify an incoming user message against the SoulMap scope system.

    Returns:
        dict with keys: tier, category, action, explanation
    """
    msg = normalize_message_text(message)

    for category, keywords in BLACKLIST_PROHIBITED.items():
        for kw in keywords:
            if _contains_keyword(msg, kw):
                return {
                    "tier": "BLACKLIST_PROHIBITED",
                    "category": category,
                    "action": "DECLINE_AND_REDIRECT",
                    "explanation": f"Prohibited request type detected: '{category}'. "
                    "Decline clearly using appropriate template in redirect-templates.md. "
                    "Apply escalation protocol if user persists.",
                    "matched_keyword": kw,
                }

    for category, keywords in BLACKLIST_LAYER1.items():
        for kw in keywords:
            if _contains_keyword(msg, kw):
                return {
                    "tier": "BLACKLIST_LAYER1",
                    "category": category,
                    "action": "DECLINE_WITH_CLEAN_EXIT",
                    "explanation": f"Out-of-scope topic detected: '{category}'. "
                    "Use two-part redirect: clean exit first, then optional inner door. "
                    "Do not presume a deeper layer exists.",
                    "matched_keyword": kw,
                }

    for category, keywords in WHITELIST_TIER1.items():
        for kw in keywords:
            if _contains_keyword(msg, kw):
                return {
                    "tier": "WHITELIST_TIER1",
                    "category": category,
                    "action": "RESPOND_FULLY",
                    "explanation": f"In-scope topic: '{category}'. "
                    "Respond fully using the five-step framework. "
                    "Presence first if emotional intensity is high.",
                    "matched_keyword": kw,
                }

    for category, keywords in WHITELIST_TIER2.items():
        for kw in keywords:
            if _contains_keyword(msg, kw):
                return {
                    "tier": "WHITELIST_TIER2",
                    "category": category,
                    "action": "ASK_INNER_CONNECTION",
                    "explanation": f"Conditional topic detected: '{category}'. "
                    "Before engaging, ask what this is stirring up inside the user. "
                    "Example: 'What is this question touching inside you?'",
                    "matched_keyword": kw,
                }

    return {
        "tier": "AMBIGUOUS",
        "category": "unknown",
        "action": "EXPLORE_GENTLY",
        "explanation": "No strong scope signal detected. "
        "Gently explore whether this connects to the user's inner experience. "
        "Use an open question to invite them inward.",
        "matched_keyword": None,
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message = require_non_empty_str_field(data, "message")
        result = classify_message(message)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
