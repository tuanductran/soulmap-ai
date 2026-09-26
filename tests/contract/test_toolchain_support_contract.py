from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
LOCKFILE = REPO_ROOT / "uv.lock"
RESEARCH = REPO_ROOT / "docs" / "engineering" / "package-compatibility-research.md"
PYTEST_DIAGNOSTICS = REPO_ROOT / "scripts" / "pytest_diagnostics.py"
WORKFLOWS = (
    REPO_ROOT / ".github" / "workflows" / "ci.yml",
    REPO_ROOT / ".github" / "workflows" / "release.yml",
)
CI_WORKFLOWS = tuple((REPO_ROOT / ".github" / "workflows").glob("*.yml"))
ACTIONLINT_ACTION = REPO_ROOT / ".github" / "actions" / "actionlint" / "action.yml"

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


SETUP_UV_SHA = "c18668ad3cf93ea998bef934396af7bb5c839dc7"


def test_python_floor_and_ci_baseline_are_aligned() -> None:
    project_text = PYPROJECT.read_text(encoding="utf-8")
    assert 'requires-python = ">=3.11"' in project_text

    for workflow_path in WORKFLOWS:
        workflow_text = workflow_path.read_text(encoding="utf-8")
        assert 'python-version: "3.11"' in workflow_text


def test_ci_and_release_use_the_same_pytest_diagnostics_helper() -> None:
    script_text = PYTEST_DIAGNOSTICS.read_text(encoding="utf-8")
    assert "uv" in script_text
    assert "--randomly-seed=" in script_text
    assert "scope=scope" in script_text
    assert '"0", scope=scope' in script_text

    ci_text = WORKFLOWS[0].read_text(encoding="utf-8")
    release_text = WORKFLOWS[1].read_text(encoding="utf-8")
    for workflow_text in (ci_text, release_text):
        assert "uv run python scripts/pytest_diagnostics.py" in workflow_text

    assert "PYTEST_RANDOMLY_SEED" in ci_text
    assert '--randomly-seed="${PYTEST_RANDOMLY_SEED}"' in ci_text


def test_workflows_pin_third_party_actions_and_use_verified_uv_setup() -> None:
    actionlint_text = ACTIONLINT_ACTION.read_text(encoding="utf-8")
    assert 'default: "1.7.12"' in actionlint_text
    assert (
        "8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8"
        in actionlint_text
    )
    assert "sha256sum --check --strict" in actionlint_text

    for workflow_path in CI_WORKFLOWS:
        workflow_text = workflow_path.read_text(encoding="utf-8")
        assert f"astral-sh/setup-uv@{SETUP_UV_SHA}" in workflow_text
        assert "raven-actions/actionlint" not in workflow_text
        assert "@v7" not in workflow_text
        assert "@v4" not in workflow_text

    release_prep_text = (REPO_ROOT / ".github" / "workflows" / "release.yml").read_text(
        encoding="utf-8"
    )
    release_finalize_text = (
        REPO_ROOT / ".github" / "workflows" / "release-finalize.yml"
    ).read_text(encoding="utf-8")
    assert "uses: $/src/action" in release_finalize_text
    assert "operation: release" in release_finalize_text
    assert 'git push origin "$TAG"' in release_finalize_text
    assert "actions/upload-artifact@" in release_finalize_text
    assert "git push --follow-tags" not in release_prep_text


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
    assert "Python 3.11.16" in research_text
    assert "python.org/downloads/release/python-31116" in research_text
    assert "| uv | 0.12.5 (CI installer pin) |" in research_text
    assert "| actionlint | 1.7.12 (CI binary pin) |" in research_text
