from soulmap.runtime.detectors import direction_detector, pattern_detector


def test_direction_scoring_uses_markdown_authored_weights() -> None:
    original = dict(direction_detector._DIRECTION_RULES)
    try:
        direction_detector._DIRECTION_RULES.update(
            {
                "lostness": "7",
                "meaning_void": "3",
                "should_vs_want": "2",
                "comparison": "2",
                "transition": "2",
                "misalignment": "2",
                "minimum detection score": "7",
                "sustained history match": "1",
                "recent user history window": "4",
                "sustained lostness signal limit": "8",
                "sustained meaning signal limit": "6",
                "sustained transition signal limit": "6",
            }
        )
        result = direction_detector.detect_direction_need("i feel lost")
        assert result["score"] == 7
        assert result["direction_detected"] is True
    finally:
        direction_detector._DIRECTION_RULES.clear()
        direction_detector._DIRECTION_RULES.update(original)


def test_pattern_scoring_uses_markdown_authored_weights() -> None:
    original = dict(pattern_detector._PATTERN_RULES)
    try:
        pattern_detector._PATTERN_RULES.update(
            {
                "Keyword signal weight": "7",
                "Cycle phrase weight": "3",
                "Minimum pattern score": "7",
                "Minimum user messages": "2",
                "Combination threshold": "2",
            }
        )
        result = pattern_detector.detect_patterns(
            [
                {"role": "user", "content": "people always do this to me"},
                {"role": "user", "content": "they always repeat it"},
            ]
        )
        assert result["patterns_detected"][0]["score"] == 7
    finally:
        pattern_detector._PATTERN_RULES.clear()
        pattern_detector._PATTERN_RULES.update(original)


def test_direction_and_pattern_sources_are_registered_runtime_knowledge() -> None:
    assert (
        direction_detector.runtime_skill_path("life-direction").name
        == "life-direction.md"
    )
    assert (
        pattern_detector.runtime_skill_path("pattern-mapper").name
        == "pattern-mapper.md"
    )
