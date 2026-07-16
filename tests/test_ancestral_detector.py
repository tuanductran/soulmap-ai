from soulmap.runtime.detectors.ancestral_detector import detect_ancestral


def test_ancestral_uses_markdown_direct_signal() -> None:
    result = detect_ancestral("This runs in my family")

    assert result["ancestral_detected"] is True
    assert result["score"] == 3


def test_ancestral_uses_markdown_secondary_groups() -> None:
    result = detect_ancestral("My mother always did the same thing")

    assert result["ancestral_detected"] is True
    assert result["score"] == 2
    assert result["signals"] == ["parent_ref + pattern_language"]
