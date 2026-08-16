from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
LOCKFILE = REPO_ROOT / "uv.lock"
RESEARCH = REPO_ROOT / "docs" / "engineering" / "package-compatibility-research.md"
WORKFLOWS = (
    REPO_ROOT / ".github" / "workflows" / "ci.yml",
    REPO_ROOT / ".github" / "workflows" / "release.yml",
)

DIRECT_DEV_PACKAGES = {
    "hypothesis",
    "ruff",
    "lefthook",
    "pymarkdownlnt",
    "pytest",
    "pytest-cov",
    "pytest-xdist",
    "pytest-timeout",
    "pytest-randomly",
    "pyright",
    "commitizen",
    "deptry",
    "vulture",
}
RESEARCH_LABELS = {
    "hypothesis": "Hypothesis",
    "ruff": "Ruff",
    "lefthook": "lefthook",
    "pymarkdownlnt": "PyMarkdownLnt",
    "pytest": "pytest",
    "pytest-cov": "pytest-cov",
    "pytest-xdist": "pytest-xdist",
    "pytest-timeout": "pytest-timeout",
    "pytest-randomly": "pytest-randomly",
    "pyright": "Pyright",
    "commitizen": "Commitizen",
    "deptry": "Deptry",
    "vulture": "Vulture",
}


def test_python_floor_and_ci_baseline_are_aligned() -> None:
    project_text = PYPROJECT.read_text(encoding="utf-8")
    assert 'requires-python = ">=3.11"' in project_text

    for workflow_path in WORKFLOWS:
        workflow_text = workflow_path.read_text(encoding="utf-8")
        assert 'python-version: "3.11"' in workflow_text


def test_direct_dev_packages_are_locked() -> None:
    lock_text = LOCKFILE.read_text(encoding="utf-8")

    for package_name in DIRECT_DEV_PACKAGES:
        assert re.search(
            rf'^name = "{re.escape(package_name)}"$', lock_text, re.MULTILINE
        )


def test_package_research_covers_every_direct_dev_package() -> None:
    research_text = RESEARCH.read_text(encoding="utf-8")

    for package_name in DIRECT_DEV_PACKAGES:
        assert f"| {RESEARCH_LABELS[package_name]} |" in research_text

    assert "Hatchling" in research_text
    assert "Python 3.11" in research_text
    assert "pytest-randomly" in research_text
    assert "pytest-xdist" in research_text
