from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EPISTEMIC = REPO_ROOT / "skills" / "meta" / "epistemic-guardrails.md"
MATRIX = REPO_ROOT / "docs" / "engineering" / "safety-enforcement-matrix.md"
SAFETY_CONTRACT = (
    REPO_ROOT / "src" / "soulmap" / "runtime" / "guards" / "response_safety_contract.py"
)


def test_epistemic_skill_states_runtime_enforcement_boundary() -> None:
    content = EPISTEMIC.read_text(encoding="utf-8")

    assert "## Enforcement Boundary" in content
    assert "doctrine and review/evaluation guidance" in content
    assert "does not currently verify every framing marker" in content
    assert "docs/engineering/safety-enforcement-matrix.md" in content
    assert "response_safety_contract.py" in content


def test_epistemic_boundary_points_to_existing_runtime_contract_and_matrix() -> None:
    matrix = MATRIX.read_text(encoding="utf-8")
    safety_contract = SAFETY_CONTRACT.read_text(encoding="utf-8")

    assert "Epistemic guardrails for spiritual content" in matrix
    assert "partial" in matrix
    for category in (
        "diagnosis",
        "prediction_as_fact",
        "dependency_reinforcement",
        "guru_positioning",
        "excessive_certainty",
        "loss_of_independence",
    ):
        assert f'"{category}"' in safety_contract or f'("{category}"' in safety_contract
