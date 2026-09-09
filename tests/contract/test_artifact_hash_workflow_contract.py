from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
RELEASE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release.yml"

LIBRARY_COMMAND = "uv run soulmap library-manifest"
VERIFY_COMMAND = "uv run python scripts/verify_artifact_hashes.py"
EXTRACT_COMMAND = "uv run python scripts/verify_extracted_artifacts.py"
RELEASE_VERIFY_COMMAND = (
    "uv run soulmap release-verify --root . --output dist/release-verification.json"
)
MANIFEST_PATH = "dist/soulmap-ai-library.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_verify_before_final_manifest_upload(content: str) -> None:
    assert content.index(LIBRARY_COMMAND) < content.index(VERIFY_COMMAND)
    assert content.index(VERIFY_COMMAND) < content.index(EXTRACT_COMMAND)
    assert content.index(EXTRACT_COMMAND) < content.rindex(MANIFEST_PATH)


def test_ci_build_job_verifies_and_uploads_library_manifest() -> None:
    content = _read(CI_WORKFLOW)

    assert "name: Build Library distribution artifacts" in content
    assert LIBRARY_COMMAND in content
    assert VERIFY_COMMAND in content
    assert EXTRACT_COMMAND in content
    assert MANIFEST_PATH in content
    _assert_verify_before_final_manifest_upload(content)


def test_release_workflow_uses_unified_release_verification_gate() -> None:
    content = _read(RELEASE_WORKFLOW)

    assert RELEASE_VERIFY_COMMAND in content
    assert "uses: actions/upload-artifact@v4" in content
    assert "release-verification.json" in content
    assert content.index(RELEASE_VERIFY_COMMAND) < content.index(
        "git push --follow-tags"
    )
    assert content.index(RELEASE_VERIFY_COMMAND) < content.index(
        "softprops/action-gh-release@v3.0.3"
    )
