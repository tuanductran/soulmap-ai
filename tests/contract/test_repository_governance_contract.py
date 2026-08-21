from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEOWNERS = REPO_ROOT / ".github" / "CODEOWNERS"


def test_codeowners_covers_critical_soulmap_surfaces() -> None:
    content = CODEOWNERS.read_text(encoding="utf-8")

    assert "* @tuanductran" in content
    for path in (
        "/AGENTS.md @tuanductran",
        "/SKILL.md @tuanductran",
        "/skills/ @tuanductran",
        "/reference/ @tuanductran",
        "/src/soulmap/runtime/ @tuanductran",
        "/.github/ @tuanductran",
    ):
        assert path in content


def test_codeowners_states_that_enforcement_is_a_github_setting() -> None:
    content = CODEOWNERS.read_text(encoding="utf-8")

    normalized = content.lower()
    assert "branch protection" in normalized
    assert "required review" in normalized
