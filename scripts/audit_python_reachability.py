#!/usr/bin/env python3
"""Report Python modules not statically reachable from declared CLI entry points.

This is a review aid, not proof that a module is unused. Dynamic imports,
plugin conventions, test-only consumers, and files outside the selected roots
must be reviewed before removal.
"""

from __future__ import annotations

import argparse
import ast
from collections import deque
from pathlib import Path

DEFAULT_ENTRY_MODULES = ("soulmap.cli",)
SOURCE_ROOT = Path("src")


def module_name(path: Path, source_root: Path) -> str | None:
    """Convert a Python source path under the source root to a module name."""
    try:
        relative = path.relative_to(source_root)
    except ValueError:
        return None
    if relative.name == "__init__.py":
        relative = relative.parent
    else:
        relative = relative.with_suffix("")
    parts = relative.parts
    return ".".join(parts) if parts else None


def resolve_imports(
    tree: ast.Module, current_module: str, known_modules: set[str]
) -> set[str]:
    """Return statically resolvable in-repository imports from an AST."""
    found: set[str] = set()
    package = current_module.rpartition(".")[0]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in known_modules:
                    found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base_parts = package.split(".") if package else []
                ascend = node.level - 1
                if ascend > len(base_parts):
                    continue
                base = ".".join(base_parts[: len(base_parts) - ascend])
                target = ".".join(part for part in (base, node.module or "") if part)
            else:
                target = node.module or ""
            if target in known_modules:
                found.add(target)
            for alias in node.names:
                candidate = ".".join(part for part in (target, alias.name) if part)
                if candidate in known_modules:
                    found.add(candidate)
        elif isinstance(node, ast.Call):
            # Resolve only literal absolute module names; computed names remain
            # outside the static graph and must be reviewed as a limitation.
            function = node.func
            is_dynamic_import = (
                (isinstance(function, ast.Name) and function.id == "__import__")
                or (
                    isinstance(function, ast.Attribute)
                    and function.attr == "import_module"
                    and isinstance(function.value, ast.Name)
                    and function.value.id == "importlib"
                )
                or (isinstance(function, ast.Name) and function.id == "import_module")
            )
            if (
                is_dynamic_import
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and node.args[0].value in known_modules
            ):
                found.add(node.args[0].value)
    return found


def analyze(
    root: Path, entries: tuple[str, ...]
) -> tuple[set[str], set[str], list[str]]:
    """Build a conservative static import graph for Python modules under src."""
    source_root = root / SOURCE_ROOT
    paths = sorted(source_root.rglob("*.py"))
    path_by_module = {
        name: path
        for path in paths
        if (name := module_name(path, source_root)) is not None
    }
    known = set(path_by_module)
    missing = sorted(set(entries) - known)
    graph: dict[str, set[str]] = {}
    for name, path in path_by_module.items():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError, UnicodeDecodeError) as exc:
            raise RuntimeError(f"Cannot analyze {path}: {exc}") from exc
        graph[name] = resolve_imports(tree, name, known)
        parts = name.split(".")
        graph[name].update(
            ".".join(parts[:index])
            for index in range(1, len(parts))
            if ".".join(parts[:index]) in known
        )

    reachable: set[str] = set()
    queue = deque(
        module
        for entry in entries
        if entry in known
        for module in (entry, *parent_modules(entry, known))
    )
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        queue.extend(graph[current] - reachable)
    return reachable, known - reachable, missing


def parent_modules(name: str, known_modules: set[str]) -> tuple[str, ...]:
    """Return known parent packages from nearest to farthest."""
    parts = name.split(".")
    return tuple(
        ".".join(parts[:index])
        for index in range(len(parts) - 1, 0, -1)
        if ".".join(parts[:index]) in known_modules
    )


def main(argv: list[str] | None = None) -> int:
    """Print review-only candidates not statically reachable from entry modules."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--entry",
        action="append",
        dest="entries",
        help="Python module entry point (repeatable; defaults to soulmap.cli).",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    entries = tuple(args.entries or DEFAULT_ENTRY_MODULES)
    reachable, candidates, missing = analyze(root, entries)
    for entry in missing:
        print(f"ENTRY NOT FOUND: {entry}")
    print("REVIEW-ONLY: not statically reachable from configured Python entry points")
    for name in sorted(candidates):
        print(f"{module_path(root, name)}: {name}")
    print(f"Entry modules: {len(entries)}")
    print(f"Reachable modules: {len(reachable)}")
    print(f"Review candidates: {len(candidates)}")
    print("Limitations: dynamic imports, test-only consumers, data/Markdown loaders,")
    print("entry-point conventions, and non-Python consumers are not proven here.")
    return 1 if missing else 0


def module_path(root: Path, name: str) -> str:
    """Return the source path for a module name."""
    base = root / SOURCE_ROOT / Path(*name.split("."))
    init_path = base / "__init__.py"
    if init_path.is_file():
        return str(init_path.relative_to(root))
    return str(base.with_suffix(".py").relative_to(root))


if __name__ == "__main__":
    raise SystemExit(main())
