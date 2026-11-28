from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PYPROJECT = REPO_ROOT / "pyproject.toml"
LOCKFILE = REPO_ROOT / "uv.lock"
RESEARCH = REPO_ROOT / "docs" / "engineering" / "package-compatibility-research.md"
PYTEST_DIAGNOSTICS = REPO_ROOT / "scripts" / "pytest_diagnostics.py"
WORKFLOWS = (
    REPO_ROOT / ".github" / "workflows" / "ci.yml",
    REPO_ROOT / ".github" / "workflows" / "release.yml",
)
# CodeQL uses build-mode none and the read-only release audit uses the Docker
# action directly; neither workflow needs the project's uv environment.
CI_WORKFLOWS = tuple(
    path
    for path in (REPO_ROOT / ".github" / "workflows").glob("*.yml")
    if path.name not in {"codeql.yml", "release-immutability-audit.yml"}
)
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


SETUP_UV_SHA = "1db35dd8eee11c5894872e0b383ae6c406cf738d"


def test_python_floor_and_ci_baseline_are_aligned() -> None:
    project_text = PYPROJECT.read_text(encoding="utf-8")
    assert 'requires-python = ">=3.11"' in project_text

    for workflow_path in WORKFLOWS:
        workflow_text = workflow_path.read_text(encoding="utf-8")
        assert 'python-version: "3.11"' in workflow_text


def test_codeql_static_analysis_uses_one_suite_without_project_install() -> None:
    workflow_text = (REPO_ROOT / ".github" / "workflows" / "codeql.yml").read_text(
        encoding="utf-8"
    )

    assert "build-mode: none" in workflow_text
    assert "queries: security-and-quality" in workflow_text
    assert "queries: security-extended,security-and-quality" not in workflow_text
    assert "astral-sh/setup-uv@" not in workflow_text
    assert "uv sync --locked" not in workflow_text


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

    assert "PYTEST_RANDOMLY_SEED" in script_text
    assert "--cov=src/soulmap" in script_text
    assert "--cov-report=term-missing" in script_text
    assert 'SOULMAP_PYTEST_COVERAGE: "1"' in ci_text
    assert "Coverage report (Ubuntu only)" not in ci_text
    assert (
        "uv run pytest -q tests/unit/runtime/detectors tests/unit/runtime/synthesis tests/unit/runtime/knowledge tests/unit/runtime/routing tests/unit/devtools/audit tests/unit/devtools/evals tests/mutation/test_safety_critical_mutations.py"
        in ci_text
    )
    assert "name: Knowledge consistency inventory" not in ci_text
    assert "name: Knowledge migration guard" not in ci_text
    assert (
        "uv run soulmap audit-knowledge --max-knowledge-duplicates 519 > knowledge-inventory.txt"
        in ci_text
    )
    assert ci_text.count("uv run soulmap audit-knowledge ") == 1


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
    pinned_release_action = (
        "tuanductran/soulmap-ai/src/action@dbc92c971f3ef2639000c1481c23bb62eaec720f"
    )
    assert release_finalize_text.count(f"uses: {pinned_release_action}") == 2
    assert "uses: ./src/action" not in release_finalize_text
    assert "operation: release" in release_finalize_text
    assert "operation: tag" in release_finalize_text
    assert "target-sha:" in release_finalize_text
    assert "actions/upload-artifact@" in release_finalize_text
    assert "git push --follow-tags" not in release_prep_text


def test_direct_dev_packages_are_locked() -> None:
    lock_text = LOCKFILE.read_text(encoding="utf-8")

    for package_name in DIRECT_DEV_PACKAGES:
        assert re.search(
            rf'^name = "{re.escape(package_name)}"$', lock_text, re.MULTILINE
        )


def _workflow_action_versions(
    workflow_text: str, action_prefix: str
) -> list[str | None]:
    """Return each matching action step's direct ``with.version`` input.

    Parse only the indentation-based YAML subset used by workflow steps.
    """
    lines = workflow_text.splitlines()
    versions: list[str | None] = []

    for index, line in enumerate(lines):
        section = re.match(r"^(?P<indent> *)steps:\s*(?:#.*)?$", line)
        if section is None:
            continue

        section_indent = len(section.group("indent"))
        step_indent = section_indent + 2
        property_indent = step_indent + 2
        cursor = index + 1

        while cursor < len(lines):
            current = lines[cursor]
            current_indent = len(current) - len(current.lstrip(" "))
            if current.strip() and current_indent <= section_indent:
                break

            step = re.match(rf"^ {{{step_indent}}}-\s*(?P<first>.*)$", current)
            if step is None:
                cursor += 1
                continue

            step_lines = [step.group("first")]
            cursor += 1
            while cursor < len(lines):
                candidate = lines[cursor]
                if candidate.strip():
                    indent = len(candidate) - len(candidate.lstrip(" "))
                    is_next_step = indent == step_indent and re.match(
                        r"^-($|\s)", candidate[step_indent:]
                    )
                    if indent <= section_indent or is_next_step:
                        break
                step_lines.append(candidate)
                cursor += 1

            properties = [(property_indent, step_lines[0])]
            properties.extend(
                (len(value) - len(value.lstrip(" ")), value.lstrip(" "))
                for value in step_lines[1:]
                if value.strip()
            )
            uses_action = any(
                indent == property_indent
                and re.match(
                    rf"^uses:\s*{re.escape(action_prefix)}(?:@|\s|$)",
                    value,
                )
                for indent, value in properties
            )
            if not uses_action:
                continue

            with_indent = next(
                (
                    indent
                    for indent, value in properties
                    if indent == property_indent and value.strip() == "with:"
                ),
                None,
            )
            version: str | None = None
            if with_indent is not None:
                in_with = False
                for raw_line in step_lines[1:]:
                    if not raw_line.strip():
                        continue
                    indent = len(raw_line) - len(raw_line.lstrip(" "))
                    value = raw_line.lstrip(" ")
                    if indent == with_indent:
                        in_with = value.strip() == "with:"
                        continue
                    if in_with and indent == with_indent + 2:
                        match = re.match(
                            r'^version:\s*"([0-9]+\.[0-9]+\.[0-9]+)"\s*(?:#.*)?$',
                            value,
                        )
                        if match is not None:
                            version = match.group(1)
                            break
            versions.append(version)

    return versions


def test_workflow_action_version_parser_rejects_unpinned_or_misplaced_values() -> None:
    workflow_text = "\n".join(
        [
            "jobs:",
            "  test:",
            "    steps:",
            "      - if: always()",
            "        name: First setup",
            "        uses: astral-sh/setup-uv@v1",
            "        with:",
            '          version: "0.13.10"',
            "      - id: second-setup",
            "        uses: astral-sh/setup-uv@v1",
            "        env:",
            '          version: "0.13.10"',
            "      - name: Third setup",
            "        uses: astral-sh/setup-uv@v1",
            "        with:",
            '          version: "0.13.10"',
        ]
    )
    assert _workflow_action_versions(workflow_text, "astral-sh/setup-uv") == [
        "0.13.10",
        None,
        "0.13.10",
    ]


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

    uv_versions = [
        version
        for workflow_path in CI_WORKFLOWS
        for version in _workflow_action_versions(
            workflow_path.read_text(encoding="utf-8"),
            "astral-sh/setup-uv",
        )
    ]
    assert uv_versions, "CI must contain at least one setup-uv invocation"
    assert all(version is not None for version in uv_versions), (
        "every setup-uv invocation must provide with.version"
    )
    pinned_versions = {version for version in uv_versions if version is not None}
    assert len(pinned_versions) == 1
    uv_version = next(iter(pinned_versions))
    assert re.search(
        rf"^\| uv \| {re.escape(uv_version)} \(CI installer pin, "
        r"\d{4}-\d{2}-\d{2}\) \|",
        research_text,
        re.MULTILINE,
    )
    assert "| actionlint | 1.7.12 (CI binary pin) |" in research_text
