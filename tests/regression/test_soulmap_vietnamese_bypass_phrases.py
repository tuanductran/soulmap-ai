"""Regression coverage for authored Vietnamese spiritual-bypass phrase packs.

These phrases are written for SoulMap's safety contract. They are not copied from
source material and are intentionally tested as secondary-layer detection only.
"""

import pytest

from soulmap.runtime.detectors.spiritual_bypass_detector import detect_bypass


@pytest.mark.parametrize(
    ("message", "expected_type"),
    [
        (
            "Mọi chuyện xảy ra đều có lý do, mình chỉ cần biết ơn là được.",
            "dismissing_pain",
        ),
        ("Mình đã chấp nhận rồi, mình không còn giận nữa.", "premature_acceptance"),
        ("Mình là empath nên người khác không thể hiểu mình.", "spiritual_inflation"),
        ("Họ đến để dạy mình, vũ trụ đưa họ đến với mình.", "bypassing_accountability"),
    ],
)
def test_authored_vietnamese_bypass_phrase_packs_are_typed(
    message: str, expected_type: str
) -> None:
    result = detect_bypass(message)

    assert result["bypass_detected"] is True
    assert result["bypass_type"] == expected_type
    assert "secondary layer" in str(result["note"]).lower()


def test_vietnamese_genuine_integration_signals_reduce_bypass_score() -> None:
    result = detect_bypass(
        "Nó làm mình mạnh mẽ hơn, nhưng mình vẫn đang xử lý và vẫn còn cảm thấy "
        "chuyện này phức tạp."
    )

    assert result["bypass_detected"] is False


def test_neutral_vietnamese_spiritual_language_is_not_flagged() -> None:
    result = detect_bypass(
        "Mình đang đọc về thiền và muốn quan sát trải nghiệm của mình."
    )

    assert result["bypass_detected"] is False
    assert result["bypass_type"] is None
