"""Check for duplicated knowledge between Python config and Markdown."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

_QUOTED_RE = re.compile(r'"([^"]+)"')


@dataclass(frozen=True, slots=True)
class KnowledgeDuplicate:
    """A phrase defined in Python config and Markdown knowledge."""

    phrase: str
    python_path: Path
    constant: str
    markdown_path: Path


def _string_values(node: ast.AST) -> tuple[str, ...]:
    if not isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return ()

    values: list[str] = []
    for item in node.elts:
        if isinstance(item, ast.Constant) and isinstance(item.value, str):
            values.append(item.value.lower())
    return tuple(values)


def _python_knowledge(path: Path) -> dict[str, tuple[str, ...]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    knowledge: dict[str, tuple[str, ...]] = {}

    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign) and node.target is not None:
            targets = (node.target,)
            value = node.value
        else:
            continue

        if value is None:
            continue
        values = _string_values(value)
        if not values:
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                knowledge[target.id] = values

    return knowledge


def _markdown_phrases(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return {phrase.lower() for phrase in _QUOTED_RE.findall(text)}


def find_python_markdown_duplicates(
    root: Path,
    *,
    python_root: Path = Path("src/soulmap/runtime/config"),
    markdown_roots: tuple[Path, ...] = (Path("skills"), Path("templates")),
) -> tuple[KnowledgeDuplicate, ...]:
    """Find exact phrase duplicates between Python config and Markdown.

    This is a diagnostic check only. It does not decide ownership or mutate files.
    """
    python_files = sorted((root / python_root).glob("*.py"))
    markdown_files = sorted(
        path
        for markdown_root in markdown_roots
        for path in (root / markdown_root).rglob("*.md")
    )

    markdown_index: dict[str, tuple[Path, ...]] = {}
    for path in markdown_files:
        for phrase in _markdown_phrases(path):
            markdown_index.setdefault(phrase, ())
            markdown_index[phrase] += (path,)

    duplicates: list[KnowledgeDuplicate] = []
    for python_path in python_files:
        for constant, phrases in _python_knowledge(python_path).items():
            for phrase in phrases:
                for markdown_path in markdown_index.get(phrase, ()):
                    duplicates.append(
                        KnowledgeDuplicate(
                            phrase=phrase,
                            python_path=python_path,
                            constant=constant,
                            markdown_path=markdown_path,
                        )
                    )

    return tuple(duplicates)
