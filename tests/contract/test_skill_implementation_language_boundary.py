from pathlib import Path

from soulmap.devtools.checks.skills_boundary import audit

ROOT = Path(__file__).resolve().parents[2]


def test_shipped_knowledge_has_no_implementation_language_references() -> None:
    """Every text member eligible for packaging stays implementation-neutral."""
    violations = audit(ROOT)
    assert not violations, (
        "Shipped package content contains implementation-language or repository-only "
        f"references: {violations}"
    )
