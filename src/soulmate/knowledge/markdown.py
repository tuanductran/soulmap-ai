"""Framework-neutral Markdown knowledge parsing primitives.

This module only parses explicitly provided Markdown text or paths. It does not
know about SoulMap routes, detectors, doctrine, or repository layout.
"""

from __future__ import annotations

import re
from pathlib import Path

_QUOTED_RE = re.compile(r'"([^"]+)"')
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def _heading_level(line: str) -> int | None:
    match = _HEADING_RE.match(line.strip())
    return len(match.group(1)) if match else None


def extract_keyword_section(text: str, heading: str) -> tuple[str, ...]:
    """Collect quoted phrases from bullets under an exact Markdown heading.

    Parsing stops at the next heading whose level is less than or equal to the
    target heading's level. An empty tuple is returned when the heading is absent.
    """

    lines = text.splitlines()
    target_level: int | None = None
    start: int | None = None

    for idx, line in enumerate(lines):
        level = _heading_level(line)
        if level is not None and line.strip()[level:].strip() == heading:
            target_level = level
            start = idx + 1
            break

    if start is None or target_level is None:
        return ()

    phrases: list[str] = []
    bullet_buffer: list[str] = []

    def flush() -> None:
        if bullet_buffer:
            joined = " ".join(bullet_buffer)
            phrases.extend(match.lower() for match in _QUOTED_RE.findall(joined))
            bullet_buffer.clear()

    for line in lines[start:]:
        level = _heading_level(line)
        if level is not None and level <= target_level:
            break
        stripped = line.strip()
        if stripped.startswith("- "):
            flush()
            bullet_buffer.append(stripped)
        elif stripped and bullet_buffer:
            bullet_buffer.append(stripped)
        else:
            flush()
    flush()

    return tuple(dict.fromkeys(phrases))


def load_keyword_section(markdown_path: Path, heading: str) -> tuple[str, ...]:
    """Load and parse one quoted-phrase section from a Markdown file."""

    return extract_keyword_section(markdown_path.read_text(encoding="utf-8"), heading)


def extract_labeled_groups(text: str, heading: str) -> dict[str, tuple[str, ...]]:
    """Collect quoted phrases grouped by category label under a heading.

    A label is a non-empty line ending in ``:``. Its key is the lowercased text
    before the first comma. Bullet phrases belong to the most recent label.
    """

    lines = text.splitlines()
    target_level: int | None = None
    start: int | None = None

    for idx, line in enumerate(lines):
        level = _heading_level(line)
        if level is not None and line.strip()[level:].strip() == heading:
            target_level = level
            start = idx + 1
            break

    if start is None or target_level is None:
        return {}

    groups: dict[str, list[str]] = {}
    current_label: str | None = None

    for line in lines[start:]:
        level = _heading_level(line)
        if level is not None and level <= target_level:
            break
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            if current_label is not None:
                quotes = [match.lower() for match in _QUOTED_RE.findall(stripped)]
                groups.setdefault(current_label, []).extend(quotes)
            continue
        if stripped.endswith(":"):
            label_text = stripped[:-1]
            key = label_text.split(",")[0].strip().lower()
            current_label = key
            groups.setdefault(current_label, [])

    return {key: tuple(dict.fromkeys(values)) for key, values in groups.items()}


def load_labeled_groups(
    markdown_path: Path, heading: str
) -> dict[str, tuple[str, ...]]:
    """Load and parse labeled phrase groups from a Markdown file."""

    return extract_labeled_groups(markdown_path.read_text(encoding="utf-8"), heading)
