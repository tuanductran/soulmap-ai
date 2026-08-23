from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "soulmate-skills-ci.yml"
CONTRIBUTING = REPO_ROOT / "packages" / "soulmate" / "CONTRIBUTING.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_order(content: str, *markers: str) -> None:
    positions = [content.index(marker) for marker in markers]
    assert positions == sorted(positions)


def test_soulmate_skills_workflow_is_pr_only_and_read_only() -> None:
    content = _read(WORKFLOW)

    assert "pull_request:" in content
    assert "workflow_dispatch:" not in content
    assert "permissions:\n  contents: read" in content
    assert "contents: write" not in content
    assert "publish" not in content.casefold()
    assert "gh release" not in content
    assert "pypi" not in content.casefold()
    assert "actions/checkout@v7" in content
    assert "./.github/actions/setup-uv" in content
    assert 'python-version: "3.11"' in content
    assert "uv sync --locked --python 3.11" in content
    assert "scripts/build_soulmate_skills.py" in content
    assert "scripts/verify_soulmate_skills.py" in content
    assert "scripts/verify_soulmate_consumer_sync.py --check" in content
    assert "tests/unit/test_soulmate_skills_artifacts.py" in content
    assert "actions/upload-artifact@v7" in content
    assert "dist/soulmate-skills/" in content

    _assert_order(
        content,
        "uv run soulmap markdown-contract --root .",
        "uv run python scripts/verify_soulmate_consumer_sync.py --check",
        "uv run python scripts/build_soulmate_skills.py",
        "uv run python scripts/verify_soulmate_skills.py",
        "Rebuild for deterministic parity",
        "Run artifact contract and security tests",
        "Upload verified review artifact",
    )


def test_soulmate_skills_workflow_paths_cover_canonical_inputs() -> None:
    content = _read(WORKFLOW)

    for path in (
        "packages/soulmate/**",
        "scripts/build_soulmate_skills.py",
        "scripts/verify_soulmate_skills.py",
        "scripts/verify_soulmate_consumer_sync.py",
        "src/soulmap/runtime/knowledge/soulmate_consumer_scope.json",
        "src/soulmap/runtime/knowledge/_soulmate_consumer_scope.py",
        "src/soulmap/runtime/knowledge/soulmate_skills.py",
        "tests/contract/test_soulmate_skills_artifact_workflow_contract.py",
        "tests/contract/test_soulmate_consumer_sync_contract.py",
        "tests/contract/test_soulmate_adapter_contract.py",
    ):
        assert path in content


def test_custom_soulmate_skill_contribution_guide_is_package_owned() -> None:
    content = _read(CONTRIBUTING)

    assert "# Contributing Soulmate skills" in content
    assert "packages/soulmate/skills/foundation/<skill-name>.md" in content
    assert "packages/soulmate/skills/manifest.json" in content
    assert "soulmate.companion.example" in content
    assert "uv run python scripts/build_soulmate_skills.py" in content
    assert "uv run python scripts/verify_soulmate_skills.py" in content
    assert "root `skills/`" in content
    assert "Soulmate → never SoulMap" in content
    assert "dynamic plugin registry" in content
    assert "registry package" in content
    assert "Do not add credentials" in content
