"""Enforce the one-way SoulMap -> Soulmate dependency direction."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

_PUBLIC_SOULMATE_NAMESPACES = {
    "contracts",
    "data",
    "knowledge",
    "pipeline",
    "resources",
    "text",
}


@dataclass(frozen=True)
class DependencyIssue:
    """One invalid import found in the source dependency graph."""

    path: Path
    line: int
    column: int
    message: str


def _imported_modules(tree: ast.AST) -> list[tuple[str, int, int]]:
    imports: list[tuple[str, int, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                (alias.name, node.lineno, node.col_offset) for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append((node.module, node.lineno, node.col_offset))
    return imports


def _check_soulmate_file(path: Path, tree: ast.AST) -> list[DependencyIssue]:
    return [
        DependencyIssue(
            path=path,
            line=line,
            column=column,
            message=f"Soulmate must not import SoulMap ({module})",
        )
        for module, line, column in _imported_modules(tree)
        if module == "soulmap" or module.startswith("soulmap.")
    ]


def _check_soulmap_file(path: Path, tree: ast.AST) -> list[DependencyIssue]:
    issues: list[DependencyIssue] = []
    for module, line, column in _imported_modules(tree):
        if module != "soulmate" and not module.startswith("soulmate."):
            continue
        namespace = module.split(".", 1)[1] if "." in module else ""
        if namespace not in _PUBLIC_SOULMATE_NAMESPACES:
            issues.append(
                DependencyIssue(
                    path=path,
                    line=line,
                    column=column,
                    message=(
                        "SoulMap must import Soulmate through a public namespace; "
                        f"got {module}"
                    ),
                )
            )
    return issues


def check_source_tree(repo_root: Path) -> list[DependencyIssue]:
    """Return dependency violations in both source package trees."""

    issues: list[DependencyIssue] = []
    package_roots = (
        (repo_root / "src" / "soulmate", _check_soulmate_file),
        (repo_root / "src" / "soulmap", _check_soulmap_file),
    )
    for package_root, checker in package_roots:
        if not package_root.is_dir():
            continue
        for path in sorted(package_root.rglob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as error:
                issues.append(
                    DependencyIssue(
                        path=path,
                        line=error.lineno or 1,
                        column=error.offset or 0,
                        message=f"Cannot parse Python source: {error.msg}",
                    )
                )
                continue
            issues.extend(checker(path, tree))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="soulmap check-dependencies")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root (default: current directory).",
    )
    args = parser.parse_args(argv)

    repo_root = args.root.resolve()
    issues = check_source_tree(repo_root)
    for issue in issues:
        relative_path = issue.path.resolve().relative_to(repo_root)
        print(f"{relative_path}:{issue.line}:{issue.column}: {issue.message}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
