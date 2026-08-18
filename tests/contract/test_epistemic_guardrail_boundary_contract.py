from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills"
EPISTEMIC = SKILLS_ROOT / "meta" / "epistemic-guardrails.md"

# These surfaces are repository-only and are deliberately absent from shipped
# SoulMap Skills artifacts. A shipped skill may describe behavior, but must not
# depend on implementation, test, engineering, or maintainer files.
FORBIDDEN_SHIPPED_REFERENCES = (
    "src/soulmap/",
    "docs/engineering/",
    "tests/",
    ".claude/",
    ".github/",
    "templates/",
    "scripts/",
    "library/",
    "pyproject.toml",
    "uv.lock",
    ".py",
)


def test_epistemic_skill_uses_doctrine_only_for_its_enforcement_boundary() -> None:
    content = EPISTEMIC.read_text(encoding="utf-8")

    assert "## Enforcement Boundary" in content
    assert "doctrine and" in content
    assert "review guidance" in content
    assert "Evaluate the whole exchange" in content


def test_shipped_skills_do_not_reference_repository_only_surfaces() -> None:
    violations: list[str] = []

    for path in sorted(SKILLS_ROOT.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_SHIPPED_REFERENCES:
            if forbidden in content:
                violations.append(
                    f"{path.relative_to(REPO_ROOT)} contains {forbidden!r}"
                )

    assert not violations, "\n".join(violations)
