from __future__ import annotations

import ast

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.knowledge.runtime_registry import (
    _has_heading,
    _registry,
    _validate_registry,
    runtime_section,
    runtime_skill_path,
)


def test_pattern_registry_heading_validation_is_exact() -> None:
    assert _has_heading("## Pattern 1: Repeating Cycle\n", "Pattern 1")
    assert not _has_heading("## Pattern 2: Different Cycle\n", "Pattern 1")


def test_runtime_registry_resolves_known_domain_source() -> None:
    path = runtime_skill_path("grief-companion")
    assert path == REPO_ROOT / "skills/frameworks/grief-companion.md"
    assert (
        runtime_section("grief-companion", "contract") == "Runtime detection contract"
    )
    assert runtime_skill_path("shadow-patterns") != runtime_skill_path(
        "self-compassion"
    )


def test_detector_modules_do_not_embed_skill_source_paths() -> None:
    detector_root = REPO_ROOT / "src/soulmap/runtime/detectors"
    violations: list[str] = []

    for path in sorted(detector_root.glob("*_detector.py")):
        content = path.read_text(encoding="utf-8")
        if 'default_skill_path("skills/' in content:
            violations.append(str(path.relative_to(REPO_ROOT)))

    assert not violations, "\n".join(violations)


def test_runtime_skill_path_consumers_are_registered() -> None:
    """Every detector's stable Markdown source reference must be registry-backed."""
    registry = _registry()
    detector_root = REPO_ROOT / "src/soulmap/runtime/detectors"
    consumers: dict[str, set[str]] = {}

    for path in sorted(detector_root.glob("*_detector.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id != "runtime_skill_path" or len(node.args) != 1:
                continue
            argument = node.args[0]
            if not isinstance(argument, ast.Constant) or not isinstance(
                argument.value, str
            ):
                raise AssertionError(
                    f"{path.relative_to(REPO_ROOT)} uses a non-literal runtime source"
                )
            consumers.setdefault(argument.value, set()).add(
                str(path.relative_to(REPO_ROOT))
            )

    unregistered = {
        source: sorted(paths)
        for source, paths in consumers.items()
        if source not in registry
    }
    assert not unregistered, f"Unregistered runtime sources: {unregistered}"


def test_runtime_knowledge_modules_do_not_embed_skill_source_paths() -> None:
    """Runtime knowledge loaders must resolve Markdown through the registry."""
    knowledge_root = REPO_ROOT / "src/soulmap/runtime/knowledge"
    excluded = {"keyword_lists.py", "runtime_registry.py"}
    violations: list[str] = []

    for path in sorted(knowledge_root.glob("*.py")):
        if path.name in excluded:
            continue
        content = path.read_text(encoding="utf-8")
        if 'default_skill_path("skills/' in content:
            violations.append(str(path.relative_to(REPO_ROOT)))

    assert not violations, "\n".join(violations)


def test_runtime_knowledge_source_consumers_are_registered() -> None:
    """Every runtime knowledge loader source reference must be registry-backed."""
    registry = _registry()
    knowledge_root = REPO_ROOT / "src/soulmap/runtime/knowledge"
    excluded = {"keyword_lists.py", "runtime_registry.py"}
    consumers: dict[str, set[str]] = {}

    for path in sorted(knowledge_root.glob("*.py")):
        if path.name in excluded:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id != "runtime_skill_path" or len(node.args) != 1:
                continue
            argument = node.args[0]
            if not isinstance(argument, ast.Constant) or not isinstance(
                argument.value, str
            ):
                raise AssertionError(
                    f"{path.relative_to(REPO_ROOT)} uses a non-literal runtime source"
                )
            consumers.setdefault(argument.value, set()).add(
                str(path.relative_to(REPO_ROOT))
            )

    unregistered = {
        source: sorted(paths)
        for source, paths in consumers.items()
        if source not in registry
    }
    assert not unregistered, f"Unregistered runtime sources: {unregistered}"


def test_runtime_registry_is_complete_and_structurally_valid() -> None:
    registry = _registry()

    assert (
        _validate_registry(
            registry, REPO_ROOT / "src/soulmap/runtime/source-registry.md"
        )
        == ()
    )
    assert all(runtime_skill_path(source).is_file() for source in registry)
