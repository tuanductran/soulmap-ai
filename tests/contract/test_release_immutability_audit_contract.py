from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_release_immutability_audit_script_exists_and_is_stdlib_only() -> None:
    script = (ROOT / ".github" / "python" / "verify_release_immutability.py").read_text(
        encoding="utf-8"
    )
    assert "urllib.request" in script
    assert "immutable" in script
    assert "third-party" not in script.lower()


def test_release_immutability_audit_workflow_is_manual_and_read_only() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "release-immutability-audit.yml"
    ).read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "contents: read" in workflow
    assert "verify_release_immutability.py" in workflow
    assert "ubuntu-24.04" in workflow
