from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_release_immutability_verification_is_owned_by_python_action() -> None:
    action = (ROOT / "src" / "action" / "__main__.py").read_text(encoding="utf-8")
    metadata = (ROOT / "src" / "action" / "action.yml").read_text(encoding="utf-8")
    assert "run_verify_release_immutability" in action
    assert "from urllib.request import Request, urlopen" in action
    assert "immutable" in action
    assert "verify-release-immutability" in metadata
    assert "required: false" in metadata


def test_release_immutability_workflow_is_manual_read_only_and_uses_action() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "release-immutability-audit.yml"
    ).read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "contents: read" in workflow
    assert "uses: ./src/action" in workflow
    assert "operation: verify-release-immutability" in workflow
    assert "verify_release_immutability.py" not in workflow
    assert "ubuntu-26.04" in workflow
    assert not (ROOT / ".github" / "python" / "verify_release_immutability.py").exists()
