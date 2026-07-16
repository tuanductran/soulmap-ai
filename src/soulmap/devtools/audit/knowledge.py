from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.knowledge.consistency import (
    KnowledgeDuplicate,
    find_python_markdown_duplicates,
)


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="soulmap audit-knowledge")
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Repo root (default: SoulMap repository root).",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    duplicates = find_python_markdown_duplicates(root)
    print(_format_inventory(duplicates, root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
