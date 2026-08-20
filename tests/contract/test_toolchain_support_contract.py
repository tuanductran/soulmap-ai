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
SETUP_UV_ACTION = REPO_ROOT / ".github" / "actions" / "setup-uv" / "action.yml"
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
    "werkzeug",
    "pytest-playwright",
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
    "werkzeug": "Werkzeug",
    "pytest-playwright": "pytest-playwright",
}


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
    assert "-n 0 -q" in script_text

    ci_text = WORKFLOWS[0].read_text(encoding="utf-8")
    release_text = WORKFLOWS[1].read_text(encoding="utf-8")
    for workflow_text in (ci_text, release_text):
        assert "uv run python scripts/pytest_diagnostics.py" in workflow_text

    assert "PYTEST_RANDOMLY_SEED" in ci_text
    assert '--randomly-seed="${PYTEST_RANDOMLY_SEED}"' in ci_text


def test_coverage_gate_is_enforced_without_masking_failures() -> None:
    project_text = PYPROJECT.read_text(encoding="utf-8")
    ci_text = WORKFLOWS[0].read_text(encoding="utf-8")

    assert "fail_under = 95" in project_text
    assert 'source = ["src/soulmap/runtime", "src/soulmap/web"]' in project_text
    assert "--cov-fail-under=95" in ci_text
    assert "--cov=src/soulmap/web" in ci_text
    assert "--cov-report=json:coverage.json" in ci_text
    assert "name: soulmap-coverage" in ci_text
    assert "--cov-report=term-missing -q 2>&1 | tail" not in ci_text


def test_pyright_scope_covers_repository_python_surfaces() -> None:
    project_text = PYPROJECT.read_text(encoding="utf-8")

    assert 'include = ["src", "tests", "scripts"]' in project_text


def test_workflows_use_local_resilient_tool_installers() -> None:
    setup_uv_text = SETUP_UV_ACTION.read_text(encoding="utf-8")
    actionlint_text = ACTIONLINT_ACTION.read_text(encoding="utf-8")

    assert 'UV_VERSION: "0.12.5"' in setup_uv_text
    assert "UV_UNMANAGED_INSTALL" in setup_uv_text
    assert "https://astral.sh/uv/${UV_VERSION}/install.sh" in setup_uv_text
    assert 'default: "1.7.12"' in actionlint_text
    assert (
        "8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8"
        in actionlint_text
    )
    assert "sha256sum --check --strict" in actionlint_text

    for workflow_path in CI_WORKFLOWS:
        workflow_text = workflow_path.read_text(encoding="utf-8")
        assert "astral-sh/setup-uv" not in workflow_text
        assert "raven-actions/actionlint" not in workflow_text
        assert "uses: ./.github/actions/setup-uv" in workflow_text

    assert "uses: ./.github/actions/actionlint" in (
        REPO_ROOT / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")


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
