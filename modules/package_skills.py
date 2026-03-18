"""Bundle skill markdown files into a generated AGENTS document."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


def _load_ignore_patterns(ignore_file: Path) -> list[str]:
    if not ignore_file.is_file():
        return []

    patterns: list[str] = []
    for raw in ignore_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _is_ignored(relative_path: Path, patterns: list[str]) -> bool:
    rel = relative_path.as_posix()
    return any(Path(rel).match(p) for p in patterns)


def _write_source_log_line(log_file: Path, rel: Path, content: str) -> None:
    sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
    entry = {
        "path": rel.as_posix(),
        "bytes": len(content.encode("utf-8")),
        "sha256": sha256,
    }
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


_FENCE_RE = re.compile(r"^(\s*)(```|~~~)")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def _demote_headings(markdown: str, *, by: int = 1) -> str:
    """Increase ATX heading depth by `by` outside fenced code blocks."""
    if by <= 0:
        return markdown.rstrip() + "\n"

    lines: list[str] = []
    in_fence = False

    for raw in markdown.splitlines():
        fence = _FENCE_RE.match(raw)
        if fence:
            in_fence = not in_fence
            lines.append(raw)
            continue

        if in_fence:
            lines.append(raw)
            continue

        match = _HEADING_RE.match(raw)
        if not match:
            lines.append(raw)
            continue

        hashes, title = match.groups()
        new_level = min(6, len(hashes) + by)
        lines.append("#" * new_level + " " + title.strip())

    return "\n".join(lines).rstrip() + "\n"


def _extract_headings(markdown: str) -> list[tuple[int, str]]:
    """Extract ATX headings outside fenced code blocks."""
    headings: list[tuple[int, str]] = []
    in_fence = False

    for raw in markdown.splitlines():
        fence = _FENCE_RE.match(raw)
        if fence:
            in_fence = not in_fence
            continue

        if in_fence:
            continue

        match = _HEADING_RE.match(raw)
        if match:
            hashes, title = match.groups()
            headings.append((len(hashes), title.strip()))

    return headings


def _slugify_github(text: str) -> str:
    """Approximate GitHub-style heading anchors."""
    slug = text.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "section"


def _build_toc(headings: list[tuple[int, str]], *, min_level: int = 2) -> str:
    if not headings:
        return ""

    used: dict[str, int] = {}
    out: list[str] = []

    for level, title in headings:
        if level < min_level:
            continue
        indent = "  " * (level - min_level)
        base = _slugify_github(title)
        count = used.get(base, 0)
        used[base] = count + 1
        anchor = base if count == 0 else f"{base}-{count}"
        out.append(f"{indent}- [{title}](#{anchor})")

    return "\n".join(out).rstrip() + "\n"


def _agents_preamble(toc_markdown: str) -> str:
    toc_body = toc_markdown.strip()
    if not toc_body:
        toc_body = "_(No headings found.)_"

    return (
        "# AGENTS.md\n"
        "\n"
        "This file is an auto-generated bundle of the SoulMap AI knowledge base Markdown.\n"
        "\n"
        "## Table of contents\n"
        "\n"
        f"{toc_body}\n"
        "\n"
        "---\n"
        "\n"
    )


def package_skills_to_markdown(
    skills_dir: str | Path,
    output_file: str | Path,
    ignore_file: str | Path | None = None,
    log_file: str | Path | None = None,
) -> Path:
    """Concatenates all markdown files from a given directory into a single markdown file.

    Args:
        skills_dir: The path to the directory containing markdown files.
        output_file: The path to the output markdown file (e.g., 'AGENTS.md').
    """
    skills_path = Path(skills_dir)
    output_path = Path(output_file)
    ignore_patterns = (
        _load_ignore_patterns(Path(ignore_file)) if ignore_file is not None else []
    )
    log_path = Path(log_file) if log_file is not None else None

    if not skills_path.is_dir():
        raise FileNotFoundError(f"Directory not found at '{skills_path}'")

    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if log_path.exists():
            log_path.unlink()

    print(f"Creating '{output_path}'...")

    sources: list[tuple[Path, str]] = []
    for filepath in sorted(
        skills_path.rglob("*.md"),
        key=lambda path: str(path.relative_to(skills_path)).lower(),
    ):
        if filepath.resolve() == output_path.resolve():
            continue

        rel = filepath.relative_to(skills_path)
        if _is_ignored(rel, ignore_patterns):
            continue

        content = filepath.read_text(encoding="utf-8").rstrip() + "\n"
        if log_path is not None:
            _write_source_log_line(log_path, rel, content)
        print(f"  - Appended '{rel.as_posix()}'")
        sources.append((rel, content))

    demoted_chunks: list[str] = []
    headings: list[tuple[int, str]] = []

    for _rel, content in sources:
        demoted = _demote_headings(content, by=1)
        demoted_chunks.append(demoted.strip() + "\n")
        headings.extend(_extract_headings(demoted))

    toc = _build_toc(headings, min_level=2)
    preamble = _agents_preamble(toc)

    with output_path.open("w", encoding="utf-8") as outfile:
        outfile.write(preamble)
        # Ensure stable spacing between concatenated files so headings never run together.
        outfile.write("\n\n".join(demoted_chunks).rstrip() + "\n")

    print(f"Successfully packaged all markdown files into '{output_path}'.")
    return output_path


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    skills_directory = project_root / "skills"
    output_markdown_file = skills_directory / "AGENTS.md"
    ignore_file = project_root / ".skillsignore"
    log_file = skills_directory / "AGENTS.sources.jsonl"

    package_skills_to_markdown(
        skills_directory,
        output_markdown_file,
        ignore_file=ignore_file,
        log_file=log_file,
    )


if __name__ == "__main__":
    main()
