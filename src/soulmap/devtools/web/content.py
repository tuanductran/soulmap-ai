"""Load canonical repository Markdown into the typed public page model.

This is the only place that reads `skills/` for the website, and it enforces
the allowlist while it reads. A document that is not public never becomes a
page model at all, and an internal section never enters one, so no downstream
template can leak either.

Markdown rendering uses `markdown-it-py`, already a main dependency of this
package, and the shared front-matter and anchor helpers in
`soulmap.devtools.support.markdown`, so the website never grows a second
Markdown implementation that could drift from the repository's own.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from markdown_it import MarkdownIt

from soulmap.devtools.support.markdown import (
    parse_yaml_front_matter,
    slugify_github_anchor,
)
from soulmap.devtools.web.allowlist import is_internal_section, is_public_skill

_ATX_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")

# A bold label standing in for a heading: **Detection signals:** or
# **Activation Signals**. Matched case-insensitively against the same names as
# the heading form, so both spellings are covered by one list.
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")

# Path segments belonging to material the website does not publish. Matching on
# segments rather than on a full prefix matters: canonical files link to each
# other relatively, so the same private target appears as `skills/meta/x.md`,
# `../meta/x.md`, and `./meta/x.md` in different files.
_PRIVATE_PATH_SEGMENTS: frozenset[str] = frozenset(
    {"meta", "safety", "spiritual", "soulmate", "templates", ".claude", "src"}
)


def _is_private_target(reference: str) -> bool:
    """Report whether a link target or label points at non-public material.

    Args:
        reference: A link target or its visible label.

    Returns:
        True when any path segment names a private area, or the reference
        points at a category ``SKILL.md``, which the allowlist never publishes.
    """
    cleaned = reference.split("#", 1)[0].strip()
    segments = [part for part in cleaned.split("/") if part not in {"", ".", ".."}]
    if any(segment in _PRIVATE_PATH_SEGMENTS for segment in segments[:-1]):
        return True
    return cleaned.endswith("SKILL.md")


_LABELLED_SIGNAL_RE = re.compile(
    r"^\*\*\s*(detection signals?|activation signals?|paired template)\s*:?\s*\*\*:?\s*$",
    re.IGNORECASE,
)

# The priority table in SOULMAP.md, one framework per row:
# | Medium | Inner Parts | Inner conflict is present without clear insight |
_PRIORITY_ROW_RE = re.compile(
    r"^\|\s*(Highest|Very high|High|Medium|Lower|Default)\s*\|\s*([^|]+?)\s*\|"
)

TIER_ORDER: tuple[str, ...] = (
    "Highest",
    "Very high",
    "High",
    "Medium",
    "Lower",
    "Default",
)


@dataclass(frozen=True, slots=True)
class PublicSection:
    """One rendered section of a public page.

    Attributes:
        heading: Section heading text, without leading hashes.
        level: Heading level, 2 for ``##``.
        anchor: GitHub-compatible slug, for in-page links.
        html: Rendered body HTML, excluding the heading itself.
    """

    heading: str
    level: int
    anchor: str
    html: str


@dataclass(frozen=True, slots=True)
class PublicPage:
    """One public page derived from a canonical repository document.

    Attributes:
        slug: URL segment, derived from the filename stem.
        name: Human-readable name, from front matter or the first heading.
        description: One-line summary from front matter.
        category: Parent directory under `skills/`, or ``"doctrine"``.
        tier: Priority tier from the SOULMAP.md table, None when the document
            is not a routed framework.
        sections: Public sections in document order, internal ones removed.
        source_path: Repository-relative path, for the "read the source" link.
    """

    slug: str
    name: str
    description: str
    category: str
    tier: str | None
    sections: tuple[PublicSection, ...]
    source_path: str


def _delink_private_targets(text: str) -> str:
    """Turn links to non-public files into plain text.

    An allowlisted document may still reference an internal one. Rendering that
    reference as a link would emit a dead link and advertise the internal
    file's path. The reference is kept as plain text so the sentence still
    reads, but it stops being a pointer, and the path itself is dropped.

    Args:
        text: Markdown body text.

    Returns:
        The text with private-target links flattened to their label.
    """

    def replace(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2)
        if _is_private_target(target) or _is_private_target(label):
            # A bare path used as its own label would leave the internal path
            # visible as text even after the link is removed.
            if _is_private_target(label):
                return "the internal knowledge base"
            return label
        return match.group(0)

    return _MD_LINK_RE.sub(replace, text)


def _markdown_renderer() -> MarkdownIt:
    """Build the Markdown renderer used for every public page.

    Returns:
        A CommonMark renderer with tables enabled and raw HTML disabled.
        Disabling raw HTML matters: canonical files are trusted, but rendering
        them with HTML passthrough would make any future authoring mistake a
        markup injection into the public site.
    """
    md = MarkdownIt("commonmark", {"html": False, "linkify": False})
    md.enable("table")
    return md


def _split_front_matter(text: str) -> tuple[dict[str, str], list[str]]:
    """Separate YAML front matter from the document body.

    Args:
        text: The full file contents.

    Returns:
        The parsed front-matter mapping (empty when absent) and the body lines
        with the front-matter block removed.
    """
    lines = text.splitlines()
    front = parse_yaml_front_matter(lines) or {}
    if not front or not lines or lines[0].strip() != "---":
        return front, lines

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return front, lines[index + 1 :]
    return front, lines


def _iter_blocks(body: list[str]) -> list[tuple[int, str, list[str]]]:
    """Split a document body into blocks at every heading level.

    Splitting at all six levels, rather than only at ``#`` and ``##``, is a
    safety requirement rather than a formatting preference: a `### Detection
    signals` subsection must be droppable on its own, and a splitter that only
    saw level-2 headings would leave it embedded in its parent section's body.

    Args:
        body: Document lines with front matter already removed.

    Returns:
        Tuples of heading level, heading text, and body lines. The preamble
        before the first heading is returned at level 0 with an empty heading.
        Fenced code blocks are tracked so a ``#`` comment inside one is never
        mistaken for a heading.
    """
    blocks: list[tuple[int, str, list[str]]] = []
    heading = ""
    level = 0
    buffer: list[str] = []
    fence: str | None = None

    for raw in body:
        fence_match = _FENCE_RE.match(raw)
        if fence_match:
            marker = fence_match.group(1)[0]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            buffer.append(raw)
            continue

        heading_match = None if fence else _ATX_HEADING_RE.match(raw)
        if heading_match:
            blocks.append((level, heading, buffer))
            level = len(heading_match.group(1))
            heading = heading_match.group(2).strip()
            buffer = []
            continue

        buffer.append(raw)

    blocks.append((level, heading, buffer))
    return blocks


def _drop_internal_blocks(
    blocks: list[tuple[int, str, list[str]]],
) -> list[tuple[int, str, list[str]]]:
    """Remove internal sections and everything nested beneath them.

    Dropping a heading must also drop its subsections, otherwise a
    `## Detection signals` section with `### Acute` beneath it would lose only
    its own preamble and publish the phrase lists underneath.

    Args:
        blocks: Blocks from ``_iter_blocks``.

    Returns:
        The blocks that may become public sections.
    """
    kept: list[tuple[int, str, list[str]]] = []
    skip_above: int | None = None

    for level, heading, lines in blocks:
        if skip_above is not None:
            if level > skip_above:
                continue
            skip_above = None

        if heading and is_internal_section(heading):
            skip_above = level
            continue

        kept.append((level, heading, lines))

    return kept


def _scrub_labelled_signals(lines: list[str]) -> list[str]:
    """Remove bold-labelled signal blocks that are not Markdown headings.

    Several framework files mark phrase lists with a bold label rather than a
    heading, for example ``**Detection signals:**`` followed by a bullet list.
    `pattern-mapper.md` alone carries six. A heading-only filter leaves every
    one of them public, so the label form is stripped here with the bullet list
    that follows it.

    Args:
        lines: A block's body lines.

    Returns:
        The lines with labelled signal blocks removed.
    """
    kept: list[str] = []
    dropping = False

    for raw in lines:
        stripped = raw.strip()

        if _LABELLED_SIGNAL_RE.match(stripped):
            dropping = True
            continue

        if dropping:
            # Consume the label's bullet list and any blank lines inside it.
            # The first line that is neither blank nor a list item ends it.
            if not stripped or stripped.startswith(("-", "*", "+")):
                continue
            dropping = False

        kept.append(raw)

    return kept


def load_priority_tiers(repo_root: Path) -> dict[str, str]:
    """Read the framework priority tiers from the SOULMAP.md doctrine table.

    The website groups frameworks the way SoulMap actually decides between
    them, so the tiers are parsed from doctrine rather than hardcoded. When the
    table changes, the site regroups itself on the next build.

    Args:
        repo_root: Repository root.

    Returns:
        A mapping of lowercased framework display name to its priority tier.

    Raises:
        OSError: If SOULMAP.md cannot be read. It is canonical doctrine, so a
            missing file is a repository error rather than a condition to
            absorb.
    """
    text = (repo_root / "SOULMAP.md").read_text(encoding="utf-8")
    tiers: dict[str, str] = {}
    for line in text.splitlines():
        match = _PRIORITY_ROW_RE.match(line)
        if match:
            tiers[match.group(2).strip().lower()] = match.group(1).strip()
    return tiers


# Words that stay lowercase inside a title unless they lead it, so a slug
# fallback does not produce "Dark Night Of Soul".
_TITLE_MINOR_WORDS: frozenset[str] = frozenset(
    {"a", "an", "and", "as", "at", "by", "for", "in", "of", "on", "or", "the", "to"}
)


def _display_name(slug: str) -> str:
    """Turn a filename stem into a readable title.

    This is a last-resort fallback. Every current knowledge file carries an H1,
    so the document's own title is used instead, and that title is canonical
    where this rule would only be a guess.

    Args:
        slug: The document's filename stem, in kebab case.

    Returns:
        A title-cased name with minor words kept lowercase.
    """
    words = slug.replace("-", " ").split()
    return " ".join(
        word.capitalize() if index == 0 or word not in _TITLE_MINOR_WORDS else word
        for index, word in enumerate(words)
    )


def _title_from_body(body: list[str]) -> str:
    for raw in body:
        match = _ATX_HEADING_RE.match(raw)
        if match and len(match.group(1)) == 1:
            return match.group(2).strip()
    return ""


# Doctrine priority-table name -> framework filename stem.
#
# This table is explicit rather than fuzzy-matched on purpose. The doctrine
# table orders safety modes, with Crisis highest, so a near-miss string match
# that silently mis-ranked a framework would be a safety-relevant bug in a
# place no test would obviously catch. Every entry below was verified against
# the file each detector in `src/soulmap/runtime/detectors/` actually loads.
#
# Names absent from this map are absent on purpose:
#   crisis, dependency, mirror   safety modes and the default posture, with no
#                                framework document of their own
#   soulmate longing,            live under `skills/soulmate/`, which the
#   partnership patterns         allowlist does not publish
_TIER_ALIASES: dict[str, str] = {
    "de-escalation / sanctuary": "emotional-deescalation",
    "de-escalation": "emotional-deescalation",
    "grief": "grief-companion",
    "existential": "existential-companion",
    "direction": "life-direction",
    "shadow": "shadow-patterns",
    "sacred polarity": "sacred-feminine-masculine",
    "integration and celebration": "integration-celebration",
    "synthesis": "conversation-synthesis",
    "pattern": "pattern-mapper",
    "dark night of the soul": "dark-night-of-soul",
    "fear of visibility": "fear-of-visibility",
}


def _match_tier(slug: str, tiers: dict[str, str]) -> str | None:
    """Look up a framework document's doctrine priority tier.

    Args:
        slug: The document's filename stem.
        tiers: Mapping from ``load_priority_tiers``.

    Returns:
        The tier, or None when the document has no row in the doctrine table.
        None is a real answer, not a failure: several framework documents are
        topic lenses applied after a primary framework rather than routed
        primaries, and the build reports the rest as gaps.
    """
    for table_name, tier in tiers.items():
        if _TIER_ALIASES.get(table_name, table_name.replace(" ", "-")) == slug:
            return tier
    return None


def build_page(
    path: Path,
    repo_root: Path,
    tiers: dict[str, str],
    *,
    category: str,
) -> PublicPage:
    """Build one public page model from a canonical Markdown file.

    Internal sections are dropped here, before rendering, so they never enter
    the model a template can see.

    Args:
        path: The canonical source file.
        repo_root: Repository root, used for the source path.
        tiers: Priority tiers from ``load_priority_tiers``.
        category: The page's category, for example ``"frameworks"``.

    Returns:
        The page model.

    Raises:
        OSError: If the file cannot be read.
    """
    front, body = _split_front_matter(path.read_text(encoding="utf-8"))
    slug = path.stem
    name = front.get("name", "").strip() or _title_from_body(body) or slug
    if name == slug:
        # Front matter carries the kebab-case identifier rather than a display
        # name, so fall back to the document's own H1 before inventing one.
        name = _title_from_body(body) or _display_name(slug)

    renderer = _markdown_renderer()
    sections: list[PublicSection] = []
    for level, heading, lines in _drop_internal_blocks(_iter_blocks(body)):
        text = _delink_private_targets(
            "\n".join(_scrub_labelled_signals(lines)).strip()
        )
        if not text and not heading:
            continue
        sections.append(
            PublicSection(
                heading=heading,
                level=level or 2,
                anchor=slugify_github_anchor(heading) if heading else "",
                html=renderer.render(text) if text else "",
            )
        )

    return PublicPage(
        slug=slug,
        name=name,
        description=front.get("description", "").strip(),
        category=category,
        tier=_match_tier(slug, tiers) if category == "frameworks" else None,
        sections=tuple(sections),
        source_path=path.relative_to(repo_root).as_posix(),
    )


def load_public_pages(repo_root: Path) -> list[PublicPage]:
    """Load every allowlisted document as a public page model.

    Args:
        repo_root: Repository root.

    Returns:
        Page models in category then slug order. Documents that the allowlist
        does not name are never opened.

    Raises:
        OSError: If an allowlisted file cannot be read.
    """
    tiers = load_priority_tiers(repo_root)
    skills_root = repo_root / "skills"
    pages: list[PublicPage] = []

    for category_dir in sorted(skills_root.iterdir()):
        if not category_dir.is_dir():
            continue
        category = category_dir.name
        for path in sorted(category_dir.glob("*.md")):
            if not is_public_skill(category, path.name):
                continue
            pages.append(build_page(path, repo_root, tiers, category=category))

    return pages
