import pytest

from soulmap.runtime.detectors.dependency_detector import analyze_dependency


def _user_messages(*texts: str) -> list[dict]:
    return [{"role": "user", "content": text} for text in texts]


def test_no_data_for_empty_history() -> None:
    result = analyze_dependency([])

    assert result["level"] == "NO_DATA"
    assert result["score"] == 0


def test_low_dependency_for_neutral_message() -> None:
    result = analyze_dependency(_user_messages("What's a good book about grief?"))

    assert result["level"] == "LOW_DEPENDENCY"


def test_high_dependency_for_english_keyword() -> None:
    result = analyze_dependency(
        _user_messages("You are the only one who truly understands me")
    )

    assert result["level"] == "HIGH_DEPENDENCY"


@pytest.mark.parametrize(
    "message",
    [
        "Chỉ có bạn mới hiểu tôi.",
        "Bạn là người duy nhất hiểu tôi.",
        "Tôi không biết sẽ làm gì nếu không có bạn.",
    ],
)
def test_high_dependency_for_accented_vietnamese_keyword(message: str) -> None:
    result = analyze_dependency(_user_messages(message))

    assert result["level"] == "HIGH_DEPENDENCY"
    assert any("dependency_keyword" in signal for signal in result["signals"])


@pytest.mark.parametrize(
    "message",
    [
        "Ban la nguoi duy nhat hieu toi, hay noi cho toi biet tuong lai cua toi.",
        "Chi co ban moi hieu toi thoi.",
    ],
)
def test_high_dependency_for_diacritic_stripped_vietnamese(message: str) -> None:
    """Regression coverage for the eval-flagged gap: Vietnamese without

    diacritics carries the same dependency signal as the accented form but
    was previously invisible to DEPENDENCY_KEYWORDS' literal matching.
    """
    result = analyze_dependency(_user_messages(message))

    assert result["level"] == "HIGH_DEPENDENCY"
    assert any("dependency_pattern" in signal for signal in result["signals"])


def test_no_false_positive_for_unrelated_diacritic_stripped_vietnamese() -> None:
    result = analyze_dependency(
        _user_messages("Toi rat vui vi hom nay troi dep va toi di choi voi ban be.")
    )

    assert result["level"] == "LOW_DEPENDENCY"


def test_isolation_signal_vietnamese() -> None:
    result = analyze_dependency(
        _user_messages("Tôi không muốn nói chuyện với người thật nữa.")
    )

    assert any("isolation_signal" in signal for signal in result["signals"])


def test_decision_seeking_vietnamese() -> None:
    result = analyze_dependency(_user_messages("Tôi nên làm gì đây?"))

    assert any("decision_seeking_count" in signal for signal in result["signals"])
