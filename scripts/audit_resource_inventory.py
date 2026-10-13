#!/usr/bin/env python3
"""Inventory indirect knowledge/resource references without declaring files unused.

This report combines runtime registry edges, literal path references, packaging
membership, and local maintainer conventions. Missing edges are review candidates
only because resources can be discovered by convention or loaded indirectly.
"""

from __future__ import annotations

import argparse
import ast
import re
from dataclasses import dataclass
from pathlib import Path

RESOURCE_ROOTS: dict[str, tuple[str, ...]] = {
    "shipped-knowledge": ("skills",),
    "internal-templates": ("templates",),
    "maintainer-prompts": (".claude/prompts",),
    "maintainer-skills": (".claude/skills",),
    "maintainer-rules": (".claude/rules",),
    "plugin-metadata": (".claude-plugin",),
    "eval-datasets": ("evals/datasets",),
    "schemas": ("schemas",),
}
ROOT_RESOURCES = ("SKILL.md", "SOULMAP.md")
TEXT_SUFFIXES = {".md", ".json", ".json5", ".jsonl", ".toml", ".yaml", ".yml", ".py", ".txt"}
EXCLUDED_PARTS = {".git", ".venv", "dist", "build", "node_modules", "__pycache__"}
MARKDOWN_LINK = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")


@dataclass(frozen=True, slots=True)
class ResourceFinding:
    """Evidence recorded for one knowledge or supporting resource."""

    path: str
    category: str
    evidence: tuple[str, ...]


def _resource_files(root: Path) -> dict[str, str]:
    """Return repository-relative resource paths and their governance categories."""
    found: dict[str, str] = {}
    for category, directories in RESOURCE_ROOTS.items():
        for directory in directories:
            base = root / directory
            if not base.is_dir():
                continue
            for path in sorted(base.rglob("*")):
                if path.is_file() and not any(part in EXCLUDED_PARTS for part in path.parts):
                    found[path.relative_to(root).as_posix()] = category
    for name in ROOT_RESOURCES:
        if (root / name).is_file():
            found[name] = "shipped-knowledge"
    return found


def _registry_paths(root: Path) -> tuple[set[str], set[str]]:
    """Read literal source paths from the canonical runtime registry."""
    registry_file = root / "src/soulmap/runtime/source_registry.py"
    if not registry_file.is_file():
        return set(), set()
    tree = ast.parse(registry_file.read_text(encoding="utf-8"), filename=str(registry_file))
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "REGISTRY":
            value = node.value
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "REGISTRY" for target in node.targets
        ):
            value = node.value
        else:
            continue
        try:
            registry = ast.literal_eval(value)
        except (ValueError, TypeError):
            return set(), {"runtime registry is not a static literal; manual review required"}
        if not isinstance(registry, dict):
            return set(), {"runtime registry is not a mapping; manual review required"}
        paths = {
            entry[0]
            for entry in registry.values()
            if isinstance(entry, tuple) and entry and isinstance(entry[0], str)
        }
        return paths, set()
    return set(), {"canonical REGISTRY assignment was not found"}


def _resolved_markdown_links(path: Path, root: Path) -> set[str]:
    """Resolve simple relative Markdown links to files inside the repository."""
    if path.suffix.lower() != ".md":
        return set()
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    targets: set[str] = set()
    for raw_target in MARKDOWN_LINK.findall(content):
        target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
        if not target or target.startswith(("#", "https://", "http://", "mailto:", "data:")):
            continue
        target = target.split("#", 1)[0].split("?", 1)[0]
        if not target:
            continue
        candidates = ((path.parent / target).resolve(), (root / target).resolve())
        for candidate in candidates:
            try:
                relative = candidate.relative_to(root.resolve()).as_posix()
            except ValueError:
                continue
            if candidate.is_file():
                targets.add(relative)
                break
    return targets


def audit(root: Path) -> tuple[ResourceFinding, ...]:
    """Return a conservative resource inventory and evidence labels."""
    root = root.resolve()
    resources = _resource_files(root)
    registry_paths, registry_warnings = _registry_paths(root)
    existing_paths = set(resources)
    source_files = [
        path for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in TEXT_SUFFIXES
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts)
    ]
    literal_path_sources: dict[str, set[str]] = {path: set() for path in resources}
    markdown_links: dict[str, set[str]] = {path: set() for path in resources}
    for source in source_files:
        relative_source = source.relative_to(root).as_posix()
        try:
            content = source.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        linked = _resolved_markdown_links(source, root)
        for target in linked & existing_paths:
            if target != relative_source:
                markdown_links[target].add(relative_source)
        for resource_path in resources:
            if resource_path != relative_source and resource_path in content:
                literal_path_sources[resource_path].add(relative_source)

    findings: list[ResourceFinding] = []
    for resource_path, category in sorted(resources.items()):
        evidence: set[str] = set()
        if resource_path in registry_paths:
            evidence.add("canonical-runtime-registry")
        if literal_path_sources[resource_path]:
            evidence.add("literal-path-reference")
        if markdown_links[resource_path]:
            evidence.add("local-markdown-link")
        if category == "shipped-knowledge":
            evidence.add("shipped-package-contract")
        elif category in {"maintainer-prompts", "maintainer-skills", "maintainer-rules", "internal-templates"}:
            evidence.add("local-maintainer-surface")
        elif category == "plugin-metadata":
            evidence.add("skill-artifact-metadata")
        elif category == "eval-datasets":
            evidence.add("evaluation-data-surface")
        if not evidence:
            evidence.add("review-only-no-static-edge")
        findings.append(ResourceFinding(resource_path, category, tuple(sorted(evidence))))

    for missing in sorted(registry_paths - existing_paths):
        findings.append(
            ResourceFinding(missing, "missing-resource", ("canonical-runtime-registry-target-missing",))
        )
    for warning in sorted(registry_warnings):
        findings.append(ResourceFinding("src/soulmap/runtime/source_registry.py", "audit-limitation", (warning,)))
    return tuple(findings)


def main(argv: list[str] | None = None) -> int:
    """Print a resource inventory; only missing registry targets fail the command."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    findings = audit(args.root)
    print("Resource reachability inventory (review aid; not a deletion report)")
    for finding in findings:
        print(f"[{finding.category}] {finding.path} :: {', '.join(finding.evidence)}")
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.category] = counts.get(finding.category, 0) + 1
    print("\nInventory counts")
    for category, count in sorted(counts.items()):
        print(f"{category}: {count}")
    missing = any(finding.category == "missing-resource" for finding in findings)
    print("Unreferenced resources remain review-only; convention-based and dynamic loaders are not proven.")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
