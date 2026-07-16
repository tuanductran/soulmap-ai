"""Audit duplicated knowledge between Python config and Markdown sources."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

_BULLET_RE = re.compile(r"^\s*[-*+]\s+(?:`([^`]+)`|\"([^\"]+)\"|'([^']+)'|(.+?))\s*$")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


@dataclass(frozen=True, slots=True)
class KnowledgeDuplicate:
    """A Python config phrase that also exists in Markdown knowledge."""

    phrase: str
    python_path: Path
    constant: str
    markdown_path: Path
    markdown_section: str
    source_kind: str
    classification: str


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


def _markdown_knowledge(path: Path) -> dict[str, tuple[str, str]]:
    """Extract list knowledge with its Markdown section and source type."""
    section = ""
    source_kind = "pattern_framework" if path.name == "pattern-mapper.md" else "markdown"
    knowledge: dict[str, tuple[str, str]] = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        heading = _HEADING_RE.match(line)
        if heading:
            section = heading.group(2)
            continue

        bullet = _BULLET_RE.match(line)
        if bullet and section:
            phrase = next(value for value in bullet.groups() if value is not None)
            normalized = phrase.strip().lower()
            if normalized:
                knowledge[normalized] = (section, source_kind)

    return knowledge


def _classification(python_path: Path, constant: str) -> str:
    """Classify overlap without deciding ownership or mutating either source."""
    if python_path.name != "safety.py":
        return "knowledge_duplicate"

    if constant.startswith("CRISIS_"):
        return "safety_protected_overlap"

    if constant == "GRANDIOSITY_SIGNALS":
        return "review_required"

    return "knowledge_duplicate"


def find_python_markdown_duplicates(
    root: Path,
    *,
    python_root: Path = Path("src/soulmap/runtime/config"),
    markdown_roots: tuple[Path, ...] = (
        Path("skills"),
        Path("templates"),
        Path("frameworks"),
    ),
) -> tuple[KnowledgeDuplicate, ...]:
    """Find exact Python/Markdown overlaps with source-aware diagnostics.

    This is a diagnostic check only. It does not decide ownership or mutate files.
    Markdown knowledge is read from list items under their actual headings. The
    pattern mapper receives a distinct source kind because its Markdown format is
    structured around pattern frameworks rather than generic skill prose.
    """
    python_files = sorted((root / python_root).glob("*.py"))
    markdown_files = sorted(
        path
        for markdown_root in markdown_roots
        for path in (root / markdown_root).rglob("*.md")
    )

    markdown_index: dict[str, tuple[tuple[Path, str, str], ...]] = {}
    for path in markdown_files:
        for phrase, (section, source_kind) in _markdown_knowledge(path).items():
            markdown_index.setdefault(phrase, ())
            markdown_index[phrase] += ((path, section, source_kind),)

    duplicates: list[KnowledgeDuplicate] = []
    for python_path in python_files:
        for constant, phrases in _python_knowledge(python_path).items():
            for phrase in phrases:
                for markdown_path, section, source_kind in markdown_index.get(phrase, ()):
                    duplicates.append(
                        KnowledgeDuplicate(
                            phrase=phrase,
                            python_path=python_path,
                            constant=constant,
                            markdown_path=markdown_path,
                            markdown_section=section,
                            source_kind=source_kind,
                            classification=_classification(python_path, constant),
                        )
                    )

    return tuple(duplicates)
