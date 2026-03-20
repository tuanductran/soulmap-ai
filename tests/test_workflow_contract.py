"""Lightweight contract checks for GitHub Actions workflows."""

from pathlib import Path


def test_autofix_workflow_has_correct_name() -> None:
    """autofix-ci/action requires the workflow name to be exactly 'autofix.ci'.
    If the name is wrong, the action fails with a security error at runtime."""
    content = Path(".github/workflows/autofix.yml").read_text(encoding="utf-8")

    assert "name: autofix.ci" in content, (
        "autofix.yml must have 'name: autofix.ci' — this is a hard requirement "
        "from the autofix-ci/action. Any other name causes a security error."
    )
    assert "autofix-ci/action@7a166d7532b277f34e16238930461bf77f9d7ed8" in content
    assert "python -m tools.format" in content
    assert "on:\n  pull_request:" in content


def test_ci_workflow_covers_critical_quality_gates() -> None:
    content = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    # autofix must NOT be inside ci.yml — it belongs in autofix.yml
    assert "autofix-ci/action" not in content, (
        "autofix-ci/action must not be in ci.yml. "
        "It requires its own workflow named 'autofix.ci'."
    )

    for expected in [
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
