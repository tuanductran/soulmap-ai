from soulmap.runtime.detectors.visibility_fear_detector import (
    detect_visibility_fear,
)


def test_visibility_fear_uses_markdown_direct_signal() -> None:
    result = detect_visibility_fear("I don't want to be seen")

    assert result["visibility_fear_detected"] is True
    assert result["score"] == 3


def test_visibility_fear_uses_markdown_secondary_groups() -> None:
    result = detect_visibility_fear("I go quiet when I share my work")

    assert result["visibility_fear_detected"] is True
    assert result["score"] == 2
    assert result["signals"] == ["shrinking + public expression context"]


def test_attributed_third_party_visibility_fear_does_not_trigger() -> None:
    result = detect_visibility_fear(
        'My friend said, "I do not want to be seen and I am afraid to post."'
    )

    assert result["visibility_fear_detected"] is False
    assert result["score"] == 0
    assert result["signals"] == []


def test_user_visibility_fear_after_attributed_quote_is_preserved() -> None:
    result = detect_visibility_fear(
        'My friend said, "I do not want to be seen." '
        "I do not want to be seen either."
    )

    assert result["visibility_fear_detected"] is True
