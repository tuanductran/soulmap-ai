"""Checks that declared tooling packages match the repo's scripts."""

from __future__ import annotations

from pathlib import Path


def test_requirements_dev_includes_active_tooling() -> None:
    content = Path("requirements-dev.txt").read_text(encoding="utf-8")

    for package in [
        "ruff",
        "isort",
        "mdformat",
        "mdformat-gfm",
        "pytest",
        "pyright",
        "pre-commit",
        "commitizen",
    ]:
        assert package in content


def test_requirements_dev_excludes_removed_formatter() -> None:
    content = Path("requirements-dev.txt").read_text(encoding="utf-8")
    assert "black" not in content
