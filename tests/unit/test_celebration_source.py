from soulmap.runtime.knowledge.celebration_source import load_celebration_rules
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path


def test_celebration_rules_load_scoring_from_markdown() -> None:
    rules = load_celebration_rules()
    text = runtime_skill_path("integration-celebration").read_text(encoding="utf-8")

    assert "| Win or completion weight | 3 |" in text
    assert "| Relief after difficulty weight | 3 |" in text
    assert "| Gratitude weight | 2 |" in text
    assert "| Recognized progress weight | 2 |" in text
    assert "| Detection threshold | 2 |" in text
    assert "| Negative override penalty | 2 |" in text
    assert "| Strength threshold | 4 |" in text
    assert "| Confirmation score | 2 |" in text

    assert rules.score_weights == {
        "win or completion": 3,
        "relief after difficulty": 3,
        "gratitude": 2,
        "recognized progress": 2,
    }
    assert rules.threshold == 2
    assert rules.negative_override_penalty == 2
    assert rules.strength_threshold == 4
    assert rules.confirmation_score == 2
    assert "it doesn't feel real" in rules.negative_overrides
    assert "what you just" in rules.confirmation_assistant_anchors


def test_celebration_guidance_uses_plain_language_labels() -> None:
    path = runtime_skill_path("integration-celebration")
    text = path.read_text(encoding="utf-8")

    assert "| Not detected |" in text
    assert "| Detected |" in text
    assert "| Closing |" in text
    for implementation_row in ("| not_detected |", "| detected |", "| closing |"):
        assert implementation_row not in text
    assert set(load_celebration_rules().guidance) == {
        "not_detected",
        "detected",
        "closing",
    }
