from __future__ import annotations

import json
from pathlib import Path

import pytest

from soulmap.devtools.checks.p_level_governance import (
    main,
    metadata_from_body,
    p_level_from_title,
    pull_request_from_event,
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


# --- Behavior coverage for the paths the contract cases above do not reach ---
#
# The cases above prove the happy path and the headline failures. These cover
# how the check behaves when the event itself is unusable, and how it reports a
# blank field, because a governance gate that reports the wrong reason costs
# the author a CI cycle chasing the wrong line.


@pytest.mark.parametrize("level", ["P0", "P1", "P2", "P3"])
def test_every_documented_p_level_is_recognized(level: str) -> None:
    assert p_level_from_title(f"[{level}] fix(safety): something") == level


@pytest.mark.parametrize(
    "title",
    [
        "[P4] out of the documented range",
        "[p1] lowercase is not the documented form",
        "chore: [P1] tag must lead the title",
        "[P1]no space after the tag",
    ],
)
def test_malformed_p_level_tags_are_out_of_scope(title: str) -> None:
    """A malformed tag leaves the pull request ungoverned rather than failing.

    The check claims authority only over titles that match the documented
    form, so these are skipped rather than reported.
    """
    assert p_level_from_title(title) is None


def test_blank_field_does_not_swallow_the_following_line() -> None:
    """A blank value must not consume the next field's line.

    The field pattern's leading gap stops at the line break. With a plain
    whitespace class it crossed the newline, so a blank boundary captured the
    Evidence line as its value and the check then reported Evidence as the
    missing field, pointing the author at the wrong line.
    """
    metadata = metadata_from_body(_body(boundary="   "))

    assert metadata["Safety boundary"] == ""
    assert (
        metadata["Evidence"] == "Focused dependency test and the full repository gate."
    )
    assert metadata["Rollback"].startswith("Revert the maintenance commit")


@pytest.mark.parametrize("boundary", ["preserved", "PRESERVED", "Preserved"])
def test_boundary_comparison_is_case_insensitive(boundary: str) -> None:
    assert validate_pull_request("[P1] chore(deps): x", _body(boundary=boundary)) == []


@pytest.mark.parametrize("boundary", ["unchanged", "maybe", "   "])
def test_boundary_outside_the_two_documented_values_is_rejected(boundary: str) -> None:
    errors = validate_pull_request("[P1] chore(deps): x", _body(boundary=boundary))

    assert any("preserved" in error and "changed" in error for error in errors)


def test_changed_boundary_reports_each_missing_marker_separately() -> None:
    """Every missing marker is named, so the author fixes them in one pass."""
    errors = validate_pull_request("[P1] chore(deps): x", _body(boundary="changed"))

    assert len(errors) == 5
    assert any("## Safety change evidence" in error for error in errors)
    assert any("- **ADR:**" in error for error in errors)
    assert any("- **Near-miss regression:**" in error for error in errors)


def test_pull_request_from_event_reads_title_and_body() -> None:
    title, body = pull_request_from_event(
        {"pull_request": {"title": "[P1] x", "body": "some body"}}
    )

    assert (title, body) == ("[P1] x", "some body")


def test_null_body_becomes_an_empty_string() -> None:
    """GitHub sends a null body for a pull request opened with no description.

    That has to reach the metadata check as an empty string, failing with the
    specific missing-fields error rather than raising here.
    """
    _title, body = pull_request_from_event(
        {"pull_request": {"title": "[P1] x", "body": None}}
    )

    assert body == ""


@pytest.mark.parametrize(
    "payload", [{}, {"pull_request": None}, {"pull_request": "not a mapping"}]
)
def test_payload_without_a_pull_request_raises(payload: dict[str, object]) -> None:
    with pytest.raises(ValueError, match="does not contain a pull_request"):
        pull_request_from_event(payload)


def test_missing_title_raises() -> None:
    with pytest.raises(ValueError, match="title is missing or invalid"):
        pull_request_from_event({"pull_request": {"body": "x"}})


def test_non_string_body_raises() -> None:
    with pytest.raises(ValueError, match="body is invalid"):
        pull_request_from_event({"pull_request": {"title": "[P1] x", "body": 42}})


def _event_args(tmp_path: Path, title: str, body: str) -> list[str]:
    path = tmp_path / "event.json"
    path.write_text(
        json.dumps({"pull_request": {"title": title, "body": body}}), encoding="utf-8"
    )
    return ["--event-path", str(path)]


def test_untagged_pull_request_is_skipped_not_failed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(_event_args(tmp_path, "chore: bump deps", "")) == 0
    assert "skipped" in capsys.readouterr().out


def test_governance_failure_exits_one_and_reports_on_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args = _event_args(tmp_path, "[P1] chore(deps): x", "no metadata here")

    assert main(args) == 1
    captured = capsys.readouterr()
    assert "P-level governance failed for P1" in captured.err
    assert "require metadata fields" in captured.err


@pytest.mark.parametrize(
    "content", [None, "{not json", json.dumps({"action": "opened"})]
)
def test_unusable_event_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], content: str | None
) -> None:
    """An unusable event is distinct from a governance failure.

    Exit 2 keeps a CI misconfiguration from being read as a pull request that
    failed review.
    """
    path = tmp_path / "event.json"
    if content is not None:
        path.write_text(content, encoding="utf-8")

    assert main(["--event-path", str(path)]) == 2
    assert "Unable to read pull-request event" in capsys.readouterr().err
