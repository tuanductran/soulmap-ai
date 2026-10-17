"""Score conversation history for signs of unhealthy AI dependency."""

from __future__ import annotations

import json
import re
import sys
from bisect import bisect_left, bisect_right
from dataclasses import dataclass

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
_APOSTROPHE_ELISIONS = re.compile(
    r"'(?:cause|em|til|round|bout|n|tis|twas|twere|twill|kay|course|cept)\b",
    re.IGNORECASE,
)


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
                and not _APOSTROPHE_ELISIONS.match(message[index:])
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


def _has_unexcluded_occurrence(
    message: str, phrase: str, context_index: _ContextIndex
) -> bool:
    """Return whether a phrase occurs outside quoted or excluded context."""
    return any(
        not _is_context_excluded(context_index, match.start(), match.end())
        for match in re.finditer(re.escape(phrase), message)
    )


@dataclass(frozen=True)
class _ContextIndex:
    """Precomputed quote, cue, and clause-boundary offsets for one message."""

    quoted_spans: tuple[tuple[int, int], ...]
    cue_ends_by_group: dict[str, tuple[int, ...]]
    boundary_spans_by_group: dict[str, tuple[tuple[int, int], ...]]
    boundary_starts_by_group: dict[str, tuple[int, ...]]


def _build_context_index(message: str) -> _ContextIndex:
    """Build one reusable context index instead of rescanning each signal prefix."""
    quoted_spans = tuple(_quoted_spans(message))

    def is_quoted(start: int, end: int) -> bool:
        return any(
            quoted_start <= start and end <= quoted_end
            for quoted_start, quoted_end in quoted_spans
        )

    cue_ends: dict[str, set[int]] = {
        group: set() for group in _CONTEXT_EXCLUSION_GROUPS
    }
    for group, cue in _CONTEXT_EXCLUSION_CUES:
        for match in re.finditer(
            rf"(?<!\w){re.escape(cue)}(?!\w)",
            message,
            flags=re.IGNORECASE,
        ):
            if not is_quoted(match.start(), match.end()):
                cue_ends[group].add(match.end())

    boundary_spans: dict[str, tuple[tuple[int, int], ...]] = {}
    for group in _CONTEXT_EXCLUSION_GROUPS:
        spans: set[tuple[int, int]] = set()
        comma_is_boundary = _CONTEXT_EXCLUSION_POLICY.get(group, True)
        for boundary in _CLAUSE_BOUNDARY_CUES:
            if boundary == "," and not comma_is_boundary:
                continue
            if boundary in {".", ";", "!", "?", ","}:
                matches = re.finditer(re.escape(boundary), message)
            elif boundary.startswith(","):
                matches = re.finditer(
                    rf"{re.escape(boundary)}\b", message, flags=re.IGNORECASE
                )
            else:
                matches = re.finditer(
                    rf"\b{re.escape(boundary)}\b",
                    message,
                    flags=re.IGNORECASE,
                )
            for match in matches:
                if not is_quoted(match.start(), match.end()):
                    spans.add((match.start(), match.end()))
        boundary_spans[group] = tuple(sorted(spans))

    return _ContextIndex(
        quoted_spans=quoted_spans,
        cue_ends_by_group={
            group: tuple(sorted(ends)) for group, ends in cue_ends.items()
        },
        boundary_spans_by_group=boundary_spans,
        boundary_starts_by_group={
            group: tuple(span[0] for span in spans)
            for group, spans in boundary_spans.items()
        },
    )


def _is_context_excluded(index: _ContextIndex, start: int, end: int) -> bool:
    """Check a signal against its message's precomputed context index."""
    if any(
        quoted_start <= start and end <= quoted_end
        for quoted_start, quoted_end in index.quoted_spans
    ):
        return True

    for group, cue_ends in index.cue_ends_by_group.items():
        cue_index = bisect_right(cue_ends, start) - 1
        if cue_index < 0:
            continue
        cue_end = cue_ends[cue_index]

        boundaries = index.boundary_spans_by_group[group]
        boundary_starts = index.boundary_starts_by_group[group]
        boundary_index = bisect_left(boundary_starts, cue_end)
        boundary_end = bisect_left(boundary_starts, start)
        # Boundary phrases are short; only a final overlapping span can end
        # after the signal start. Walk backward until a completed boundary is
        # found, rather than rescanning every boundary in the interval.
        has_boundary = False
        while boundary_end > boundary_index:
            _, boundary_span_end = boundaries[boundary_end - 1]
            if boundary_span_end <= start:
                has_boundary = True
                break
            boundary_end -= 1

        if "third-party attribution" in group.lower():
            has_boundary = has_boundary or any(
                cue_end <= quoted_start and quoted_end <= start
                for quoted_start, quoted_end in index.quoted_spans
            )

        if not has_boundary:
            return True
    return False


def _unexcluded_decision_seeking_matches(
    message: str, context_index: _ContextIndex
) -> list[tuple[int, int]]:
    """Count decision-seeking spans once, preferring longer overlapping phrases."""
    candidates = [
        (match.start(), match.end())
        for phrase in _DECISION_SEEKING
        for match in re.finditer(rf"(?<!\w){re.escape(phrase)}(?!\w)", message)
        if not _is_context_excluded(context_index, match.start(), match.end())
    ]
    candidates.sort(key=lambda span: (span[0], -(span[1] - span[0]), span[1]))

    selected: list[tuple[int, int]] = []
    occupied_until = -1
    for start, end in candidates:
        if start >= occupied_until:
            selected.append((start, end))
            occupied_until = end
    return selected


def analyze_dependency(
    conversation_messages: list, *, current_message: str | None = None
) -> dict:
    """Analyze conversation history to detect AI dependency signals.

    Args:
        conversation_messages: Conversation messages with role and content.
        current_message: Optional current user turn appended to prior-only history.

    Returns:
        Dict with keys: level (str), score (int), signals (list), recommendation (str)
    """
    # The caller contract defines conversation_messages as prior turns.
    # Always append the current turn when supplied: text equality cannot tell
    # whether the same words are a previous turn or the current turn repeated.
    messages = list(conversation_messages)
    if current_message:
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

    context_indexes = [_build_context_index(msg) for msg in user_messages]

    for msg, context_index in zip(user_messages, context_indexes):
        keyword_match = next(
            (
                keyword
                for keyword in _DEPENDENCY_KEYWORDS
                if _has_unexcluded_occurrence(msg, keyword, context_index)
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
                not _is_context_excluded(context_index, match.start(), match.end())
                for match in pattern.finditer(msg)
            ):
                signal = f"dependency_pattern: '{label}'"
                if signal not in signals_found:
                    score += _DEPENDENCY_REGEX_WEIGHT
                    signals_found.append(signal)
                break

    decision_count = 0
    for msg, context_index in zip(user_messages, context_indexes):
        unexcluded_matches = _unexcluded_decision_seeking_matches(msg, context_index)
        decision_count += len(unexcluded_matches)
        score += len(unexcluded_matches) * _DECISION_SEEKING_WEIGHT
    if decision_count > 0:
        signals_found.append(f"decision_seeking_count: {decision_count}")

    for msg, context_index in zip(user_messages, context_indexes):
        for signal in _ISOLATION_SIGNALS:
            if _has_unexcluded_occurrence(msg, signal, context_index):
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
