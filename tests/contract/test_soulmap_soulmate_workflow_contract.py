from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
ROOT_BUILDER = (
    REPO_ROOT / "src" / "soulmap" / "devtools" / "packaging" / "build_skill.py"
)
COMPOSED_BUILDER = (
    REPO_ROOT / "src" / "soulmap" / "devtools" / "packaging" / "composition.py"
)


def test_ci_builds_and_verifies_composed_artifacts() -> None:
    content = CI_WORKFLOW.read_text(encoding="utf-8")
    for marker in (
        "uv run soulmap build-composed --output-dir dist/soulmap-with-soulmate-ai",
        "scripts/verify_soulmap_with_soulmate.py",
        "scripts/verify_artifact_security.py \\",
        "dist/soulmap-with-soulmate-ai/soulmap-with-soulmate-ai.zip",
        "dist/soulmap-with-soulmate-ai/soulmap-with-soulmate-ai.skill",
    ):
        assert marker in content
    assert content.index("build-composed") < content.index(
        "verify_soulmap_with_soulmate.py"
    )
    assert content.index("verify_soulmap_with_soulmate.py") < content.index(
        "Audit composed artifact security"
    )
    build_job = content.split("\n  build:\n", maxsplit=1)[1]
    assert (
        "uv run soulmap build-composed --output-dir dist/soulmap-with-soulmate-ai"
        in build_job
    )
    assert build_job.index("build-composed") < build_job.index(
        "Verify build outputs and SHA-256 integrity"
    )
    assert build_job.index(
        "Verify build outputs and SHA-256 integrity"
    ) < build_job.index("Upload skill artifact")


def test_standalone_and_composed_builders_are_distinct() -> None:
    root_content = ROOT_BUILDER.read_text(encoding="utf-8")
    composed_content = COMPOSED_BUILDER.read_text(encoding="utf-8")
    assert "soulmap-ai.zip" in root_content
    assert "soulmap-with-soulmate-ai.zip" in composed_content
    assert "packages/soulmate/skills" not in root_content
    assert "SOULMATE_SKILLS_ROOT" in composed_content


def test_composed_builder_preserves_soulmate_namespace() -> None:
    content = COMPOSED_BUILDER.read_text(encoding="utf-8")
    for marker in (
        "soulmate/COMPOSITION.md",
        "soulmate/manifest.json",
        "soulmate/{entry['source']}",
        "SoulMap orchestration pipeline remains authoritative",
    ):
        assert marker in content
