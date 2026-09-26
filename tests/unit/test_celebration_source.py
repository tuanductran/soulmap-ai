from soulmap.runtime.knowledge.celebration_source import load_celebration_rules


def test_celebration_rules_match_markdown_contract() -> None:
    rules = load_celebration_rules()

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
