"""Reusable, runtime-owned Markdown parsing primitives."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

from markdown_it import MarkdownIt

_FENCE_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
_ATX_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_MD_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
_MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_UNSAFE_MD_LINK_RE = re.compile(
    r"(?<!!)\[([^\]]+)\]\(\s*((?:javascript|data|file):[^)\s]+)",
    re.IGNORECASE,
)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_MARKDOWN_PARSER = MarkdownIt("commonmark")

_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "dist",
    "node_modules",
    ".ruff_cache",
    ".pytest_cache",
    ".cache",
    ".npm",
    ".yarn",
    ".pnpm-store",
}


@dataclass(frozen=True)
class MarkdownReference:
    """One Markdown link or image found in a file.

    Attributes:
        line: 1-indexed line the reference was found on.
        label: Link text, or alt text for an image.
        target: Destination exactly as written in the source, before any
            resolution, so an error message can quote what the author typed.
        is_image: True for an image reference, False for a link.
    """

    line: int
    label: str
    target: str
    is_image: bool = False


@dataclass(frozen=True)
class MarkdownHeadingAnchor:
    """One heading and the anchor GitHub will generate for it.

    Attributes:
        slug: Anchor slug, with GitHub's numeric suffix already applied when an
            earlier heading in the file produced the same slug.
        title: Heading text as written, including any inline markup.
        line: 1-indexed line the heading is on.
    """

    slug: str
    title: str
    line: int


class FenceTracker:
    """Track a top-level fenced-code-block state across lines.

    A fence only closes on a line whose marker uses the same character as the
    opening fence and a run length greater than or equal to it. A naive
    "any 3+ backtick or tilde run toggles the state" check would desync on a
    four-backtick fence wrapping a three-backtick example, so this tracks the
    opening marker's character and length instead of a bare boolean toggle.
    Use :func:`markdown_code_block_lines` for complete documents with nested
    list or block-quote containers.
    """

    def __init__(self) -> None:
        """Start outside any fence."""
        self._marker_char: str | None = None
        self._marker_len = 0

    @property
    def in_fence(self) -> bool:
        """bool: Whether the tracker is currently inside a fenced block."""
        return self._marker_char is not None

    def consume(self, raw: str) -> bool:
        """Update fence state for one line.

        Args:
            raw: The line exactly as it appears in the file.

        Returns:
            True when the caller should treat this line as fence delimiter or
            fenced content and skip its other line checks. False only for a
            line outside any fence.
        """
        line = raw.rstrip("\r\n")
        match = _FENCE_RE.match(line)
        if self._marker_char is None:
            if not match:
                return False
            run, info = match.group(2), match.group(3)
            # CommonMark forbids backticks in the info string of a backtick
            # fence. Such a line is not an opening fence at all.
            if run[0] == "`" and "`" in info:
                return False
            self._marker_char = run[0]
            self._marker_len = len(run)
            return True
        if (
            match
            and match.group(2)[0] == self._marker_char
            and len(match.group(2)) >= self._marker_len
            and not match.group(3).strip(" \t")
        ):
            self._marker_char = None
            self._marker_len = 0
            return True
        return True


def iter_markdown_files(repo_root: Path) -> list[Path]:
    """Collect every Markdown file under a directory.

    Skips version-control, virtual-environment, build, and package-cache
    directories, and deduplicates paths that resolve to the same file through
    a symlink.

    Args:
        repo_root: Directory to search recursively.

    Returns:
        Sorted Markdown file paths, as found rather than resolved.
    """
    md_files: list[Path] = []
    seen_resolved: set[Path] = set()
    for path in repo_root.rglob("*.md"):
        parts = set(path.parts)
        if parts & _EXCLUDED_DIRS:
            continue
        resolved = path.resolve()
        if resolved in seen_resolved:
            continue
        seen_resolved.add(resolved)
        md_files.append(path)
    return sorted(md_files)


def parse_yaml_front_matter(lines: list[str]) -> dict[str, str] | None:
    """Parse a minimal YAML front-matter block.

    Deliberately avoids an external YAML dependency and supports only the
    strict subset the repository's front matter uses: the block must open on
    the first line with ``---``, close on the next line that is exactly
    ``---``, and hold simple ``key: value`` pairs whose value may be quoted.
    Blank lines and comment lines inside the block are skipped.

    Args:
        lines: The file's lines, in order, starting at the first line.

    Returns:
        The parsed key-value pairs, or None when the file has no front-matter
        block. An empty dict means the block is present but held no pairs.
    """
    if not lines or lines[0].strip() != "---":
        return None

    try:
        end_idx = lines[1:].index("---") + 1
    except ValueError:
        return None

    data: dict[str, str] = {}
    for raw in lines[1:end_idx]:
        if not raw.strip():
            continue
        if raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            data[key] = value
    return data


def strip_inline_markup(text: str) -> str:
    """Reduce a line of Markdown to its visible text.

    Replaces links with their label, drops HTML tags, removes code, emphasis,
    and strikethrough markers, and collapses runs of whitespace.

    Args:
        text: Markdown source text.

    Returns:
        The text a reader would see, without inline markup.
    """
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _HTML_TAG_RE.sub("", text)
    text = text.replace("`", "")
    text = text.replace("*", "")
    text = text.replace("_", "")
    text = text.replace("~", "")
    return " ".join(text.split())


def slugify_github_anchor(text: str) -> str:
    """Build the anchor slug GitHub generates for a heading.

    Lowercases the visible text, drops characters that are neither word
    characters, whitespace, nor hyphens, and joins the rest with single
    hyphens.

    Args:
        text: Heading text, which may still contain inline markup.

    Returns:
        The anchor slug, without a leading ``#``. Falls back to ``"section"``
        when the heading has no sluggable characters, matching what an
        anchor-less heading would otherwise collide on.
    """
    text = strip_inline_markup(text).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "section"


def extract_heading_anchors(lines: list[str]) -> list[MarkdownHeadingAnchor]:
    """List every ATX heading in a file with its generated anchor.

    Headings inside fenced code blocks are skipped. Repeated slugs get
    GitHub's numeric suffix, so the second heading slugging to ``notes``
    becomes ``notes-1``.

    Args:
        lines: The file's lines, in order.

    Returns:
        Anchors in document order.
    """
    anchors: list[MarkdownHeadingAnchor] = []
    counts: dict[str, int] = {}
    code_lines = markdown_code_block_lines(lines)

    for line_no, raw in enumerate(lines, start=1):
        if line_no in code_lines:
            continue

        match = _ATX_HEADING_RE.match(raw)
        if not match:
            continue

        _hashes, title = match.groups()
        base = slugify_github_anchor(title)
        duplicate_count = counts.get(base, 0)
        counts[base] = duplicate_count + 1
        slug = base if duplicate_count == 0 else f"{base}-{duplicate_count}"
        anchors.append(MarkdownHeadingAnchor(slug=slug, title=title, line=line_no))

    return anchors


def split_markdown_link_target(target: str) -> tuple[str, str | None]:
    """Split a link destination into its path and fragment.

    Args:
        target: Link destination as written, optionally wrapped in angle
            brackets.

    Returns:
        A ``(path, fragment)`` pair. The path is empty for a same-file anchor
        such as ``#section``, and the fragment is None when the destination
        carries no anchor or an empty one.
    """
    cleaned = target.strip().strip("<>").strip()
    if "#" in cleaned and not cleaned.startswith("#"):
        path, frag = cleaned.split("#", 1)
        return path, frag or None
    if cleaned.startswith("#"):
        return "", cleaned[1:] or None
    return cleaned, None


def is_external_markdown_target(target: str) -> bool:
    """Report whether a link destination points outside the repository.

    Args:
        target: Link destination as written.

    Returns:
        True for an ``http``, ``https``, ``mailto``, or ``tel`` destination,
        which the local link checker cannot resolve on disk.
    """
    lower = target.strip().strip("<>").lower()
    return lower.startswith(("http://", "https://", "mailto:", "tel:"))


def _token_attribute(token: object, name: str) -> str | None:
    attrs = getattr(token, "attrs", None)
    if not isinstance(attrs, dict):
        return None
    value = attrs.get(name)
    return value if isinstance(value, str) else None


def _inline_token_label(token: object) -> str:
    content = getattr(token, "content", "")
    return content if isinstance(content, str) else ""


def _reference_line(
    lines: list[str],
    *,
    label: str,
    is_image: bool,
    start_line: int,
) -> int:
    marker = f"![{label}]" if is_image else f"[{label}]"
    for line_no in range(max(start_line, 1), len(lines) + 1):
        if marker in lines[line_no - 1]:
            return line_no
    return start_line


def _raw_reference_target(
    lines: list[str],
    *,
    label: str,
    parsed_target: str,
    is_image: bool,
    start_line: int,
) -> str:
    marker = f"![{label}]" if is_image else f"[{label}]"
    for line_no in range(max(start_line, 1), len(lines) + 1):
        raw = lines[line_no - 1]
        start = raw.find(f"{marker}(")
        if start < 0:
            continue
        end = raw.find(")", start + len(marker) + 1)
        if end < 0:
            continue
        candidate = raw[start + len(marker) + 1 : end].strip()
        if unquote(candidate) == unquote(parsed_target):
            return candidate
    return parsed_target


def _markdown_source(lines: list[str]) -> str:
    if any(line.endswith(("\n", "\r")) for line in lines):
        return "".join(lines)
    return "\n".join(lines)


def _code_block_lines_from_tokens(tokens: Sequence[object]) -> frozenset[int]:
    """Return 1-indexed source lines covered by CommonMark code-block tokens."""
    code_lines: set[int] = set()
    for token in tokens:
        if getattr(token, "type", None) not in {"fence", "code_block"}:
            continue
        token_map = getattr(token, "map", None)
        if token_map:
            code_lines.update(range(int(token_map[0]) + 1, int(token_map[1]) + 1))
    return frozenset(code_lines)


def markdown_code_block_lines(lines: list[str]) -> frozenset[int]:
    """Return 1-indexed source lines inside CommonMark code blocks.

    Parser token maps account for container-relative indentation in lists
    and block quotes, unlike a line-only fence tracker.
    """
    tokens = _MARKDOWN_PARSER.parse(_markdown_source(lines))
    return _code_block_lines_from_tokens(tokens)


def _strip_blockquote_prefixes(line: str, container_level: int) -> tuple[int, str]:
    """Remove blockquote prefixes using the indentation of their containers."""
    quote_depth = 0
    while quote_depth < container_level:
        list_depth = max(0, (container_level - quote_depth) // 2)
        max_indent = 3 + (2 * list_depth)
        prefix = re.match(rf"^ {{0,{max_indent}}}>[ \t]?", line)
        if prefix is None:
            break
        quote_depth += 1
        line = line[prefix.end() :]
    return quote_depth, line


def markdown_unclosed_fence_lines(lines: list[str]) -> tuple[int, ...]:
    """Return opening lines for fenced code blocks without a CommonMark close.

    Token maps identify the complete container-relative block. The final mapped
    line is a closing fence only when its marker and blockquote depth match the
    opener and its indentation is valid for the surrounding list containers.
    """
    tokens = _MARKDOWN_PARSER.parse(_markdown_source(lines))
    unclosed: list[int] = []

    for token in tokens:
        if token.type != "fence" or token.map is None:
            continue

        opening_line = token.map[0]
        if token.map[1] <= opening_line + 1:
            unclosed.append(opening_line + 1)
            continue

        opening = lines[opening_line].rstrip("\r\n")
        closing = lines[token.map[1] - 1].rstrip("\r\n")
        quote_depth, _ = _strip_blockquote_prefixes(opening, token.level)
        closing_quote_depth, closing = _strip_blockquote_prefixes(
            closing, token.level
        )
        if closing_quote_depth != quote_depth:
            unclosed.append(opening_line + 1)
            continue

        list_depth = max(0, (token.level - quote_depth) // 2)
        max_indent = 3 + (2 * list_depth)
        marker = re.escape(token.markup[0])
        closing_pattern = rf" {{0,{max_indent}}}{marker}{{{len(token.markup)},}}[ \t]*"
        if re.fullmatch(closing_pattern, closing) is None:
            unclosed.append(opening_line + 1)

    return tuple(unclosed)


def markdown_without_code_blocks(text: str) -> str:
    """Blank CommonMark code-block lines while preserving source line numbers.

    Runtime knowledge parsers use regular expressions for semantic Markdown
    structures. Removing code-block content first prevents examples from
    masquerading as headings, bullets, groups, or tables.
    """
    lines = text.splitlines(keepends=True)
    code_lines = markdown_code_block_lines(lines)
    return "".join(
        "".join(char for char in line if char in "\r\n")
        if line_number in code_lines
        else line
        for line_number, line in enumerate(lines, start=1)
    )


def iter_disallowed_markdown_references(
    lines: list[str],
) -> list[MarkdownReference]:
    """Find unsafe Markdown destinations that parsers intentionally discard."""
    references: list[MarkdownReference] = []
    code_lines = markdown_code_block_lines(lines)

    for line_no, raw in enumerate(lines, start=1):
        if line_no in code_lines:
            continue
        for label, target in _UNSAFE_MD_LINK_RE.findall(raw):
            references.append(
                MarkdownReference(
                    line=line_no,
                    label=label,
                    target=target,
                )
            )

    return references


def iter_markdown_references(lines: list[str]) -> list[MarkdownReference]:
    """Extract parsed Markdown links and images outside code blocks.

    The repository keeps its own reference dataclass and policy checks, while
    ``markdown-it-py`` handles CommonMark edge cases such as reference links,
    nested destinations, link titles, autolinks, and inline markup. HTML links
    remain outside this helper's scope because they are not Markdown references.
    """
    references: list[MarkdownReference] = []
    source = _markdown_source(lines)

    block_tokens = _MARKDOWN_PARSER.parse(source)
    code_lines = _code_block_lines_from_tokens(block_tokens)

    for block_token in block_tokens:
        if getattr(block_token, "type", None) != "inline":
            continue
        children = getattr(block_token, "children", None) or []
        token_map = getattr(block_token, "map", None)
        block_line = int(token_map[0]) + 1 if token_map else 1
        open_link: dict[str, str] | None = None

        for token in children:
            token_type = getattr(token, "type", None)
            if token_type == "link_open":
                open_link = {
                    "label": "",
                    "target": _token_attribute(token, "href") or "",
                }
                continue

            if token_type == "link_close":
                if open_link is not None:
                    references.append(
                        MarkdownReference(
                            line=_reference_line(
                                lines,
                                label=open_link["label"],
                                is_image=False,
                                start_line=block_line,
                            ),
                            label=open_link["label"],
                            target=_raw_reference_target(
                                lines,
                                label=open_link["label"],
                                parsed_target=open_link["target"],
                                is_image=False,
                                start_line=block_line,
                            ),
                        )
                    )
                open_link = None
                continue

            if token_type == "image":
                references.append(
                    MarkdownReference(
                        line=_reference_line(
                            lines,
                            label=_inline_token_label(token),
                            is_image=True,
                            start_line=block_line,
                        ),
                        label=_inline_token_label(token),
                        target=_token_attribute(token, "src") or "",
                        is_image=True,
                    )
                )
                continue

            if (
                open_link is not None
                and isinstance(token_type, str)
                and not token_type.endswith(("_open", "_close"))
            ):
                open_link["label"] += _inline_token_label(token)

    known = {(ref.line, ref.label, ref.target, ref.is_image) for ref in references}
    for line_no, raw in enumerate(lines, start=1):
        if line_no in code_lines:
            continue
        for label, target in _MD_IMAGE_RE.findall(raw):
            if label.strip():
                continue
            reference = MarkdownReference(
                line=line_no,
                label=label,
                target=target.strip(),
                is_image=True,
            )
            key = (
                reference.line,
                reference.label,
                reference.target,
                reference.is_image,
            )
            if key not in known:
                references.append(reference)
                known.add(key)

    return references
