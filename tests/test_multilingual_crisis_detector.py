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


@pytest.mark.parametrize(
    "message",
    [
        "Lately I've been cutting myself and I don't know why I keep doing it.",
        "Dạo này tôi hay tự cắt tay, tôi không biết vì sao nữa.",
        "Ultimamente pienso en cortarme y no se por que sigo asi.",
        "Ces derniers temps je n'arrete pas de me couper et je ne sais pas pourquoi.",
        "最近我一直在割伤自己我也不知道为什么。",
    ],
    ids=["en", "vi", "es", "fr", "zh"],
)
def test_tier1_self_harm_morphological_variants_across_languages(message: str) -> None:
    """Regression coverage for colloquial self-harm phrasing (Issue #130 follow-up).

    These are morphological/colloquial paraphrases of existing tier 1 signals
    (e.g. 'cutting myself' vs. 'cut myself', 'cortarme' vs. a bare noun form),
    not new signal phrases, so no language pack changes are required.
    """
    result = detect_crisis(message)

    assert result["level"] == "CRISIS_TIER1"
    assert result["tier"] == 1
    assert result["action"] == "IMMEDIATE_SAFETY_RESPONSE"
    assert result["signals"]


@pytest.mark.parametrize(
    "message",
    [
        "toi khong muon song nua",
        "muon chet qua",
        "dao nay hay nghi den chuyen tu tu",
        "toi muon tu sat",
        "khong muon ton tai nua",
    ],
)
def test_tier1_crisis_detected_for_diacritic_stripped_vietnamese(
    message: str,
) -> None:
    """Vietnamese typed without diacritics must still trip Tier 1 (issue: safety-enforcement-matrix

    'Morphological crisis phrase variants' gap, previously English-only).
    """
    result = detect_crisis(message)

    assert result["level"] == "CRISIS_TIER1"
    assert result["tier"] == 1
    assert result["action"] == "IMMEDIATE_SAFETY_RESPONSE"
    assert result["signals"]


def test_diacritic_stripped_vietnamese_does_not_break_accented_matching() -> None:
    """Regression guard: the diacritic-stripping helper must not change

    detection for correctly accented Vietnamese input.
    """
    result = detect_crisis("Tôi không muốn sống nữa.")

    assert result["level"] == "CRISIS_TIER1"
    assert "không muốn sống nữa" in result["signals"]


@pytest.mark.parametrize(
    "message",
    [
        "Toi rat vui vi hom nay troi dep.",
        "Cong viec cua toi khong lien quan den chuyen nay.",
    ],
)
def test_no_crisis_for_unrelated_diacritic_stripped_vietnamese(message: str) -> None:
    """Diacritic stripping must not cause false positives on neutral text."""
    result = detect_crisis(message)

    assert result["level"] == "NO_CRISIS"
    assert result["signals"] == []


@pytest.mark.parametrize(
    "message",
    [
        "Creo que soy el elegido, tengo una mision cosmica que nadie entiende.",
        "Je pense que je suis l'elu, j'ai une mission cosmique que personne ne comprend.",
    ],
    ids=["es", "fr"],
)
def test_grandiosity_detected_in_additional_languages(message: str) -> None:
    """Fills the es/fr grandiosity coverage gap left by the en/vi-only case above."""
    result = detect_crisis(message)

    assert result["level"] == "GRANDIOSITY_SIGNAL"
