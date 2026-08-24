from __future__ import annotations

import json
from pathlib import Path

import pytest

from soulmap.devtools.checks.p_level_governance import (
    main,
    metadata_from_body,
    p_level_from_title,
    validate_pull_request,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "p-level-governance.yml"
POLICY = REPO_ROOT / "docs" / "operations" / "p-level-governance.md"
PLAN = REPO_ROOT / "docs" / "operations" / "p1-dependency-advisory-refresh-plan.md"
DEPENDENCY_REFRESH = REPO_ROOT / "docs" / "operations" / "dependency-refresh.md"


def _body(
    *,
    priority: str = "P1",
    boundary: str = "preserved",
    evidence: str = "Focused dependency test and the full repository gate.",
    rollback: str = "Revert the maintenance commit and restore the previous lockfile.",
    change_evidence: str = "",
) -> str:
    return "\n".join(
        (
            "## P-level governance",
            f"- **Priority:** {priority}",
            f"- **Safety boundary:** {boundary}",
            f"- **Evidence:** {evidence}",
            f"- **Rollback:** {rollback}",
            change_evidence,
        )
    )


def test_non_p_level_pull_request_is_not_subject_to_metadata_contract() -> None:
    assert validate_pull_request("docs: clarify contributor guide", "") == []
    assert p_level_from_title("docs: clarify contributor guide") is None


def test_p_level_metadata_is_parsed_and_matches_title() -> None:
    body = _body()

    assert p_level_from_title("[P1] chore(deps): controlled refresh") == "P1"
    assert metadata_from_body(body)["Safety boundary"] == "preserved"
    assert validate_pull_request("[P1] chore(deps): controlled refresh", body) == []


def test_p_level_metadata_rejects_missing_or_mismatched_governance() -> None:
    errors = validate_pull_request("[P1] chore(deps): controlled refresh", "## Summary")
    assert "Priority" in errors[0]

    errors = validate_pull_request(
        "[P1] chore(deps): controlled refresh", _body(priority="P2")
    )
    assert "must match the title" in errors[0]


def test_p_level_metadata_requires_meaningful_evidence_and_rollback() -> None:
    errors = validate_pull_request(
        "[P1] chore(deps): controlled refresh",
        _body(evidence="n/a", rollback="Keep the change."),
    )

    assert any("Evidence" in error for error in errors)
    assert any("Rollback" in error for error in errors)


def test_changed_safety_boundary_requires_explicit_evidence_bundle() -> None:
    title = "[P0] fix(safety): narrow reviewed phrase gap"
    errors = validate_pull_request(title, _body(priority="P0", boundary="changed"))
    assert any("Safety change evidence" in error for error in errors)

    change_evidence = "\n".join(
        (
            "## Safety change evidence",
            "- **ADR:** not required: no architecture reversal.",
            "- **Positive regression:** reviewed phrase is blocked.",
            "- **Near-miss regression:** reflective phrasing remains allowed.",
            "- **Safety matrix:** matrix row updated.",
        )
    )
    assert (
        validate_pull_request(
            title,
            _body(priority="P0", boundary="changed", change_evidence=change_evidence),
        )
        == []
    )


def test_event_checker_returns_expected_exit_codes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    event_path = tmp_path / "event.json"
    event_path.write_text(
        json.dumps(
            {
                "pull_request": {
                    "title": "[P1] chore(deps): controlled refresh",
                    "body": _body(),
                }
            }
        ),
        encoding="utf-8",
    )

    assert main(["--event-path", str(event_path)]) == 0

    captured = capsys.readouterr()
    assert "passed for P1" in captured.out


def test_governance_workflow_template_and_p1_plan_are_contractual() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    policy = POLICY.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    dependency_refresh = DEPENDENCY_REFRESH.read_text(encoding="utf-8")

    assert "pull_request:" in workflow
    assert "scripts/check_p_level_pr.py" in workflow
    assert "P-level safety governance" in workflow
    for field in ("Priority", "Safety boundary", "Evidence", "Rollback"):
        assert field in policy
    assert "Safety change evidence" in policy
    assert "dependency-refresh.md" in policy
    assert "p1-dependency-advisory-refresh-plan.md" in dependency_refresh
    for marker in (
        "Entry criteria",
        "Execution sequence",
        "Required validation",
        "Rollback",
    ):
        assert marker in plan
