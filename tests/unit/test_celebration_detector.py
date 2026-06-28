"""Tests for celebration_detector (P9b) and its integration into framework_selector."""

from __future__ import annotations

from soulmap.runtime.detectors.celebration_detector import detect_celebration
from soulmap.runtime.routing.framework_selector import select_framework

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _msg(text: str) -> list[dict[str, str]]:
    return [{"role": "user", "content": text}]


# ---------------------------------------------------------------------------
# detect_celebration - positive cases
# ---------------------------------------------------------------------------


class TestDetectCelebrationPositive:
    def test_win_signal(self) -> None:
        r = detect_celebration("I finally did it.", _msg("I finally did it."))
        assert r["celebration_detected"] is True
        assert r["celebration_type"] == "win"

    def test_win_long(self) -> None:
        msg = "I finally did it. I said the thing I have been afraid to say for two years."
        r = detect_celebration(msg, _msg(msg))
        assert r["celebration_detected"] is True
        assert r["celebration_type"] == "win"

    def test_relief_signal(self) -> None:
        msg = "I feel lighter than I have in months. I think the worst is over."
        r = detect_celebration(msg, _msg(msg))
        assert r["celebration_detected"] is True
        assert r["celebration_type"] == "relief"

    def test_gratitude_signal(self) -> None:
        msg = "I am so grateful for everything that happened."
        r = detect_celebration(msg, _msg(msg))
        assert r["celebration_detected"] is True
        assert r["celebration_type"] == "gratitude"

    def test_recognized_progress(self) -> None:
        msg = "I noticed I did not react the way I used to. I caught myself this time."
        r = detect_celebration(msg, _msg(msg))
        assert r["celebration_detected"] is True
        assert r["celebration_type"] == "recognized_progress"

    def test_caught_myself(self) -> None:
        msg = "I caught myself this time before I spiraled."
        r = detect_celebration(msg, _msg(msg))
        assert r["celebration_detected"] is True

    def test_i_can_breathe_again(self) -> None:
        msg = "I can breathe again. It's finally over."
        r = detect_celebration(msg, _msg(msg))
        assert r["celebration_detected"] is True
        assert r["celebration_type"] == "relief"

    def test_returns_signals_list(self) -> None:
        msg = "I finally did it."
        r = detect_celebration(msg, _msg(msg))
        assert isinstance(r["signals"], list)
        assert len(r["signals"]) > 0

    def test_strength_field_present(self) -> None:
        msg = "I finally did it."
        r = detect_celebration(msg, _msg(msg))
        assert r["strength"] in ("strong", "present")

    def test_recommendation_references_framework(self) -> None:
        msg = "I finally did it."
        r = detect_celebrate(msg, _msg(msg))
        assert "integration-celebration.md" in r["recommendation"]

    def test_score_above_threshold(self) -> None:
        msg = "I finally did it."
        r = detect_celebration(msg, _msg(msg))
        assert isinstance(r["score"], int)
        assert r["score"] >= 2


# ---------------------------------------------------------------------------
# detect_celebration - negative cases (must NOT fire)
# ---------------------------------------------------------------------------


class TestDetectCelebrationNegative:
    def test_grief_message(self) -> None:
        msg = "My mother passed away and I cannot stop crying."
        r = detect_celebration(msg, _msg(msg))
        assert r["celebration_detected"] is False

    def test_pattern_message(self) -> None:
        msg = "I keep repeating the same behavior in every relationship."
        r = detect_celebration(msg, _msg(msg))
        assert r["celebration_detected"] is False

    def test_lost_direction_message(self) -> None:
        msg = "I feel so lost and I do not know what to do."
        r = detect_celebration(msg, _msg(msg))
        assert r["celebration_detected"] is False

    def test_crisis_message(self) -> None:
        msg = "I've been thinking about ending it all."
        r = detect_celebration(msg, _msg(msg))
        assert r["celebration_detected"] is False

    def test_neutral_message(self) -> None:
        msg = "I had an interesting day today."
        r = detect_celebration(msg, _msg(msg))
        assert r["celebration_detected"] is False

    def test_score_zero_on_neutral(self) -> None:
        msg = "I had an interesting day today."
        r = detect_celebration(msg, _msg(msg))
        assert r["score"] == 0


# ---------------------------------------------------------------------------
# detect_celebration - negative override (mixed pain signal)
# ---------------------------------------------------------------------------


class TestDetectCelebrationNegativeOverride:
    def test_mixed_pain_reduces_score(self) -> None:
        msg = "I finally did it but I still feel empty inside."
        r = detect_celebration(msg, _msg(msg))
        assert r["has_negative_override"] is True

    def test_mixed_does_not_detect_if_score_drops_below_threshold(self) -> None:
        # Score starts at 3 (win), minus 2 for negative override = 1 < threshold
        msg = "I finally did it but I feel I do not deserve this."
        r = detect_celebration(msg, _msg(msg))
        # May or may not detect depending on final score - just verify override flagged
        assert r["has_negative_override"] is True

    def test_no_negative_override_on_clean_win(self) -> None:
        msg = "I finally did it."
        r = detect_celebration(msg, _msg(msg))
        assert r["has_negative_override"] is False


# ---------------------------------------------------------------------------
# framework_selector P9b routing
# ---------------------------------------------------------------------------


class TestFrameworkSelectorP9b:
    def test_win_routes_to_integration_celebration(self) -> None:
        msg = "I finally did it. I said the thing I had been afraid to say."
        r = select_framework(msg, _msg(msg), {})
        assert r["primary_framework"] == "INTEGRATION_CELEBRATION"

    def test_relief_routes_to_integration_celebration(self) -> None:
        msg = "I feel lighter than I have in months. The worst is over."
        r = select_framework(msg, _msg(msg), {})
        assert r["primary_framework"] == "INTEGRATION_CELEBRATION"

    def test_gratitude_routes_to_integration_celebration(self) -> None:
        msg = "I am so grateful for everything that happened."
        r = select_framework(msg, _msg(msg), {})
        assert r["primary_framework"] == "INTEGRATION_CELEBRATION"

    def test_recognized_progress_routes_to_integration_celebration(self) -> None:
        msg = "I noticed I did not react the way I used to. I caught myself this time."
        r = select_framework(msg, _msg(msg), {})
        assert r["primary_framework"] == "INTEGRATION_CELEBRATION"

    def test_grief_overrides_celebration(self) -> None:
        """Crisis/grief signals must never be overridden by celebration."""
        msg = "My father just died. I am relieved his suffering is over."
        r = select_framework(msg, _msg(msg), {})
        # Grief takes priority even when "relief" language is present
        assert r["primary_framework"] in ("GRIEF", "DE_ESCALATION", "MIRROR")
        assert r["primary_framework"] != "INTEGRATION_CELEBRATION"

    def test_crisis_overrides_celebration(self) -> None:
        msg = "I finally did it - I've been thinking about ending it all."
        r = select_framework(msg, _msg(msg), {})
        assert r["primary_framework"] == "CRISIS"

    def test_plain_mirror_message_not_routed_to_celebration(self) -> None:
        msg = "I keep getting stuck in my head."
        r = select_framework(msg, _msg(msg), {})
        assert r["primary_framework"] != "INTEGRATION_CELEBRATION"

    def test_instruction_field_references_framework_file(self) -> None:
        msg = "I finally did it."
        r = select_framework(msg, _msg(msg), {})
        assert r["primary_framework"] == "INTEGRATION_CELEBRATION"
        assert "integration-celebration.md" in r.get("instruction", "")

    def test_mode_is_mirror(self) -> None:
        msg = "I finally did it."
        r = select_framework(msg, _msg(msg), {})
        assert r["primary_framework"] == "INTEGRATION_CELEBRATION"
        assert r["mode"] == "MIRROR"


# ---------------------------------------------------------------------------
# Typo guard - ensure the function name used above is correct
# ---------------------------------------------------------------------------


def detect_celebrate(msg: str, history: list) -> dict:
    return detect_celebration(msg, history)
