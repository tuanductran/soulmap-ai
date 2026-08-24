from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "weekly-governance.yml"
WEEKLY_GUIDE = REPO_ROOT / "docs" / "operations" / "weekly-governance-review.md"
CLAUDE_PILOT = REPO_ROOT / "docs" / "operations" / "p2-claude-private-pilot.md"

WEEKLY_COMMANDS = (
    "actionlint",
    "uv sync --locked --python 3.11",
    "uv lock --check",
    "tests/contract/test_p_level_governance.py",
    "tests/contract/test_dependency_refresh_process_contract.py",
    "tests/contract/test_toolchain_support_contract.py",
    "uv run soulmap audit-knowledge",
    "uv run python tests/eval_regression/test_safety_evals.py",
    "uv run python scripts/pytest_diagnostics.py",
    "uv run deptry .",
    "uv run soulmap library-manifest",
    "uv run python scripts/verify_artifact_hashes.py",
    "uv run python scripts/verify_extracted_artifacts.py",
)

SCENARIOS = (
    "Tier 1 crisis handling",
    "Dependency redirect",
    "Diagnosis refusal",
    "Prediction refusal",
    "Instruction-disclosure refusal",
    "Jailbreak refusal",
    "Ordinary mirror interaction",
)


def test_weekly_workflow_is_scheduled_deterministic_and_non_mutating() -> None:
    content = WORKFLOW.read_text(encoding="utf-8")

    assert 'cron: "17 5 * * 1"' in content
    assert "workflow_dispatch:" in content
    assert "permissions:\n  contents: read" in content
    assert "weekly-governance-evidence" in content
    for command in WEEKLY_COMMANDS:
        assert command in content
    for forbidden in ("gh pr merge", "gh pr create", "uv lock --upgrade", "git tag"):
        assert forbidden not in content


def test_weekly_governance_guide_matches_workflow_boundary() -> None:
    content = WEEKLY_GUIDE.read_text(encoding="utf-8")

    assert "Monday at 05:17 UTC" in content
    assert "weekly-governance-evidence" in content
    assert "never updates a" in content
    assert "or creates a release" in content
    assert "dependency-refresh.md" in content


def test_claude_private_pilot_preserves_all_required_safety_scenarios() -> None:
    content = CLAUDE_PILOT.read_text(encoding="utf-8")

    assert "private/test deployment pilot" in content
    assert "dist/soulmap-ai.skill" in content
    for scenario in SCENARIOS:
        assert scenario in content
    assert "Do not commit credentials" in content
    assert "blocks rollout immediately" in content
    assert "P0 safety issue" in content
