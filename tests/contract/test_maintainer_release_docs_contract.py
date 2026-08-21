from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEV_DOC = REPO_ROOT / "docs" / "engineering" / "DEV.md"
TESTER_DOC = REPO_ROOT / "docs" / "engineering" / "TESTER.md"
RELEASE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release.yml"


REQUIRED_ARTIFACT_COMMANDS = (
    "uv run soulmap library-manifest",
    "uv run python scripts/verify_artifact_hashes.py",
    "uv run python scripts/verify_extracted_artifacts.py",
    "uv run python scripts/verify_artifact_security.py",
)


def test_release_docs_describe_all_current_artifact_steps() -> None:
    dev_text = DEV_DOC.read_text(encoding="utf-8")
    tester_text = TESTER_DOC.read_text(encoding="utf-8")
    workflow_text = RELEASE_WORKFLOW.read_text(encoding="utf-8")

    for command in REQUIRED_ARTIFACT_COMMANDS:
        assert command in tester_text
        assert command in workflow_text

    assert "uv run soulmap catalog-parity" in workflow_text
    assert "versioned Library manifest" in dev_text
    assert "Verifying artifact SHA-256 integrity" in dev_text
    assert "Verifying extracted ZIP and `.skill` boundaries" in dev_text
    assert "uploading all three artifacts" in dev_text


def test_release_docs_name_the_manifest_artifact() -> None:
    dev_text = DEV_DOC.read_text(encoding="utf-8")
    tester_text = TESTER_DOC.read_text(encoding="utf-8")

    for content in (dev_text, tester_text):
        assert "dist/soulmap-ai-library.json" in content
        assert "SHA-256" in content
