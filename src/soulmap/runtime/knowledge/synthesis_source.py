"""Load conversation-synthesis detection knowledge from Markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from soulmap.runtime.knowledge.keyword_lists import default_skill_path, extract_labeled_groups

_CONTRACT_HEADING = "Runtime detection contract"
_THRESHOLD_RE = re.compile(r"^\|\s*(?P<name>[^|]+?)\s*\|\s*(?P<value>\d+)\s*\|\s*$", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class SynthesisRules:
    """Executable configuration authored in conversation-synthesis.md."""

    minimum_user_messages: int
    automatic_user_messages: int
    minimum_recurring_themes: int
    max_themes: int
    max_anchors: int
    max_longitudinal: int
    explicit_requests: tuple[str, ...]
    emotional_themes: dict[str, tuple[str, ...]]
    value_themes: dict[str, tuple[str, ...]]
    conflict_themes: dict[str, tuple[str, ...]]


def _contract_body(text: str) -> str:
    match = re.search(
        rf"^## {re.escape(_CONTRACT_HEADING)}\s*$",
        text,
        re.MULTILINE,
    )
    if match is None:
        raise ValueError("Conversation synthesis runtime contract is missing.")
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def _table_values(body: str) -> dict[str, int]:
    section = re.search(
        r"### Detection thresholds(?P<body>.*?)(?=\n### |\Z)",
        body,
        re.DOTALL,
    )
    if section is None:
        raise ValueError("Synthesis detection thresholds are missing.")
    values: dict[str, int] = {}
    for match in _THRESHOLD_RE.finditer(section.group("body")):
        key = re.sub(r"[^a-z0-9]+", "_", match.group("name").strip().lower()).strip("_")
        values[key] = int(match.group("value"))
    required = {
        "minimum_user_messages",
        "automatic_synthesis_user_messages",
        "minimum_distinct_recurring_themes_for_automatic_synthesis",
        "maximum_themes_returned",
        "maximum_anchors_per_theme",
        "maximum_longitudinal_themes",
    }
    if set(values) != required:
        raise ValueError("Synthesis detection thresholds are incomplete.")
    return values


def _quoted_bullets(section: str, heading: str) -> tuple[str, ...]:
    match = re.search(
        rf"^### {re.escape(heading)}\s*$(?P<body>.*?)(?=^### |\Z)",
        section,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise ValueError(f"Synthesis section {heading!r} is missing.")
    return tuple(
        dict.fromkeys(
            phrase.lower()
            for line in match.group("body").splitlines()
            if (phrase := (re.match(r'^- "([^"]+)"\s*$', line.strip()) or [None, None])[1])
        )
    )


def _theme_groups(body: str, heading: str) -> dict[str, tuple[str, ...]]:
    match = re.search(
        rf"^### {re.escape(heading)} signals\s*$(?P<body>.*?)(?=^### |\Z)",
        body,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise ValueError(f"Synthesis theme section {heading!r} is missing.")
    groups: dict[str, tuple[str, ...]] = {}
    current: str | None = None
    for line in match.group("body").splitlines():
        stripped = line.strip()
        if stripped.startswith("#### "):
            current = stripped[5:].strip().lower()
            groups[current] = ()
        elif current and (m := re.match(r'^- "([^"]+)"\s*$', stripped)):
            groups[current] = groups[current] + (m.group(1).lower(),)
    if not groups or any(not phrases for phrases in groups.values()):
        raise ValueError(f"Synthesis theme section {heading!r} is incomplete.")
    return groups


@lru_cache(maxsize=1)
def load_synthesis_rules() -> SynthesisRules:
    """Read and validate the runtime contract from shipped Markdown."""
    path = default_skill_path("skills/frameworks/conversation-synthesis.md")
    body = _contract_body(path.read_text(encoding="utf-8"))
    values = _table_values(body)
    return SynthesisRules(
        minimum_user_messages=values["minimum_user_messages"],
        automatic_user_messages=values["automatic_synthesis_user_messages"],
        minimum_recurring_themes=values[
            "minimum_distinct_recurring_themes_for_automatic_synthesis"
        ],
        max_themes=values["maximum_themes_returned"],
        max_anchors=values["maximum_anchors_per_theme"],
        max_longitudinal=values["maximum_longitudinal_themes"],
        explicit_requests=_quoted_bullets(body, "Explicit request signals"),
        emotional_themes=_theme_groups(body, "Recurring emotional theme"),
        value_themes=_theme_groups(body, "Recurring value"),
        conflict_themes=_theme_groups(body, "Recurring inner-conflict"),
    )
