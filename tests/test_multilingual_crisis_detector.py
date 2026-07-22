import pytest

from soulmap.runtime.detectors.crisis_detector import detect_crisis
from soulmap.runtime.knowledge.crisis_language_packs import SUPPORTED_LANGUAGES


def test_supported_languages_cover_issue_130_scope() -> None:
    assert set(SUPPORTED_LANGUAGES) == {"en", "vi", "es", "fr", "zh"}


@pytest.mark.parametrize(
    "message",
    [
        "I want to kill myself.",
        "Muốn tự tử, không muốn sống nữa.",
        "Quiero suicidarme, no quiero seguir viviendo.",
        "Je veux me suicider, je ne veux plus vivre.",
        "我想自杀不想活了。",
    ],
    ids=["en", "vi", "es", "fr", "zh"],
)
def test_tier1_crisis_detected_across_supported_languages(message: str) -> None:
    result = detect_crisis(message)

    assert result["level"] == "CRISIS_TIER1"
    assert result["tier"] == 1
    assert result["action"] == "IMMEDIATE_SAFETY_RESPONSE"
    assert result["signals"]


@pytest.mark.parametrize(
    "message",
    [
        "I feel empty inside and I'm trapped.",
        "Tôi cảm thấy trống rỗng, tôi bị mắc kẹt.",
        "Me siento vacio, estoy atrapado.",
        "Je me sens vide, je me sens piege.",
        "我感觉很空虚我被困住了。",
    ],
    ids=["en", "vi", "es", "fr", "zh"],
)
def test_tier2_crisis_detected_across_supported_languages(message: str) -> None:
    result = detect_crisis(message)

    assert result["level"] == "CRISIS_TIER2"
    assert result["tier"] == 2
    assert result["action"] == "PRESENCE_FIRST_MANDATORY"


@pytest.mark.parametrize(
    "message",
    [
        "I feel pretty happy and calm today.",
        "Hôm nay tôi cảm thấy khá vui và bình yên.",
        "Hoy me siento bastante feliz y tranquilo.",
        "Aujourd'hui je me sens plutot heureux et calme.",
        "我今天感觉很开心很平静。",
    ],
    ids=["en", "vi", "es", "fr", "zh"],
)
def test_no_crisis_for_neutral_positive_messages_across_languages(
    message: str,
) -> None:
    result = detect_crisis(message)

    assert result["level"] == "NO_CRISIS"
    assert result["tier"] == 0
    assert result["signals"] == []


def test_english_tier1_behavior_is_unchanged_by_multilingual_support() -> None:
    """Regression guard: adding language packs must not change English signals."""
    result = detect_crisis(
        "I do not want to keep living. I have been thinking about it a lot."
    )

    assert result["level"] == "CRISIS_TIER1"
    assert "do not want to keep living" in result["signals"]


def test_grandiosity_detected_across_supported_languages() -> None:
    en = detect_crisis("I am the chosen one with a divine mission no one understands.")
    vi = detect_crisis("Tôi là người được chọn, tôi có sứ mệnh vũ trụ.")

    assert en["level"] == "GRANDIOSITY_SIGNAL"
    assert vi["level"] == "GRANDIOSITY_SIGNAL"
