"""Knowledge-inventory audit.

Traces which Markdown knowledge files the runtime actually loads and reports
configuration constants no runtime module references any more. An orphaned
constant is a drift signal: either its consumer was removed, or the constant
should have been.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.knowledge.consistency import (
    ConfigUsage,
    KnowledgeDuplicate,
    find_config_usage,
    find_python_markdown_duplicates,
    markdown_consumers,
)

_IMPLEMENTATION_REFERENCE_PATTERNS = (
    re.compile(r"^\s*```(?:python|py)\s*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"(?:src/soulmap/|tests/)[^\s)]+\.py", re.IGNORECASE),
    re.compile(
        r"(^|\s)(?:from|import)\s+soulmap(?:\.|\s)", re.MULTILINE | re.IGNORECASE
    ),
    re.compile(
        r"\bPython\s+(?:runtime|code|implementation|source|modules?)\b", re.IGNORECASE
    ),
    re.compile(r"\bin\s+Python\b", re.IGNORECASE),
    re.compile(
        r"\b(?:runtime|implementation)\s+(?:code|module|details?|logic)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bruntime\s+(?:routing\s+)?modules?\b", re.IGNORECASE),
    re.compile(r"\bruntime\s+synthesizer\b", re.IGNORECASE),
    re.compile(r"\bnot\s+implemented\s+in\s+this\s+repository\b", re.IGNORECASE),
    re.compile(
        r"\b(?:implemented|implementation)\s+(?:in|by)\s+(?:this\s+repository|Python|code|module)\b",
        re.IGNORECASE,
    ),
)


def find_markdown_implementation_references(root: Path) -> tuple[Path, ...]:
    """Find shipped knowledge files coupled to implementation details."""
    findings: list[Path] = []
    roots = tuple(
        path
        for path in (root / "skills", root / "templates", root / "frameworks")
        if path.exists()
    )
    for knowledge_root in roots:
        for path in sorted(knowledge_root.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            if any(
                pattern.search(text) for pattern in _IMPLEMENTATION_REFERENCE_PATTERNS
            ):
                findings.append(path)
    return tuple(findings)


def _format_inventory(duplicates: tuple[KnowledgeDuplicate, ...], root: Path) -> str:
    grouped: dict[str, list[KnowledgeDuplicate]] = defaultdict(list)
    for duplicate in duplicates:
        grouped[duplicate.classification].append(duplicate)

    lines = [
        "Knowledge consistency inventory",
        f"total overlaps: {len(duplicates)}",
    ]

    for classification in sorted(grouped):
        entries = grouped[classification]
        lines.append(f"\n[{classification}] {len(entries)}")
        by_constant: dict[tuple[Path, str], list[KnowledgeDuplicate]] = defaultdict(
            list
        )
        for entry in entries:
            by_constant[(entry.python_path, entry.constant)].append(entry)

        for (python_path, constant), constant_entries in sorted(by_constant.items()):
            lines.append(f"  {python_path.relative_to(root)}::{constant}")
            ownership = {
                (entry.markdown_path, entry.markdown_section, entry.markdown_group)
                for entry in constant_entries
            }
            for markdown_path, section, group in sorted(ownership):
                lines.append(f"    ownership: {markdown_path.relative_to(root)}")
                lines.append(f"      section: {section} / {group}")
                consumers = markdown_consumers(root, markdown_path)
                if consumers:
                    for consumer in consumers:
                        lines.append(f"      loaded by: {consumer.relative_to(root)}")
                else:
                    lines.append("      loaded by: no runtime loader found")
            for entry in sorted(
                constant_entries,
                key=lambda item: (
                    item.markdown_path,
                    item.markdown_section,
                    item.phrase,
                ),
            ):
                markdown_path = entry.markdown_path.relative_to(root)
                lines.append(
                    f"    - {entry.phrase!r} -> {markdown_path} [{entry.markdown_section}]"
                )

    return "\n".join(lines)


def _format_usage(usage: tuple[ConfigUsage, ...], root: Path) -> str:
    active = tuple(item for item in usage if not item.is_orphaned)
    orphaned = tuple(item for item in usage if item.is_orphaned)
    lines = [
        "Config usage inventory",
        f"active constants: {len(active)}",
        f"orphaned constants: {len(orphaned)}",
    ]

    if active:
        lines.append("\n[active]")
        for item in active:
            lines.append(f"  {item.python_path.relative_to(root)}::{item.constant}")
            for path in item.referenced_from:
                lines.append(f"    - {path.relative_to(root)}")

    if orphaned:
        lines.append("\n[orphaned]")
        for item in orphaned:
            lines.append(f"  {item.python_path.relative_to(root)}::{item.constant}")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Run the knowledge audit from the command line.

    Args:
        argv: Command-line arguments, or None to read from ``sys.argv``.

    Returns:
        0 when the inventory is clean, 1 when an orphaned constant is found.
    """
    parser = argparse.ArgumentParser(prog="soulmap audit-knowledge")
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Repo root (default: SoulMap repository root).",
    )
    parser.add_argument(
        "--max-knowledge-duplicates",
        type=int,
        help="Fail when semantic knowledge duplicates exceed this threshold.",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    duplicates = find_python_markdown_duplicates(root)
    usage = find_config_usage(root)
    implementation_references = find_markdown_implementation_references(root)
    print(_format_inventory(duplicates, root))
    print(f"\n{_format_usage(usage, root)}")
    print("\nMarkdown implementation-reference audit")
    print(f"implementation references: {len(implementation_references)}")
    for path in implementation_references:
        print(f"  - {path.relative_to(root)}")
    if args.max_knowledge_duplicates is not None:
        duplicate_count = sum(
            duplicate.classification == "knowledge_duplicate"
            for duplicate in duplicates
        )
        if duplicate_count > args.max_knowledge_duplicates:
            print(
                "\nKnowledge migration guard failed: "
                f"{duplicate_count} knowledge duplicates exceed "
                f"{args.max_knowledge_duplicates}."
            )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

