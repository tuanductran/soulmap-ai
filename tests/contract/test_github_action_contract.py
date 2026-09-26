from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).parents[2]
ACTION_DIR = ROOT / "src" / "action"


def test_python_github_action_is_self_contained() -> None:
    metadata = (ACTION_DIR / "action.yml").read_text(encoding="utf-8")
    dockerfile = (ACTION_DIR / "Dockerfile").read_text(encoding="utf-8")
    source = (ACTION_DIR / "__main__.py").read_text(encoding="utf-8")

    assert "runs:" in metadata
    assert "using: docker" in metadata
    assert "image: Dockerfile" in metadata
    assert "INPUT_OPERATION" in metadata
    assert "INPUT_TOKEN" in metadata
    assert "FROM python:3.11-slim" in dockerfile
    assert 'ENTRYPOINT ["python", "/__main__.py"]' in dockerfile
    assert "urllib.request" in source
    assert 'API_VERSION = "2026-03-10"' in source
    assert "softprops" not in source
    assert "requests" not in source
    assert "PyGithub" not in source
    assert 'operation == "probe"' in source
    assert "run_probe" in source


def test_python_github_action_has_no_external_imports() -> None:
    source = (ACTION_DIR / "__main__.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    stdlib = set(__import__("sys").stdlib_module_names)
    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert imports <= stdlib
