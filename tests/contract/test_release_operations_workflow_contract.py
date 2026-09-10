"""Contract tests for release operational workflows."""

from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_release_workflow_publishes_provenance_and_health_before_promotion() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text()

    assert "soulmap release-verify" in workflow
    assert "soulmap release-provenance" in workflow
    assert "soulmap release-health" in workflow
    assert "dist/release-provenance.json" in workflow
    assert workflow.index("Verify release health") < workflow.index("Push bump commit + tag")
    assert workflow.index("Push bump commit + tag") < workflow.index("Create GitHub Release")


def test_rollback_workflow_is_read_only_and_checks_known_good_tag() -> None:
    workflow = (ROOT / ".github" / "workflows" / "rollback-verify.yml").read_text()

    assert "release_ref:" in workflow
    assert "contents: read" in workflow
    assert "release-verify" in workflow
    assert 'test "v${version}" = "${{ inputs.release_ref }}"' in workflow
    assert "rollback_ready" in workflow
    assert "contents: write" not in workflow
