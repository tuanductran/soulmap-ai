from soulmap.runtime.detectors.emotional_intensity_detector import (
    check_escalation,
)


def test_check_escalation_uses_markdown_intensity_modifiers() -> None:
    history = [
        {"role": "user", "content": "I am worried"},
        {"role": "user", "content": "Everything is happening"},
        {"role": "user", "content": "I can't deal with all of it"},
    ]

    assert check_escalation(history) is True
