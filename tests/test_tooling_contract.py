"""Checks that declared tooling packages match the repo's scripts."""

from __future__ import annotations

from pathlib import Path
import tomllib


def _dev_dependencies() -> list[str]:
    with Path("pyproject.toml").open("rb") as file:
        data = tomllib.load(file)
    return data["project"]["optional-dependencies"]["dev"]


def test_pyproject_dev_includes_active_tooling() -> None:
    content = "\n".join(_dev_dependencies())

    for package in [
        "ruff",
        "isort",
        "pymarkdownlnt",
        "pytest",
        "pyright",
        "pre-commit",
        "commitizen",
    ]:
        assert package in content


def test_pyproject_dev_excludes_removed_formatter() -> None:
    content = "\n".join(_dev_dependencies())
    assert "black" not in content


def test_pyproject_runtime_dependencies_are_explicit() -> None:
    with Path("pyproject.toml").open("rb") as file:
        data = tomllib.load(file)
    assert data["project"]["dependencies"] == []


def test_docs_cover_experimental_modules_and_safety_workflow() -> None:
    api = Path("docs/API.md").read_text(encoding="utf-8")
    operations = Path("docs/OPERATIONS.md").read_text(encoding="utf-8")

    for phrase in [
        "modules.resource_sanitizer",
        "modules.biometric_ingest",
        "modules.memory_ledger",
        "explicit user consent",
    ]:
        assert phrase in api

    for phrase in [
        "python tests/test_safety_evals.py",
        "modules/biometric_ingest.py",
        "modules/memory_ledger.py",
        "opt-in features",
    ]:
        assert phrase in operations


def test_tools_format_runs_pymarkdown_fix() -> None:
    formatter = Path("tools/format.py").read_text(encoding="utf-8")

    assert '"-m", "pymarkdown", "fix"' in formatter
