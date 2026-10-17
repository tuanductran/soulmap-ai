"""Score conversation history for signs of unhealthy AI dependency."""

from __future__ import annotations

import json
import re
import sys

from soulmap.runtime.io.text_normalization import normalize_message_text
from soulmap.runtime.knowledge.keyword_lists import (
    load_key_value_table,
    load_labeled_groups,
    load_table_rows,
)
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

_SOURCE = runtime_skill_path("dependency-detection")
_SIGNAL_GROUPS = load_labeled_groups(_SOURCE, "Detection signals")
_DEPENDENCY_KEYWORDS = _SIGNAL_GROUPS["dependency keywords"]
_DECISION_SEEKING = _SIGNAL_GROUPS["decision-seeking phrases"]
_ISOLATION_SIGNALS = _SIGNAL_GROUPS["isolation signals"]

_PATTERN_ROWS = load_table_rows(_SOURCE, "Regex patterns")
_DEPENDENCY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (row[0], re.compile(row[1].strip(chr(96))))
    for row in _PATTERN_ROWS
    if len(row) >= 2
)

_SCORING = load_key_value_table(_SOURCE, "Scoring")
_GUIDANCE = load_key_value_table(_SOURCE, "Guidance")
_CONTEXT_EXCLUSION_GROUPS = load_labeled_groups(_SOURCE, "Context exclusion cues")
_CONTEXT_EXCLUSION_CUES = tuple(
    (group, cue) for group, cues in _CONTEXT_EXCLUSION_GROUPS.items() for cue in cues
)
_CONTEXT_EXCLUSION_POLICY = {
    row[0].lower(): row[1].strip().lower() == "yes"
    for row in load_table_rows(_SOURCE, "Context exclusion policy")
    if len(row) >= 2
}
_CLAUSE_BOUNDARY_GROUPS = load_labeled_groups(_SOURCE, "Clause boundaries")
_CLAUSE_BOUNDARY_CUES = tuple(
    cue for cues in _CLAUSE_BOUNDARY_GROUPS.values() for cue in cues
)
_DEPENDENCY_KEYWORD_WEIGHT = int(_SCORING["Dependency keyword weight"])
_DEPENDENCY_REGEX_WEIGHT = int(_SCORING["Dependency regex weight"])
_DECISION_SEEKING_WEIGHT = int(_SCORING["Decision-seeking weight"])
_ISOLATION_SIGNAL_WEIGHT = int(_SCORING["Isolation signal weight"])
_HIGH_MESSAGE_VOLUME_THRESHOLD = int(_SCORING["High message volume threshold"])
_HIGH_MESSAGE_VOLUME_BONUS = int(_SCORING["High message volume bonus"])
_HIGH_DEPENDENCY_THRESHOLD = int(_SCORING["High dependency threshold"])
_MODERATE_DEPENDENCY_THRESHOLD = int(_SCORING["Moderate dependency threshold"])


def _quoted_spans(message: str) -> list[tuple[int, int]]:
    """Return quoted spans while leaving contractions intact."""
    spans: list[tuple[int, int]] = []
    start: int | None = None
    closing: str | None = None

    for index, char in enumerate(message):
        if closing is None:
            if char in {'"', chr(0x201C), chr(0x2018)}:
                start = index
                closing = {
                    '"': '"',
                    chr(0x201C): chr(0x201D),
                    chr(0x2018): chr(0x2019),
                }[char]
            elif (
                char == "'"
                and (index == 0 or not message[index - 1].isalnum())
                and index + 1 < len(message)
                and not message[index + 1].isspace()
            ):
                start = index
                closing = "'"
            continue

        if char != closing and not (closing == chr(0x2019) and char == "'"):
            continue
        if (
            char == "'"
            and index > 0
            and index + 1 < len(message)
            and message[index - 1].isalnum()
            and message[index + 1].isalnum()
        ):
            continue
        if start is not None:
            spans.append((start, index + 1))
        start = None
        closing = None

    return spans


def _has_unexcluded_occurrence(message: str, phrase: str) -> bool:
    """Return whether a phrase occurs outside quoted or excluded context."""
    return any(
        not _is_context_excluded(message, match.start(), match.end())
        for match in re.finditer(re.escape(phrase), message)
    )


def _is_context_excluded(message: str, start: int, end: int) -> bool:
    """Check whether one signal occurrence is quoted or contextually excluded."""
    quoted_spans = _quoted_spans(message)
    if any(
        quoted_start <= start and end <= quoted_end
        for quoted_start, quoted_end in quoted_spans
    ):
        return True

    for group, cue in _CONTEXT_EXCLUSION_CUES:
        for match in re.finditer(re.escape(cue), message[:start], flags=re.IGNORECASE):
            cue_is_quoted = any(
                quoted_start <= match.start() and match.end() <= quoted_end
                for quoted_start, quoted_end in quoted_spans
            )
            if (
                match.end() <= start
                and not cue_is_quoted
                and not _has_clause_boundary(
                    message[match.end() : start],
                    comma_is_boundary=_CONTEXT_EXCLUSION_POLICY.get(group, True),
                    quoted_span_is_boundary="attribution" in group.lower(),
                )
            ):
                return True
    return False


def _has_clause_boundary(
    text: str,
    *,
    comma_is_boundary: bool,
    quoted_span_is_boundary: bool,
) -> bool:
    """Check Markdown-defined clause boundaries for one exclusion cue."""
    if quoted_span_is_boundary and _quoted_spans(text):
        return True
    for boundary in _CLAUSE_BOUNDARY_CUES:
        if boundary == "," and not comma_is_boundary:
            continue
        if boundary in {".", ";", "!", "?", ","}:
            if boundary in text:
                return True
        elif re.search(rf"\b{re.escape(boundary)}\b", text, flags=re.IGNORECASE):
            return True
    return False


def analyze_dependency(
    conversation_messages: list, *, current_message: str | None = None
) -> dict:
    """Analyze conversation history to detect AI dependency signals.

    Args:
        conversation_messages: Conversation messages with role and content.
        current_message: Optional current user turn; included unless already last.

    Returns:
        Dict with keys: level (str), score (int), signals (list), recommendation (str)
    """
    # The caller contract defines conversation_messages as prior turns.
    # Always append the current turn when supplied: text equality cannot tell
    # whether the same words are a previous turn or the current turn repeated.
    messages = list(conversation_messages)
    if current_message is not None:
        messages.append({"role": "user", "content": current_message})

    score = 0
    signals_found = []

    user_messages = [
        normalize_message_text(m["content"])
        for m in messages
        if isinstance(m, dict) and m.get("role") == "user"
    ]

    if not user_messages:
        return {
            "level": "NO_DATA",
            "score": 0,
            "signals": [],
            "recommendation": "No user messages found in conversation history.",
        }

    for msg in user_messages:
        keyword_match = next(
            (
                keyword
                for keyword in _DEPENDENCY_KEYWORDS
                if _has_unexcluded_occurrence(msg, keyword)
            ),
            None,
        )
        if keyword_match:
            signal = f"dependency_keyword: '{keyword_match}'"
            if signal not in signals_found:
                score += _DEPENDENCY_KEYWORD_WEIGHT
                signals_found.append(signal)
            continue

        for label, pattern in _DEPENDENCY_PATTERNS:
            if any(
                not _is_context_excluded(msg, match.start(), match.end())
                for match in pattern.finditer(msg)
            ):
                signal = f"dependency_pattern: '{label}'"
                if signal not in signals_found:
                    score += _DEPENDENCY_REGEX_WEIGHT
                    signals_found.append(signal)
                break

    decision_count = 0
    for msg in user_messages:
        for phrase in _DECISION_SEEKING:
            if _has_unexcluded_occurrence(msg, phrase):
                decision_count += 1
                score += _DECISION_SEEKING_WEIGHT
    if decision_count > 0:
        signals_found.append(f"decision_seeking_count: {decision_count}")

    for msg in user_messages:
        for signal in _ISOLATION_SIGNALS:
            if _has_unexcluded_occurrence(msg, signal):
                score += _ISOLATION_SIGNAL_WEIGHT
                if signal not in signals_found:
                    signals_found.append(f"isolation_signal: '{signal}'")

    if len(user_messages) > _HIGH_MESSAGE_VOLUME_THRESHOLD:
        score += _HIGH_MESSAGE_VOLUME_BONUS
        signals_found.append(f"high_message_volume: {len(user_messages)} user messages")

    if score >= _HIGH_DEPENDENCY_THRESHOLD:
        level = "HIGH_DEPENDENCY"
    elif score >= _MODERATE_DEPENDENCY_THRESHOLD:
        level = "MODERATE_DEPENDENCY"
    else:
        level = "LOW_DEPENDENCY"

    return {
        "level": level,
        "score": score,
        "signals": signals_found,
        "recommendation": _GUIDANCE[level],
    }


if __name__ == "__main__":
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            print(
                json.dumps(
                    {
                        "level": "NO_DATA",
                        "score": 0,
                        "signals": [],
                        "recommendation": "No input provided.",
                    }
                )
            )
            sys.exit(0)

        data = json.loads(raw)
        messages = data if isinstance(data, list) else data.get("messages", [])
        result = analyze_dependency(messages)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except json.JSONDecodeError as e:
        print(json.dumps({"level": "ERROR", "error": f"JSON parse error: {e!s}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"level": "ERROR", "error": str(e)}))
        sys.exit(1)
