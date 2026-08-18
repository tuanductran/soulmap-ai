from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKLIST = REPO_ROOT / "docs" / "operations" / "dependency-refresh.md"
ROADMAP = REPO_ROOT / "docs" / "ROADMAP.md"
COMPATIBILITY = REPO_ROOT / "docs" / "engineering" / "package-compatibility-research.md"


REQUIRED_COMMANDS = (
    "uv tree --depth 1",
    "uv lock --check",
    "uv run soulmap test -n auto -q",
    "uv run python scripts/verify_artifact_hashes.py",
    "uv run deptry .",
)


REQUIRED_POLICY_ANCHORS = (
    "security advisory",
    "deprecation warning",
    "Python 3.11",
    "pytest-randomly seed",
    "xdist worker count",
    "pytest-timeout",
    "one maintenance purpose per pull request",
    "do not add a scanner",
    "platform adapters",
)


def test_dependency_refresh_checklist_exists_and_covers_required_commands() -> None:
    content = CHECKLIST.read_text(encoding="utf-8")

    for command in REQUIRED_COMMANDS:
        assert command in content

    for anchor in REQUIRED_POLICY_ANCHORS:
        assert anchor in content


def test_dependency_refresh_checklist_preserves_upstream_references() -> None:
    content = CHECKLIST.read_text(encoding="utf-8")

    assert "docs.astral.sh/uv/concepts/projects/sync" in content
    assert "docs.GitHub.com/en/code-security/concepts/supply-chain-security" in content
    assert "package-compatibility-research.md" in content


def test_phase12_points_to_dependency_refresh_process() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    compatibility = COMPATIBILITY.read_text(encoding="utf-8")

    assert "dependency-refresh.md" in roadmap
    assert "dependency-refresh.md" in compatibility


def test_checklist_does_not_expand_phase12_scope() -> None:
    content = CHECKLIST.read_text(encoding="utf-8")

    assert "does not authorize a new runtime dependency" in content
    assert "Python-version expansion" in content
    assert "semantic safety classifier" in content
    assert "platform adapter" in content
