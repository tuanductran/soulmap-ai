from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
RELEASE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release.yml"

LIBRARY_COMMAND = "uv run soulmap library-manifest"
VERIFY_COMMAND = "uv run python scripts/verify_artifact_hashes.py"
EXTRACT_COMMAND = "uv run python scripts/verify_extracted_artifacts.py"
SECURITY_COMMAND = "uv run python scripts/verify_artifact_security.py"
MANIFEST_PATH = "dist/soulmap-ai-library.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_order(content: str, *markers: str) -> None:
    positions = [content.index(marker) for marker in markers]
    assert positions == sorted(positions)


def _assert_verify_before_final_manifest_upload(content: str) -> None:
    assert content.index(LIBRARY_COMMAND) < content.index(VERIFY_COMMAND)
    assert content.index(VERIFY_COMMAND) < content.index(EXTRACT_COMMAND)
    assert content.index(EXTRACT_COMMAND) < content.index(SECURITY_COMMAND)
    assert content.index(SECURITY_COMMAND) < content.rindex(MANIFEST_PATH)


def test_ci_build_job_verifies_and_uploads_library_manifest() -> None:
    content = _read(CI_WORKFLOW)

    assert "name: Build Library distribution artifacts" in content
    assert LIBRARY_COMMAND in content
    assert VERIFY_COMMAND in content
    assert EXTRACT_COMMAND in content
    assert SECURITY_COMMAND in content
    assert MANIFEST_PATH in content
    build_job = content.split("\n  build:\n", maxsplit=1)[1]
    _assert_verify_before_final_manifest_upload(build_job)


def test_release_workflow_verifies_before_uploading_library_manifest() -> None:
    content = _read(RELEASE_WORKFLOW)

    assert LIBRARY_COMMAND in content
    assert VERIFY_COMMAND in content
    assert EXTRACT_COMMAND in content
    assert SECURITY_COMMAND in content
    assert MANIFEST_PATH in content
    assert "id-token: write" in content
    assert "attestations: write" in content
    assert "uses: actions/attest@v4" in content
    assert "permissions:\n  contents: read" in content
    assert "if: github.ref == 'refs/heads/main'" in content
    assert "contents: write" in content
    assert re.search(
        r"uses: softprops/action-gh-release@[0-9a-f]{40}(?:\s+# v[0-9.]+)?",
        content,
    )
    assert "dist/soulmap-ai.zip" in content
    assert "dist/soulmap-ai.skill" in content
    _assert_verify_before_final_manifest_upload(content)
    _assert_order(
        content,
        EXTRACT_COMMAND,
        "uses: actions/attest@v4",
        "name: Push bump commit + tag",
    )
