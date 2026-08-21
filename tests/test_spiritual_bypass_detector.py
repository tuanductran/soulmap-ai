"""Edge-case coverage for the spiritual bypass detector.

English phrases used below are taken verbatim from
skills/spiritual/spiritual-discernment.md, "## Detection signal reference".
Locale phrase coverage is maintained in
reference/languages/<locale>/spiritual-bypass.md and is tested separately. Nothing
here is guessed.
"""

from soulmap.runtime.detectors.spiritual_bypass_detector import detect_bypass


def test_dismissing_pain_bypass_is_detected_and_typed_correctly() -> None:
    result = detect_bypass(
        "Everything happens for a reason, so I shouldn't be attached."
    )

    assert result["bypass_detected"] is True
    assert result["bypass_type"] == "dismissing_pain"


def test_premature_acceptance_bypass_is_detected_and_typed_correctly() -> None:
    result = detect_bypass("I've already forgiven them, I'm at peace with it.")

    assert result["bypass_detected"] is True
    assert result["bypass_type"] == "premature_acceptance"


def test_spiritual_inflation_bypass_is_detected_and_typed_correctly() -> None:
    result = detect_bypass(
        "As an empath I feel everything, most people can't understand."
    )

    assert result["bypass_detected"] is True
    assert result["bypass_type"] == "spiritual_inflation"


def test_bypassing_accountability_is_detected_and_typed_correctly() -> None:
    result = detect_bypass("I manifested this situation, they were my teacher.")

    assert result["bypass_detected"] is True
    assert result["bypass_type"] == "bypassing_accountability"


def test_dismissing_pain_takes_priority_when_multiple_types_present() -> None:
    """Dismissing-pain phrases are checked first and should win when
    phrasing overlaps with another bypass category in one message."""
    result = detect_bypass(
        "Everything happens for a reason, and as an empath I feel it deeply."
    )

    assert result["bypass_detected"] is True
    assert result["bypass_type"] == "dismissing_pain"


def test_genuine_integration_signals_reduce_score_below_threshold() -> None:
    """Two or more genuine-integration phrases should reduce the score by 2,
    which can drop a single weak bypass signal below the detection threshold."""
    result = detect_bypass(
        "It made me stronger, but I'm still processing it and still feeling "
        "it, even though i know it's complicated."
    )

    assert result["bypass_detected"] is False


def test_neutral_spiritual_language_without_bypass_phrases_is_not_flagged() -> None:
    result = detect_bypass("I've been reading about meditation lately.")

    assert result["bypass_detected"] is False
    assert result["bypass_type"] is None


def test_empty_message_does_not_crash_and_is_not_bypass() -> None:
    result = detect_bypass("")

    assert result["bypass_detected"] is False
    assert result["signals"] == []


def test_case_and_punctuation_do_not_prevent_detection() -> None:
    result = detect_bypass("EVERYTHING HAPPENS FOR A REASON!!! I need to surrender...")

    assert result["bypass_detected"] is True


def test_note_marks_result_as_secondary_layer_not_primary_framework() -> None:
    """Per the module docstring, spiritual bypass is always a secondary
    layer flag and must never be returned as a primary framework."""
    result = detect_bypass("I need to raise my vibration and let go.")

    assert result["bypass_detected"] is True
    assert "secondary layer" in str(result["note"]).lower()


def test_recommendation_present_for_each_detected_bypass_type() -> None:
    dismiss = detect_bypass(
        "I need to surrender, it's all happening for my highest good."
    )
    premature = detect_bypass("I've moved on, everything worked out for the best.")
    inflation = detect_bypass("As a lightworker, i operate at a different level.")
    accountability = detect_bypass(
        "They reflected my shadow to me, the universe sent them."
    )

    assert dismiss["recommendation"]
    assert premature["recommendation"]
    assert inflation["recommendation"]
    assert accountability["recommendation"]
