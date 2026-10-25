from soulmap.runtime.knowledge.celebration_source import load_celebration_rules
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path


def test_celebration_rules_use_python_owned_scoring() -> None:
    rules = load_celebration_rules()
    text = runtime_skill_path("integration-celebration").read_text(encoding="utf-8")

    assert "Score weight: win or completion" not in text
    assert "Detection threshold" not in text
    assert "Strong-signal threshold" not in text
    assert "Confirmation score" not in text

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
