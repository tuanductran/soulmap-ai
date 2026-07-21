"""Audit duplicated knowledge between Python config and Markdown sources."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from importlib.util import resolve_name
from pathlib import Path

from soulmap.runtime.knowledge.keyword_lists import (
    extract_keyword_section,
    extract_labeled_groups,
)
from soulmap.runtime.knowledge.pattern_source import parse_pattern_mapper

_SIGNAL_HEADINGS = ("Activation Signals", "Detection signals")
_CONFIG_MODULE_PREFIX = "soulmap.runtime.config"


@dataclass(frozen=True, slots=True)
class KnowledgeDuplicate:
    """A Python config phrase that also exists in Markdown knowledge."""

    phrase: str
    python_path: Path
    constant: str
    markdown_path: Path
    markdown_section: str
    markdown_group: str
    source_kind: str
    classification: str


@dataclass(frozen=True, slots=True)
class ConfigUsage:
    """Runtime usage information for one Python config constant."""

    python_path: Path
    constant: str
    referenced_from: tuple[Path, ...]

    @property
    def is_orphaned(self) -> bool:
        return not self.referenced_from


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
        elif isinstance(node, ast.AnnAssign):
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
            if isinstance(target, ast.Name) and target.id != "__all__":
                knowledge[target.id] = values

    return knowledge


def _add_markdown_phrases(
    knowledge: dict[str, tuple[str, str, str]],
    phrases: tuple[str, ...],
    *,
    section: str,
    group: str,
    source_kind: str,
) -> None:
    for phrase in phrases:
        normalized = phrase.strip().lower()
        if normalized:
            knowledge[normalized] = (section, group, source_kind)


def _markdown_knowledge(path: Path) -> dict[str, tuple[str, str, str]]:
    """Extract only Markdown knowledge consumed by the runtime parsers."""
    text = path.read_text(encoding="utf-8")
    source_kind = (
        "pattern_framework" if path.name == "pattern-mapper.md" else "markdown"
    )

    if path.name == "pattern-mapper.md":
        knowledge: dict[str, tuple[str, str, str]] = {}
        for pattern in parse_pattern_mapper(text).values():
            _add_markdown_phrases(
                knowledge,
                pattern.keywords,
                section="Detection signals",
                group=pattern.name,
                source_kind=source_kind,
            )
        return knowledge

    knowledge: dict[str, tuple[str, str, str]] = {}
    for heading in _SIGNAL_HEADINGS:
        groups = extract_labeled_groups(text, heading)
        if groups:
            for group, phrases in groups.items():
                _add_markdown_phrases(
                    knowledge,
                    phrases,
                    section=heading,
                    group=group,
                    source_kind=source_kind,
                )
        else:
            phrases = extract_keyword_section(text, heading)
            _add_markdown_phrases(
                knowledge,
                phrases,
                section=heading,
                group=heading,
                source_kind=source_kind,
            )

    return knowledge


def markdown_consumers(root: Path, markdown_path: Path) -> tuple[Path, ...]:
    """Find runtime files that load a Markdown source via ``default_skill_path``."""
    relative_path = markdown_path.relative_to(root).as_posix()
    consumers: list[Path] = []

    for path in sorted((root / "src/soulmap/runtime").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "default_skill_path"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == relative_path
            ):
                continue
            consumers.append(path)
            break

    return tuple(consumers)


def _classification(python_path: Path, constant: str) -> str:
    """Classify overlap without deciding ownership or mutating either source."""
    if python_path.name != "safety.py":
        return "knowledge_duplicate"

    if constant.startswith("CRISIS_"):
        return "safety_protected_overlap"

    if constant == "GRANDIOSITY_SIGNALS":
        return "review_required"

    return "knowledge_duplicate"


def _module_name(path: Path, root: Path) -> str:
    relative = path.relative_to(root / "src").with_suffix("")
    return ".".join(relative.parts)


def _is_config_module(module: str) -> bool:
    return module == _CONFIG_MODULE_PREFIX or module.startswith(
        f"{_CONFIG_MODULE_PREFIX}."
    )


def _resolve_import_module(
    module: str | None,
    level: int,
    path: Path,
    root: Path,
) -> str:
    if level == 0:
        return module or ""

    package = _module_name(path, root).rsplit(".", 1)[0]
    relative = "." * level + (module or "")
    return resolve_name(relative, package)


def _reexported_symbols(
    init_path: Path,
    root: Path,
    symbols: dict[str, dict[str, tuple[Path, str]]],
) -> dict[str, tuple[Path, str]]:
    """Resolve the names a config package's ``__init__.py`` re-exports.

    ``from soulmap.runtime.config import X`` only works at runtime if
    ``__init__.py`` actually imports ``X`` from one of its submodules. This
    mirrors that resolution so the audit's symbol table has an entry for the
    plain package name, not just per-submodule module names.
    """
    if not init_path.is_file():
        return {}

    tree = ast.parse(init_path.read_text(encoding="utf-8"), filename=str(init_path))
    reexported: dict[str, tuple[Path, str]] = {}

    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        module = _resolve_import_module(node.module, node.level, init_path, root)
        module_symbols = symbols.get(module, {})
        if not module_symbols:
            continue
        for alias in node.names:
            if alias.name == "*":
                continue
            symbol = module_symbols.get(alias.name)
            if symbol is not None:
                reexported[alias.asname or alias.name] = symbol

    return reexported


def _config_symbols(
    root: Path,
    config_dir: Path,
) -> dict[str, dict[str, tuple[Path, str]]]:
    symbols: dict[str, dict[str, tuple[Path, str]]] = {}
    for path in sorted(config_dir.glob("*.py")):
        module = _module_name(path, root)
        symbols[module] = {
            constant: (path, constant) for constant in _python_knowledge(path)
        }

    package_module = _module_name(config_dir, root)
    reexported = _reexported_symbols(config_dir / "__init__.py", root, symbols)
    if reexported:
        symbols[package_module] = reexported

    return symbols


def _config_references(
    path: Path,
    root: Path,
    symbols: dict[str, dict[str, tuple[Path, str]]],
) -> set[tuple[Path, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    direct_names: dict[str, tuple[Path, str]] = {}
    module_aliases: dict[str, str] = {}

    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            module = _resolve_import_module(node.module, node.level, path, root)
            if not _is_config_module(module):
                continue
            module_symbols = symbols.get(module, {})
            for alias in node.names:
                if alias.name == "*":
                    continue
                symbol = module_symbols.get(alias.name)
                if symbol is not None:
                    direct_names[alias.asname or alias.name] = symbol
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if not _is_config_module(alias.name):
                    continue
                if alias.asname:
                    module_aliases[alias.asname] = alias.name

    references: set[tuple[Path, str]] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            symbol = direct_names.get(node.id)
            if symbol is not None:
                references.add(symbol)
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            module = module_aliases.get(node.value.id)
            if module is None:
                continue
            symbol = symbols.get(module, {}).get(node.attr)
            if symbol is not None:
                references.add(symbol)

    return references


def find_config_usage(
    root: Path,
    *,
    python_root: Path = Path("src/soulmap/runtime/config"),
) -> tuple[ConfigUsage, ...]:
    """Find runtime references to config constants by import provenance.

    Local variables with the same name as a config constant are not treated as
    config usage unless the runtime file actually imports that constant or its
    config module.
    """
    config_dir = root / python_root
    config_files = sorted(config_dir.glob("*.py"))
    symbols = _config_symbols(root, config_dir)
    constants = {
        (path, constant)
        for path in config_files
        for constant in _python_knowledge(path)
    }
    references: dict[tuple[Path, str], set[Path]] = {
        symbol: set() for symbol in constants
    }
    runtime_root = root / "src/soulmap/runtime"

    for path in sorted(runtime_root.rglob("*.py")):
        if config_dir in path.parents or path == config_dir:
            continue
        for symbol in _config_references(path, root, symbols):
            references[symbol].add(path)

    return tuple(
        ConfigUsage(
            python_path=path,
            constant=constant,
            referenced_from=tuple(sorted(references[(path, constant)])),
        )
        for path, constant in sorted(constants)
    )


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
    Markdown knowledge is parsed with the same runtime loaders used by detectors.
    """
    python_files = sorted((root / python_root).glob("*.py"))
    markdown_files = sorted(
        path
        for markdown_root in markdown_roots
        for path in (root / markdown_root).rglob("*.md")
    )

    markdown_index: dict[str, tuple[tuple[Path, str, str, str], ...]] = {}
    for path in markdown_files:
        for phrase, (section, group, source_kind) in _markdown_knowledge(path).items():
            markdown_index.setdefault(phrase, ())
            markdown_index[phrase] += ((path, section, group, source_kind),)

    duplicates: list[KnowledgeDuplicate] = []
    for python_path in python_files:
        for constant, phrases in _python_knowledge(python_path).items():
            for phrase in phrases:
                for markdown_path, section, group, source_kind in markdown_index.get(
                    phrase, ()
                ):
                    duplicates.append(
                        KnowledgeDuplicate(
                            phrase=phrase,
                            python_path=python_path,
                            constant=constant,
                            markdown_path=markdown_path,
                            markdown_section=section,
                            markdown_group=group,
                            source_kind=source_kind,
                            classification=_classification(python_path, constant),
                        )
                    )

    return tuple(duplicates)
