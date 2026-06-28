from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

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

_FENCE_RE = re.compile(r"^(\s*)(```|~~~)")
_ATX_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_MD_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
_MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_HTML_TAG_RE = re.compile(r"<[^>]+>")


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
    in_fence = False

    for line_no, raw in enumerate(lines, start=1):
        if _FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
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


def iter_markdown_references(lines: list[str]) -> list[MarkdownReference]:
    references: list[MarkdownReference] = []
    in_fence = False

    for line_no, raw in enumerate(lines, start=1):
        if _FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        for label, target in _MD_IMAGE_RE.findall(raw):
            references.append(
                MarkdownReference(
                    line=line_no,
                    label=label,
                    target=target,
                    is_image=True,
                )
            )

        for label, target in _MD_LINK_RE.findall(raw):
            references.append(
                MarkdownReference(
                    line=line_no,
                    label=label,
                    target=target,
                    is_image=False,
                )
            )

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
