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
