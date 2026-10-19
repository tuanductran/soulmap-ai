from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
ACTION_DIR = ROOT / "src" / "action"


def test_python_github_action_is_self_contained() -> None:
    metadata = (ACTION_DIR / "action.yml").read_text(encoding="utf-8")
    dockerfile = (ACTION_DIR / "Dockerfile").read_text(encoding="utf-8")
    sources = {
        path.name: path.read_text(encoding="utf-8")
        for path in ACTION_DIR.glob("*.py")
    }
    combined_source = "\n".join(sources.values())

    assert "runs:" in metadata
    assert "using: docker" in metadata
    assert "image: Dockerfile" in metadata
    assert "INPUT_OPERATION" in metadata
    assert "INPUT_TOKEN" in metadata
    assert (
        "FROM python:3.11-slim-bookworm@"
        "sha256:0a310eeecf4e1f5a0743f9a6520c90c88d089c903ca5fd283f501e3a805f5f89"
    ) in dockerfile
    assert 'ENTRYPOINT ["python", "/__main__.py"]' in dockerfile
    assert "COPY ./*.py /" in dockerfile
    assert "urllib.request" in combined_source
    assert 'API_VERSION = "2026-03-10"' in sources["constants.py"]
    assert "softprops" not in combined_source
    assert "requests" not in combined_source
    assert "PyGithub" not in combined_source
    assert len(sources["__main__.py"].splitlines()) < 80


def test_python_github_action_has_no_external_imports() -> None:
    sources = list(ACTION_DIR.glob("*.py"))
    stdlib = set(sys.stdlib_module_names)
    local_modules = {path.stem for path in sources}
    imports: set[str] = set()

    for path in sources:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])

    assert imports <= stdlib | local_modules
