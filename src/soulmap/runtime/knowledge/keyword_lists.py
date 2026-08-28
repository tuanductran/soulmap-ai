"""Load flat keyword-phrase lists straight from shipped Markdown skills.

Several detectors (spiritual bypass, shadow patterns) only need a plain tuple
of matching phrases per category — no name/description/reflection structure
like `pattern_source.py` builds. This module is the generic version: point it
at a Markdown heading (``##`` or ``###``) and it collects every quoted phrase
in the bullets under that heading, up to the next heading of the same or
higher level.
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

    Stops at the next heading whose level is <= the target heading's level.
    Returns an empty tuple if the heading is not found.
    """
    lines = text.splitlines()
    target_level: int | None = None
    start = None

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
            phrases.extend(m.lower() for m in _QUOTED_RE.findall(joined))
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
            # Continuation of a wrapped bullet line.
            bullet_buffer.append(stripped)
        else:
            flush()
    flush()

    return tuple(dict.fromkeys(phrases))


def load_keyword_section(markdown_path: Path, heading: str) -> tuple[str, ...]:
    """Read a Markdown file and extract one section's quoted phrases.

    Args:
        markdown_path: Path to the knowledge file that owns the phrases.
        heading: Heading text of the section to read, without leading hashes.

    Returns:
        The quoted phrases in document order, deduplicated. Empty when the
        heading is absent or holds no quoted phrase.

    Raises:
        OSError: If the file cannot be read. The phrase list is authored
            content, so a missing file is a repository error rather than a
            condition to absorb.
    """
    text = markdown_path.read_text(encoding="utf-8")
    return extract_keyword_section(text, heading)


def extract_labeled_groups(text: str, heading: str) -> dict[str, tuple[str, ...]]:
    """Collect quoted phrases grouped by category label under a Markdown heading.

    Handles sections shaped like::

        ## Detection signals

        Win or completion, something was achieved or finished:

        - "i finally did it"
        - "i did it"

        Relief after difficulty, the hard part is over:

        - "i can breathe again"

    Returns a dict keyed by the lowercased text before the first comma (or the
    whole label line if there's no comma) — e.g. ``{"win": (...), "relief": (...)}``.
    """
    lines = text.splitlines()
    target_level: int | None = None
    start = None

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
                quotes = [m.lower() for m in _QUOTED_RE.findall(stripped)]
                groups.setdefault(current_label, []).extend(quotes)
            continue
        if stripped.endswith(":"):
            label_text = stripped[:-1]
            key = label_text.split(",")[0].strip().lower()
            current_label = key
            groups.setdefault(current_label, [])

    return {k: tuple(dict.fromkeys(v)) for k, v in groups.items()}


def load_labeled_groups(
    markdown_path: Path, heading: str
) -> dict[str, tuple[str, ...]]:
    """Read a Markdown file and extract one section's labeled phrase groups.

    Args:
        markdown_path: Path to the knowledge file that owns the phrases.
        heading: Heading text of the section to read, without leading hashes.

    Returns:
        A mapping of lowercased category label to that label's phrases,
        deduplicated and in document order. Empty when the heading is absent.

    Raises:
        OSError: If the file cannot be read.
    """
    text = markdown_path.read_text(encoding="utf-8")
    return extract_labeled_groups(text, heading)


def default_skill_path(relative_path: str) -> Path:
    """Locate a file under ``skills/`` without depending on devtools.

    Mirrors ``pattern_source.default_pattern_mapper_path`` — runtime modules
    ship and run standalone, so this does not import ``soulmap.devtools``.
    """
    import os

    rel = Path(relative_path)
    env_root = os.environ.get("SOULMAP_REPO_ROOT")
    if env_root:
        candidate = Path(env_root) / rel
        if candidate.exists():
            return candidate

    for base in (Path(__file__).resolve(), Path.cwd().resolve()):
        for parent in (base, *base.parents):
            candidate = parent / rel
            if candidate.exists():
                return candidate

    raise FileNotFoundError(
        f"Could not locate {relative_path}; set SOULMAP_REPO_ROOT or run from "
        "within the soulmap-ai repo."
    )
