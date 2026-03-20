"""Checks that declared tooling packages match the repo's scripts."""

from __future__ import annotations

from pathlib import Path
import re
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
    dev = Path("docs/DEV.md").read_text(encoding="utf-8")

    for phrase in [
        "modules.resource_sanitizer",
        "modules.biometric_ingest",
        "modules.memory_ledger",
        "explicit user consent",
    ]:
        assert phrase in api

    for phrase in [
        "python tests/test_safety_evals.py",
        "python -m tools.eval_responses",
        "modules/biometric_ingest.py",
        "modules/memory_ledger.py",
        "opt-in features",
    ]:
        assert phrase in operations

    for phrase in [
        "python -m tools.eval_responses",
        ".codex/",
        "Neither layer replaces `AGENTS.md`",
    ]:
        assert phrase in dev


def test_tools_format_runs_pymarkdown_fix() -> None:
    formatter = Path("tools/format.py").read_text(encoding="utf-8")

    assert '"-m", "pymarkdown", "fix"' in formatter


def test_bootstrap_installs_git_hooks() -> None:
    shell_bootstrap = Path("scripts/bootstrap_venv.sh").read_text(encoding="utf-8")
    python_bootstrap = Path("tools/bootstrap_venv.py").read_text(encoding="utf-8")
    dev = Path("docs/DEV.md").read_text(encoding="utf-8")

    for phrase in [
        "python -m pre_commit install",
        "python -m pre_commit install --hook-type commit-msg",
    ]:
        assert phrase in shell_bootstrap

    for phrase in [
        '"pre_commit", "install"',
        '"pre_commit", "install", "--hook-type", "commit-msg"',
    ]:
        assert phrase in python_bootstrap

    for phrase in [
        "This bootstrap flow also installs the local Git hooks",
        "installed automatically",
    ]:
        assert phrase in dev


def test_pre_commit_uses_current_python_tooling_hooks() -> None:
    config = Path(".pre-commit-config.yaml").read_text(encoding="utf-8")
    dev_dependencies = "\n".join(_dev_dependencies())

    assert "- id: ruff-check" in config
    assert "- id: ruff-format" in config
    assert "- id: ruff\n" not in config

    isort_dependency = next(
        dep for dep in _dev_dependencies() if dep.startswith("isort==")
    )
    match = re.search(r"repo: https://github.com/PyCQA/isort\s+rev: ([^\n]+)", config)
    assert match is not None
    assert match.group(1).strip() == isort_dependency.split("==", maxsplit=1)[1]
    assert "pre-commit" in dev_dependencies
