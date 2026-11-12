"""Markdown parsing helpers shared by the repository checkers.

Centralizes file discovery, front-matter parsing, GitHub anchor slugging, and
reference extraction so the link checker, case checker, and contract validators
all read Markdown the same way.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote

from soulmap.runtime.io.markdown import (
    FenceTracker,
    MarkdownHeadingAnchor,
    MarkdownReference,
    extract_heading_anchors,
    is_external_markdown_target,
    iter_disallowed_markdown_references,
    iter_markdown_files,
    iter_markdown_references,
    parse_yaml_front_matter,
    slugify_github_anchor,
    split_markdown_link_target,
    strip_inline_markup,
)

def resolve_markdown_inputs(
    repo_root: Path, inputs: list[str] | None = None
) -> list[Path]:
    """Turn command-line path arguments into a Markdown file list.

    Args:
        repo_root: Repository root, used to resolve relative inputs and as the
            search root when no inputs are given.
        inputs: Files or directories to check. Empty or None means the whole
            repository.

    Returns:
        Sorted Markdown file paths. Directory inputs expand recursively, and
        non-Markdown or missing paths are dropped rather than raising, so a
        caller can pass a mixed changed-file list straight through.
    """
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

def resolve_local_markdown_target(
    *,
    repo_root: Path,
    current_file: Path,
    target_path: str,
) -> Path:
    """Resolve a local link destination to a filesystem path.

    Args:
        repo_root: Repository root, which root-relative destinations resolve
            against.
        current_file: File holding the link, which relative destinations
            resolve against.
        target_path: Link destination as written, percent-encoding included.

    Returns:
        The resolved path. An empty destination, meaning a same-file anchor,
        resolves to ``current_file``. The path is not checked for existence.
    """
    raw = unquote(target_path.strip().strip("<>").strip())
    if not raw:
        return current_file.resolve()

    if raw.startswith("/"):
        candidate = repo_root / raw.lstrip("/")
    else:
        candidate = current_file.parent / raw

    return candidate.resolve()
