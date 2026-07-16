"""Load pattern-detection knowledge straight from the shipped Markdown skill.

`skills/frameworks/pattern-mapper.md` is the single source of truth for pattern
names, descriptions, detection signals, cycle phrases, SoulMap role guidance, and
reflection language. This module parses that Markdown (plain prose sections, no
YAML front matter keys) into the structure `detectors/pattern_detector.py` needs
at runtime, so the two never drift apart.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_HEADING_RE = re.compile(r"^##\s+Pattern\s+\d+:\s*(?P<name>.+?)\s*$")
_QUOTED_RE = re.compile(r'"([^"]+)"')

_KNOWN_LABELS = (
    "what it looks like",
    "detection signals",
    "cycle phrases",
    "reflection language",
    "soulmap role",
    "root origin",
)


@dataclass(frozen=True)
class PatternSignal:
    slug: str
    name: str
    description: str
    keywords: tuple[str, ...] = field(default_factory=tuple)
    cycle_phrases: tuple[str, ...] = field(default_factory=tuple)
    soulmap_role: str = ""
    reflection_language: tuple[str, ...] = field(default_factory=tuple)


def _slugify(name: str) -> str:
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")


def _split_sections(block_lines: list[str]) -> dict[str, list[str]]:
    """Split a pattern's body lines into label -> logical (unwrapped) lines.

    Bullets that wrap onto a following indented line are joined back into one
    logical line so multi-line quoted phrases parse correctly.
    """

    sections: dict[str, list[str]] = {}
    current: str | None = None

    for raw in block_lines:
        line = raw.rstrip()
        stripped = line.strip()
        label_match = re.match(
            r"^\*\*([^:*]+?)(?:\s*\([^)]*\))?:\*\*\s*(.*)$", stripped
        )
        label = label_match.group(1).strip().lower() if label_match else None
        if label_match and label is not None and label in _KNOWN_LABELS:
            current = label
            sections.setdefault(current, [])
            remainder = label_match.group(2).strip()
            if remainder:
                sections[current].append(remainder)
            continue
        if current is None:
            continue
        if not stripped:
            continue
        bucket = sections[current]
        if stripped.startswith("- ") or not bucket:
            bucket.append(stripped)
        else:
            # Continuation of a wrapped bullet/paragraph line.
            bucket[-1] = f"{bucket[-1]} {stripped}"

    return sections


def _prose(lines: list[str]) -> str:
    return " ".join(lines).strip()


def _bulleted_lines(lines: list[str]) -> list[str]:
    # Bullets in this file are one per source line, prefixed with "- ".
    return [line[2:].strip() for line in lines if line.startswith("- ")]


def _quoted_phrases(bullet_lines: list[str]) -> tuple[str, ...]:
    phrases: list[str] = []
    for line in bullet_lines:
        phrases.extend(m.lower() for m in _QUOTED_RE.findall(line))
    return tuple(dict.fromkeys(phrases))


def parse_pattern_mapper(text: str) -> dict[str, PatternSignal]:
    lines = text.splitlines()
    heading_indices: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        match = _HEADING_RE.match(line.strip())
        if match:
            heading_indices.append((idx, match.group("name")))

    signals: dict[str, PatternSignal] = {}
    for pos, (start_idx, name) in enumerate(heading_indices):
        end_idx = (
            heading_indices[pos + 1][0]
            if pos + 1 < len(heading_indices)
            else len(lines)
        )
        body = lines[start_idx + 1 : end_idx]
        sections = _split_sections(body)

        description = _prose(sections.get("what it looks like", []))
        keyword_bullets = _bulleted_lines(sections.get("detection signals", []))
        keywords = _quoted_phrases(keyword_bullets)

        cycle_bullets = _bulleted_lines(sections.get("cycle phrases", []))
        cycle_phrases = _quoted_phrases(cycle_bullets) or tuple(
            b.strip('"').lower() for b in cycle_bullets
        )

        soulmap_role = _prose(sections.get("soulmap role", []))

        reflection_bullets = _bulleted_lines(sections.get("reflection language", []))
        # Preserve original casing/punctuation for display text (quotes stripped,
        # not lowercased like the matching keyword phrases).
        reflection_language = tuple(
            b.strip('"') for b in reflection_bullets if b.strip('"')
        )

        slug = _slugify(name)
        signals[slug] = PatternSignal(
            slug=slug,
            name=name,
            description=description,
            keywords=keywords,
            cycle_phrases=cycle_phrases,
            soulmap_role=soulmap_role,
            reflection_language=reflection_language,
        )

    return signals


def load_pattern_signals(markdown_path: Path) -> dict[str, PatternSignal]:
    text = markdown_path.read_text(encoding="utf-8")
    return parse_pattern_mapper(text)


_RELATIVE_MARKDOWN_PATH = Path("skills") / "frameworks" / "pattern-mapper.md"


def default_pattern_mapper_path() -> Path:
    """Locate ``skills/frameworks/pattern-mapper.md`` without depending on devtools.

    Runtime modules ship and run standalone (invoked via stdin JSON), so this
    intentionally does not import ``soulmap.devtools``. It walks up from this
    file, then from the current working directory, looking for the shipped
    Markdown skill.
    """

    import os

    env_root = os.environ.get("SOULMAP_REPO_ROOT")
    if env_root:
        candidate = Path(env_root) / _RELATIVE_MARKDOWN_PATH
        if candidate.exists():
            return candidate

    for base in (Path(__file__).resolve(), Path.cwd().resolve()):
        for parent in (base, *base.parents):
            candidate = parent / _RELATIVE_MARKDOWN_PATH
            if candidate.exists():
                return candidate

    raise FileNotFoundError(
        "Could not locate skills/frameworks/pattern-mapper.md; set "
        "SOULMAP_REPO_ROOT or run from within the soulmap-ai repo."
    )
