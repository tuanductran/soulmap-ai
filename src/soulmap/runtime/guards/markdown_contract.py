"""Lightweight GitHub-flavored Markdown contract checks (no external deps).

This module is intentionally conservative: it checks for issues that commonly break
rendering or navigation on GitHub (bad headings, unclosed fences, broken links).
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from soulmap.devtools.support.markdown import (
    extract_heading_anchors,
    is_external_markdown_target,
    iter_disallowed_markdown_references,
    iter_markdown_files,
    iter_markdown_references,
    parse_yaml_front_matter,
    split_markdown_link_target,
)

_FENCE_RE = re.compile(r"^(\s*)(```|~~~)")
_ATX_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
# Flags headings like `##Title` (missing required whitespace after the heading marker).
_BAD_ATX_HEADING_RE = re.compile(r"^#{1,6}(?![ \t#])")
# Disallow headings like `## 1) Foo` or `## 1. Foo` to keep anchors stable and avoid
# tool-specific numbering conventions in the knowledge base.
_NUMBERED_HEADING_PREFIX_RE = re.compile(r"^\(?\d+\)?\s*[.)]\s+")
_PACKAGE_VERSION_RE = re.compile(r'^version\s*=\s*["\']([^"\']+)["\']\s*$')
_INTEGRATION_METADATA = ("title", "description", "doctrine_source", "soulmap_version")
_INTEGRATION_DOCTRINE_SOURCE = "AGENTS.md"
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


@dataclass(frozen=True)
class Issue:
    path: Path
    line: int
    message: str


def _iter_markdown_files(root: Path) -> list[Path]:
    return iter_markdown_files(root)


def _package_version(repo_root: Path) -> str | None:
    """Return the repository package version without adding a TOML dependency."""
    pyproject = repo_root / "pyproject.toml"
    if not pyproject.is_file():
        return None
    for raw in pyproject.read_text(encoding="utf-8").splitlines():
        match = _PACKAGE_VERSION_RE.match(raw.strip())
        if match:
            return match.group(1)
    return None


def _is_integration_guide(rel: Path) -> bool:
    return rel.parts[:2] == ("docs", "integrations")


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
    #   - `SKILL.md` and `skills/**.md` require the shipped skill contract.
    #   - `docs/integrations/**.md` declares its canonical doctrine source and
    #     exact package compatibility so release drift is checked locally.
    is_skill_document = rel.as_posix() == "SKILL.md" or (
        rel.parts and rel.parts[0] == "skills"
    )
    is_integration_guide = _is_integration_guide(rel)
    if is_skill_document or is_integration_guide:
        meta = parse_yaml_front_matter(lines[:50])
        if is_skill_document and (
            not meta or not meta.get("name") or not meta.get("description")
        ):
            issues.append(
                Issue(
                    path,
                    1,
                    "Missing YAML front matter metadata (--- name: ... description: ... ---)",
                )
            )
        if is_integration_guide:
            for key in _INTEGRATION_METADATA:
                if not meta or not meta.get(key):
                    issues.append(
                        Issue(path, 1, f"Missing integration metadata: {key}")
                    )
            if meta and meta.get("doctrine_source") != _INTEGRATION_DOCTRINE_SOURCE:
                issues.append(
                    Issue(
                        path,
                        1,
                        "Integration doctrine_source must be AGENTS.md",
                    )
                )
            expected_version = _package_version(repo_root)
            actual_version = meta.get("soulmap_version") if meta else None
            if (
                expected_version
                and actual_version
                and actual_version != expected_version
            ):
                issues.append(
                    Issue(
                        path,
                        1,
                        "Integration soulmap_version must match pyproject.toml "
                        f"version (expected {expected_version}, got {actual_version})",
                    )
                )

    # 0) Portability: disallow typography characters that can confuse tools or break diffs.
    for i, raw in enumerate(lines, start=1):
        for ch, desc in _BANNED_UNICODE.items():
            if ch in raw:
                issues.append(Issue(path, i, f"Banned Unicode character: {desc}"))

    # 1) Heading correctness: require a space after ATX heading marker.
    in_fence = False
    for i, raw in enumerate(lines, start=1):
        if _FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if _BAD_ATX_HEADING_RE.match(raw):
            issues.append(Issue(path, i, "ATX heading missing a space after '#'"))

    # 1a) Heading numbering: disallow numeric prefixes like `1)` / `1.` in headings.
    #     Guard against false positives inside fenced code blocks (e.g. bash comments
    #     like `# 1. do something` would otherwise be flagged as headings).
    in_fence = False
    for i, raw in enumerate(lines, start=1):
        if _FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
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

    # 2c) HTML comments must be balanced (skip inside fenced code blocks).
    in_fence = False
    opens = 0
    closes = 0
    for raw in lines:
        if _FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        opens += raw.count("<!--")
        closes += raw.count("-->")
    if opens != closes:
        issues.append(
            Issue(
                path,
                1,
                f"Unbalanced HTML comment markers (<!--: {opens}, -->: {closes})",
            )
        )

    # 2d) Images should have non-empty alt text for accessibility.
    for reference in iter_markdown_references(lines):
        if reference.is_image and not reference.label.strip():
            issues.append(
                Issue(
                    path,
                    reference.line,
                    f"Image missing alt text: {reference.target.strip()}",
                )
            )

    # 2b) Ordered lists: require sequential numbering (`1. 2. 3.`) so repo tooling
    # and rendered Markdown stay aligned. Repeated `1.` markers are intentionally
    # rejected in this project.
    ordered_re = re.compile(r"^(\s*)(\d+)\.\s+\S")
    in_fence = False
    prev_indent: str | None = None
    prev_num: int | None = None
    prev_line_was_item = False
    for i, raw in enumerate(lines, start=1):
        if _FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        match = ordered_re.match(raw)
        if not match:
            if raw.strip() == "":
                continue

            if (
                prev_line_was_item
                and prev_indent is not None
                and raw.startswith(f"{prev_indent}   ")
            ):
                continue

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
                        f"Ordered list numbering should stay sequential (expected {expected}., got {num}.)",
                    )
                )
        elif num != 1:
            issues.append(
                Issue(
                    path,
                    i,
                    "Ordered lists must start at 1.",
                )
            )

        prev_indent = indent
        prev_num = num
        prev_line_was_item = True

    # 3) Internal anchor links should resolve to a heading-generated anchor.
    anchors = {anchor.slug for anchor in extract_heading_anchors(lines)}

    # 4) Relative file links should exist, and file+anchor links should resolve.
    for reference in iter_disallowed_markdown_references(lines):
        issues.append(Issue(path, reference.line, "Disallowed link scheme"))

    for reference in iter_markdown_references(lines):
        if reference.is_image:
            continue
        i = reference.line
        target = reference.target.strip()
        if not target or is_external_markdown_target(target):
            continue
        if target.startswith(("javascript:", "data:")):
            issues.append(Issue(path, i, "Disallowed link scheme"))
            continue

        file_part, frag = split_markdown_link_target(target)
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
            other_anchors = {
                anchor.slug for anchor in extract_heading_anchors(other_lines)
            }
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
