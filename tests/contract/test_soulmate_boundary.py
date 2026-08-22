"""Contracts for the initial Soulmate library boundary."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from soulmap.devtools.support.repo import REPO_ROOT
from soulmate.contracts import ResourceContractError, ResourceReference

SOULMATE_ROOT = REPO_ROOT / "src/soulmate"


def _soulmate_python_files() -> list[Path]:
    return sorted(SOULMATE_ROOT.rglob("*.py"))


def test_soulmate_package_is_importable_without_soulmap_runtime() -> None:
    import soulmate

    assert soulmate.__all__ == ()
    assert SOULMATE_ROOT.is_dir()


def test_soulmate_source_has_no_reverse_import_to_soulmap() -> None:
    for path in _soulmate_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported_modules: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)
        assert all(
            module != "soulmap" and not module.startswith("soulmap.")
            for module in imported_modules
        ), f"Soulmate must not import SoulMap: {path}"


def test_soulmate_contract_rejects_invalid_resource_references() -> None:
    with pytest.raises(ResourceContractError, match="must not be empty"):
        ResourceReference("", Path("skills/example.md"))

    with pytest.raises(ResourceContractError, match="repository-relative"):
        ResourceReference("example", Path("/tmp/example.md"))


def test_current_soulmap_wheel_boundary_stays_unchanged() -> None:
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert 'packages = ["src/soulmap"]' in pyproject
    assert "src/soulmate" not in pyproject
