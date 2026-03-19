"""Lightweight GitHub-flavored Markdown contract checks (no external deps).

This module is intentionally conservative: it checks for issues that commonly break
rendering or navigation on GitHub (bad headings, unclosed fences, broken links).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re

from tools._markdown import iter_markdown_files

_FENCE_RE = re.compile(r"^(\s*)(```|~~~)")
_ATX_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
# Flags headings like `##Title` (missing required whitespace after the heading marker).
_BAD_ATX_HEADING_RE = re.compile(r"^#{1,6}(?![ \t#])")
# Disallow headings like `## 1) Foo` or `## 1. Foo` to keep anchors stable and avoid
# tool-specific numbering conventions in the knowledge base.
_NUMBERED_HEADING_PREFIX_RE = re.compile(r"^\(?\d+\)?\s*[.)]\s+")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_BANNED_UNICODE = {
    "\u2019": "U+2019 RIGHT SINGLE QUOTATION MARK (use ASCII apostrophe ')",
    "\u2018": "U+2018 LEFT SINGLE QUOTATION MARK (use ASCII apostrophe ')",
    "\u201c": 'U+201C LEFT DOUBLE QUOTATION MARK (use ASCII quote ")',
    "\u201d": 'U+201D RIGHT DOUBLE QUOTATION MARK (use ASCII quote ")',
    "\u2014": "U+2014 EM DASH (use ASCII hyphen -)",
    "\u2013": "U+2013 EN DASH (use ASCII hyphen -)",
    "\u2026": "U+2026 HORIZONTAL ELLIPSIS (use three dots ...)",
    "\u00a0": "U+00A0 NO-BREAK SPACE (use regular space)",
}


def _parse_yaml_front_matter(lines: list[str]) -> dict[str, str] | None:
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


def _strip_inline_markup(text: str) -> str:
    # Approximate GitHub's "markup formatting is removed" rule for anchors.
    # Keep it simple and predictable rather than fully parsing Markdown.
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _HTML_TAG_RE.sub("", text)
    text = text.replace("`", "")
    text = text.replace("*", "")
    text = text.replace("_", "")
    text = text.replace("~", "")
    return " ".join(text.split())


def _slugify_github(text: str) -> str:
    """Approximate GitHub heading anchors.

    Rules (per GitHub docs, simplified):
    - lower-case
    - spaces -> hyphens
    - punctuation removed
    - markup removed (approx.)
    - duplicates get -1, -2, ...
    """

    text = _strip_inline_markup(text).strip().lower()
    # Remove punctuation but keep unicode letters/numbers, whitespace, and hyphens.
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "section"


def _split_link_target(target: str) -> tuple[str, str | None]:
    target = target.strip()
    if "#" in target and not target.startswith("#"):
        path, frag = target.split("#", 1)
        return path, frag or None
    if target.startswith("#"):
        return "", target[1:] or None
    return target, None


def _is_external_link(target: str) -> bool:
    lower = target.lower()
    return lower.startswith(("http://", "https://", "mailto:", "tel:"))


@dataclass(frozen=True)
class Issue:
    path: Path
    line: int
    message: str


def _iter_markdown_files(root: Path) -> list[Path]:
    return iter_markdown_files(root)


def _extract_anchors(lines: list[str]) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    in_fence = False

    for raw in lines:
        if _FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        match = _ATX_HEADING_RE.match(raw)
        if not match:
            continue

        _hashes, title = match.groups()
        base = _slugify_github(title)
        n = counts.get(base, 0)
        counts[base] = n + 1
        anchor = base if n == 0 else f"{base}-{n}"
        anchors.add(anchor)

    return anchors


def check_markdown_file(path: Path, repo_root: Path) -> list[Issue]:
    issues: list[Issue] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    rel = path.resolve().relative_to(repo_root.resolve())

    # - File naming: prefer kebab-case for Markdown files (no underscores).
    if "_" in path.name:
        issues.append(
            Issue(path, 1, "Markdown filename should not contain '_' (use '-')")
        )

    # - Metadata: important docs should start with YAML front matter metadata.
    #   - `SKILL.md`, `skills/**.md`, and `templates/**.md`.
    if rel.as_posix() == "SKILL.md" or (
        rel.parts and rel.parts[0] in {"skills", "templates"}
    ):
        meta = _parse_yaml_front_matter(lines[:50])
        if not meta or not meta.get("name") or not meta.get("description"):
            issues.append(
                Issue(
                    path,
                    1,
                    "Missing YAML front matter metadata (--- name: ... description: ... ---)",
                )
            )

    # 0) Portability: disallow typography characters that can confuse tools or break diffs.
    for i, raw in enumerate(lines, start=1):
        for ch, desc in _BANNED_UNICODE.items():
            if ch in raw:
                issues.append(Issue(path, i, f"Banned Unicode character: {desc}"))

    # 1) Heading correctness: require a space after ATX heading marker.
    for i, raw in enumerate(lines, start=1):
        if _BAD_ATX_HEADING_RE.match(raw):
            issues.append(Issue(path, i, "ATX heading missing a space after '#'"))

    # 1a) Heading numbering: disallow numeric prefixes like `1)` / `1.` in headings.
    for i, raw in enumerate(lines, start=1):
        match = _ATX_HEADING_RE.match(raw)
        if not match:
            continue
        _hashes, title = match.groups()
        if _NUMBERED_HEADING_PREFIX_RE.match(title.strip()):
            issues.append(
                Issue(
                    path,
                    i,
                    "Heading should not start with numeric prefix like '1)' or '1.'",
                )
            )

    # 1b) Heading spacing: require a blank line before/after headings (outside fences).
    in_fence = False
    for idx, raw in enumerate(lines):
        if _FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not raw.startswith("#"):
            continue

        # Blank line before (except at BOF).
        if idx > 0 and lines[idx - 1].strip() != "":
            issues.append(
                Issue(path, idx + 1, "Heading should be preceded by a blank line")
            )

        # Blank line after (except at EOF).
        if idx + 1 < len(lines) and lines[idx + 1].strip() != "":
            issues.append(
                Issue(path, idx + 1, "Heading should be followed by a blank line")
            )

    # 2) Fenced code blocks must be balanced.
    in_fence = False
    for _i, raw in enumerate(lines, start=1):
        if _FENCE_RE.match(raw):
            in_fence = not in_fence
    if in_fence:
        issues.append(Issue(path, len(lines) or 1, "Unclosed fenced code block"))

    # 2c) HTML comments must be balanced.
    joined = "\n".join(lines)
    opens = joined.count("<!--")
    closes = joined.count("-->")
    if opens != closes:
        issues.append(
            Issue(
                path,
                1,
                f"Unbalanced HTML comment markers (<!--: {opens}, -->: {closes})",
            )
        )

    # 2d) Images should have non-empty alt text for accessibility.
    for i, raw in enumerate(lines, start=1):
        for alt, target in _MD_IMAGE_RE.findall(raw):
            if not alt.strip():
                issues.append(
                    Issue(path, i, f"Image missing alt text: {target.strip()}")
                )

    # 2b) Ordered lists: prefer sequential numbering (1., 2., 3.) for readability.
    ordered_re = re.compile(r"^(\s*)(\d+)\.\s+\S")
    in_fence = False
    prev_indent: str | None = None
    prev_num: int | None = None
    prev_line_was_item = False

    for i, raw in enumerate(lines, start=1):
        if _FENCE_RE.match(raw):
            in_fence = not in_fence
            prev_indent = None
            prev_num = None
            prev_line_was_item = False
            continue
        if in_fence:
            continue

        match = ordered_re.match(raw)
        if not match:
            if raw.strip() == "":
                prev_indent = None
                prev_num = None
                prev_line_was_item = False
            continue

        indent, num_str = match.groups()
        num = int(num_str)

        if prev_line_was_item and prev_indent == indent and prev_num is not None:
            expected = prev_num + 1
            if num != expected:
                issues.append(
                    Issue(
                        path,
                        i,
                        f"Ordered list numbering should be sequential (expected {expected}., got {num}.)",
                    )
                )

        prev_indent = indent
        prev_num = num
        prev_line_was_item = True

    # 3) Internal anchor links should resolve to a heading-generated anchor.
    anchors = _extract_anchors(lines)

    # 4) Relative file links should exist, and file+anchor links should resolve.
    for i, raw in enumerate(lines, start=1):
        for _label, target in _MD_LINK_RE.findall(raw):
            target = target.strip()
            if not target or _is_external_link(target):
                continue
            if target.startswith(("javascript:", "data:")):
                issues.append(Issue(path, i, "Disallowed link scheme"))
                continue

            file_part, frag = _split_link_target(target)
            if file_part == "" and frag is not None:
                if frag not in anchors:
                    issues.append(Issue(path, i, f"Broken anchor link: #{frag}"))
                continue

            # Skip pure fragment in empty file_part case already handled above.
            resolved = (path.parent / file_part).resolve()
            try:
                resolved.relative_to(repo_root.resolve())
            except ValueError:
                issues.append(Issue(path, i, "Link escapes repo root"))
                continue

            if not resolved.exists():
                issues.append(Issue(path, i, f"Broken relative link: {file_part}"))
                continue

            if frag is not None and resolved.suffix.lower() == ".md":
                other_lines = resolved.read_text(encoding="utf-8").splitlines()
                other_anchors = _extract_anchors(other_lines)
                if frag not in other_anchors:
                    issues.append(
                        Issue(path, i, f"Broken cross-file anchor: {file_part}#{frag}")
                    )

    return issues


def check_repo(repo_root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for path in _iter_markdown_files(repo_root):
        issues.extend(check_markdown_file(path, repo_root))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check Markdown contract for this repo."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repo root (default: current directory).",
    )
    args = parser.parse_args(argv)

    repo_root = args.root.resolve()
    issues = check_repo(repo_root)
    if not issues:
        return 0

    for issue in issues:
        rel = issue.path.resolve().relative_to(repo_root)
        print(f"{rel}:{issue.line}: {issue.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
