from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

from markdown_it import MarkdownIt

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

_FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")
_ATX_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_MD_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
_MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_UNSAFE_MD_LINK_RE = re.compile(
    r"(?<!!)\[([^\]]+)\]\(\s*((?:javascript|data|file):[^)\s]+)",
    re.IGNORECASE,
)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_MARKDOWN_PARSER = MarkdownIt("commonmark")


@dataclass(frozen=True)
class MarkdownReference:
    line: int
    label: str
    target: str
    is_image: bool = False


@dataclass(frozen=True)
class MarkdownHeadingAnchor:
    slug: str
    title: str
    line: int


class FenceTracker:
    """Track fenced-code-block state across lines using CommonMark fence rules.

    A fence only closes on a line whose marker uses the same character as the
    opening fence and a run length greater than or equal to it. A naive
    "any 3+ backtick or tilde run toggles the state" check would desync on a
    four-backtick fence wrapping a three-backtick example, so this tracks the
    opening marker's character and length instead of a bare boolean toggle.
    """

    def __init__(self) -> None:
        self._marker_char: str | None = None
        self._marker_len = 0

    @property
    def in_fence(self) -> bool:
        return self._marker_char is not None

    def consume(self, raw: str) -> bool:
        """Update state for one line. Return True if callers should treat
        this line as fence delimiter/content and skip other line checks."""
        match = _FENCE_RE.match(raw)
        if self._marker_char is None:
            if not match:
                return False
            run = match.group(2)
            self._marker_char = run[0]
            self._marker_len = len(run)
            return True
        if (
            match
            and match.group(2)[0] == self._marker_char
            and len(match.group(2)) >= self._marker_len
        ):
            self._marker_char = None
            self._marker_len = 0
            return True
        return True


def iter_markdown_files(repo_root: Path) -> list[Path]:
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


def resolve_markdown_inputs(
    repo_root: Path, inputs: list[str] | None = None
) -> list[Path]:
    if not inputs:
        return iter_markdown_files(repo_root)

    md_files: list[Path] = []
    seen_resolved: set[Path] = set()
    for raw in inputs:
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = (repo_root / candidate).resolve()
        else:
            candidate = candidate.resolve()

        if candidate.is_dir():
            for path in iter_markdown_files(candidate):
                resolved = path.resolve()
                if resolved not in seen_resolved:
                    seen_resolved.add(resolved)
                    md_files.append(path)
            continue

        if (
            candidate.is_file()
            and candidate.suffix.lower() == ".md"
            and candidate not in seen_resolved
        ):
            seen_resolved.add(candidate)
            md_files.append(candidate)

    return sorted(md_files)


def parse_yaml_front_matter(lines: list[str]) -> dict[str, str] | None:
    """Parse a minimal YAML front matter block.

    We intentionally avoid external YAML deps. This is a strict subset:
    - Must start at BOF with '---'
    - Must end with the next line that is exactly '---'
    - Only supports simple 'key: value' pairs (value may be quoted)
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
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _HTML_TAG_RE.sub("", text)
    text = text.replace("`", "")
    text = text.replace("*", "")
    text = text.replace("_", "")
    text = text.replace("~", "")
    return " ".join(text.split())


def slugify_github_anchor(text: str) -> str:
    text = strip_inline_markup(text).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "section"


def extract_heading_anchors(lines: list[str]) -> list[MarkdownHeadingAnchor]:
    anchors: list[MarkdownHeadingAnchor] = []
    counts: dict[str, int] = {}
    fence = FenceTracker()

    for line_no, raw in enumerate(lines, start=1):
        if fence.consume(raw):
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
    cleaned = target.strip().strip("<>").strip()
    if "#" in cleaned and not cleaned.startswith("#"):
        path, frag = cleaned.split("#", 1)
        return path, frag or None
    if cleaned.startswith("#"):
        return "", cleaned[1:] or None
    return cleaned, None


def is_external_markdown_target(target: str) -> bool:
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


def iter_disallowed_markdown_references(
    lines: list[str],
) -> list[MarkdownReference]:
    """Find unsafe Markdown destinations that parsers intentionally discard."""
    references: list[MarkdownReference] = []
    fence = FenceTracker()

    for line_no, raw in enumerate(lines, start=1):
        if fence.consume(raw):
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

    for block_token in _MARKDOWN_PARSER.parse(source):
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
    fence = FenceTracker()
    for line_no, raw in enumerate(lines, start=1):
        if fence.consume(raw):
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


def resolve_local_markdown_target(
    *,
    repo_root: Path,
    current_file: Path,
    target_path: str,
) -> Path:
    raw = unquote(target_path.strip().strip("<>").strip())
    if not raw:
        return current_file.resolve()

    if raw.startswith("/"):
        candidate = repo_root / raw.lstrip("/")
    else:
        candidate = current_file.parent / raw

    return candidate.resolve()
