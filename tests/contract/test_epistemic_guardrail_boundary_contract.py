from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills"
EPISTEMIC = SKILLS_ROOT / "meta" / "epistemic-guardrails.md"
SYMBOLIC_REPORT = SKILLS_ROOT / "spiritual" / "symbolic-report-handling.md"

# These surfaces are repository-only and are deliberately absent from shipped
# SoulMap Skills artifacts. A shipped skill may describe behavior, but must not
# depend on implementation, test, engineering, or maintainer files.
FORBIDDEN_SHIPPED_REFERENCES = (
    "src/soulmap/",
    "docs/",
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


def test_symbolic_report_handling_keeps_reports_reflective_and_private() -> None:
    content = SYMBOLIC_REPORT.read_text(encoding="utf-8")

    for marker in (
        "Confirm the frame",
        "Minimize personal data",
        "Remove prediction and prescription",
        "Return authorship to the user",
        "Never use a symbolic report to",
    ):
        assert marker in content

    assert "birth dates" in content
    assert "guaranteed life path" in content
    assert "diagnose a mental or physical condition" in content


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
