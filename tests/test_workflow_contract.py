"""Lightweight contract checks for GitHub Actions workflows."""

from pathlib import Path


def test_ci_workflow_covers_critical_quality_gates() -> None:
    content = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    for expected in [
        "if: github.event_name == 'pull_request'",
        "python -m tools.format",
        "autofix-ci/action@7a166d7532b277f34e16238930461bf77f9d7ed8",
        "raven-actions/actionlint@v2",
        "python -m tools.lint --skip-tests",
        "python -m pytest -q",
        "python tests/test_safety_evals.py",
        "python -m tools.eval_responses",
        "python -m tools.build_skill",
        "python -m tools.build_skill --skill",
        "python -m modules.markdown_contract --root .",
    ]:
        assert expected in content, (
            f"CI workflow missing critical quality gate: {expected}"
        )


def test_release_workflow_verifies_repo_and_builds_artifacts() -> None:
    content = Path(".github/workflows/release.yml").read_text(encoding="utf-8")

    for expected in [
        "python -m tools.lint",
        "python -m commitizen bump --yes",
        "python -m tools.build_skill",
        "python -m tools.build_skill --skill",
        "softprops/action-gh-release@v2",
    ]:
        assert expected in content, (
            f"Release workflow missing expected release contract step: {expected}"
        )
