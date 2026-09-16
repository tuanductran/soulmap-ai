from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
RELEASE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release.yml"
RELEASE_FINALIZE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release-finalize.yml"

LIBRARY_COMMAND = "uv run soulmap library-manifest"
VERIFY_COMMAND = "uv run python scripts/verify_artifact_hashes.py"
EXTRACT_COMMAND = "uv run python scripts/verify_extracted_artifacts.py"
RELEASE_VERIFY_COMMAND = (
    "uv run soulmap release-verify --root . --output dist/release-verification.json"
)
MANIFEST_PATH = "dist/soulmap-ai-library.json"
UPLOAD_ARTIFACT_SHA = "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"
RELEASE_ACTION_SHA = "efb35369e0ad2af669f228072c1b0d510eae64"


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


def test_release_prep_defers_publication_to_finalize_workflow() -> None:
    content = _read(RELEASE_WORKFLOW)

    assert "workflow_dispatch" in content
    assert "git push --set-upstream origin" in content
    assert "gh pr create" in content
    assert "release-finalize" in content
    assert "softprops/action-gh-release" not in content
    assert "actions/upload-artifact" not in content
    assert "git push --follow-tags" not in content


def test_release_finalize_verifies_artifacts_before_publication() -> None:
    content = _read(RELEASE_FINALIZE_WORKFLOW)

    assert RELEASE_VERIFY_COMMAND in content
    assert f"uses: actions/upload-artifact@{UPLOAD_ARTIFACT_SHA}" in content
    assert f"uses: softprops/action-gh-release@{RELEASE_ACTION_SHA}" in content
    assert "dist/release-verification.json" in content
    assert "dist/release-provenance.json" in content
    assert content.index(LIBRARY_COMMAND) < content.index(VERIFY_COMMAND)
    assert content.index(VERIFY_COMMAND) < content.index(EXTRACT_COMMAND)
    assert content.index(EXTRACT_COMMAND) < content.index(
        f"uses: actions/upload-artifact@{UPLOAD_ARTIFACT_SHA}"
    )
    assert content.index(
        f"uses: actions/upload-artifact@{UPLOAD_ARTIFACT_SHA}"
    ) < content.index(f"uses: softprops/action-gh-release@{RELEASE_ACTION_SHA}")
