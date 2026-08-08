"""Edge-case coverage for the somatic detector.

Phrases used below are taken verbatim from
skills/frameworks/somatic-wellbeing.md, "## Detection signals", which is
the single source of truth this detector loads from. Nothing here is
guessed.
"""

from soulmap.runtime.detectors.somatic_detector import detect_somatic


def test_body_sensation_is_detected_and_typed_correctly() -> None:
    result = detect_somatic("My heart is racing and my chest is tight.")

    assert result["somatic_detected"] is True
    assert result["mode"] == "BODY_SENSATION"


def test_biometric_context_is_detected_and_typed_correctly() -> None:
    result = detect_somatic("My HRV and sleep data have been low this week.")

    assert result["somatic_detected"] is True
    assert result["mode"] == "BIOMETRIC"


def test_somatic_invitation_is_detected_and_typed_correctly() -> None:
    result = detect_somatic("I keep overthinking, I'm totally in my head today.")

    assert result["somatic_detected"] is True
    assert result["mode"] == "SOMATIC_INVITATION"


def test_biometric_takes_priority_over_body_sensation() -> None:
    """Biometric is checked first and should win when phrasing overlaps
    with body-sensation language in the same message."""
    result = detect_somatic("My HRV is low and my chest is tight too.")

    assert result["somatic_detected"] is True
    assert result["mode"] == "BIOMETRIC"


def test_neutral_message_is_not_misclassified() -> None:
    result = detect_somatic("I had a sandwich for lunch and read a book.")

    assert result["somatic_detected"] is False
    assert result["mode"] is None


def test_empty_message_does_not_crash_and_is_not_detected() -> None:
    result = detect_somatic("")

    assert result["somatic_detected"] is False
    assert result["mode"] is None


def test_guidance_present_for_each_detected_mode() -> None:
    body = detect_somatic("Heart racing, chest tightness right now.")
    biometric = detect_somatic("My resting heart rate has been off lately.")
    invitation = detect_somatic("I feel spaced out and zoned out today.")

    assert body["guidance"]
    assert biometric["guidance"]
    assert invitation["guidance"]
