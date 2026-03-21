"""Brand consistency checks for key public-facing surfaces."""

from pathlib import Path


def test_core_positioning_phrase_is_consistent() -> None:
    expected_phrase = "reflective companion"
    files = [
        Path("README.md"),
        Path("skills/brand/SKILL.md"),
        Path("skills/brand/message-hierarchy.md"),
        Path("skills/brand/brand-positioning.md"),
        Path("templates/brand-copy.md"),
        Path("templates/marketplace-copy.md"),
        Path("templates/onboarding-copy.md"),
    ]

    for path in files:
        content = path.read_text(encoding="utf-8").lower()
        assert expected_phrase in content, f"{path} is missing '{expected_phrase}'."


def test_brand_promise_is_present_on_key_surfaces() -> None:
    expected_phrase = "stop abandoning themselves"
    files = [
        Path("README.md"),
        Path("skills/brand/message-hierarchy.md"),
        Path("skills/brand/brand-positioning.md"),
        Path("templates/launch-readiness-checklist.md"),
        Path("templates/faq.md"),
    ]

    for path in files:
        content = " ".join(path.read_text(encoding="utf-8").lower().split())
        assert expected_phrase in content, f"{path} is missing '{expected_phrase}'."


def test_canonical_guardrails_are_reflected_in_public_surfaces() -> None:
    phrases = [
        "not a therapist",
        "not a guru",
        "not a replacement for real-world support",
    ]
    files = [
        Path("skills/brand/message-hierarchy.md"),
        Path("skills/brand/brand-positioning.md"),
        Path("templates/brand-copy.md"),
        Path("templates/marketplace-copy.md"),
        Path("templates/onboarding-copy.md"),
    ]

    for phrase in phrases:
        normalized = " ".join(phrase.split())
        matched = False
        for path in files:
            content = " ".join(path.read_text(encoding="utf-8").lower().split())
            if normalized in content:
                matched = True
                break
        assert matched, f"Missing canonical guardrail phrase: {phrase}"


def test_launch_readiness_checklist_covers_core_areas() -> None:
    content = Path("templates/launch-readiness-checklist.md").read_text(
        encoding="utf-8"
    )

    for section in [
        "## Positioning",
        "## Brand Integrity",
        "## Safety & Boundaries",
        "## Product Surfaces",
        "## Validation",
    ]:
        assert section in content


def test_surfaces_and_scope_separates_behavior_layers() -> None:
    content = Path("skills/brand/surfaces-and-scope.md").read_text(encoding="utf-8")

    for section in [
        "## Live Conversation",
        "## Public Content",
        "## Internal Strategy",
        "## Canonical Order",
    ]:
        assert section in content


def test_dependency_inviting_closings_are_not_present_on_public_surfaces() -> None:
    forbidden_phrases = [
        "come back anytime",
        "i hope this helped",
        "it was great talking with you",
        "i'm here for you",
    ]
    files = [
        Path("README.md"),
        Path("templates/marketplace-copy.md"),
        Path("templates/onboarding-copy.md"),
        Path("templates/faq.md"),
        Path("templates/redirect-templates.md"),
        Path("skills/brand/message-hierarchy.md"),
    ]

    for path in files:
        content = path.read_text(encoding="utf-8").lower()
        for phrase in forbidden_phrases:
            assert phrase not in content, f"{path} contains forbidden phrase: {phrase}"


def test_founder_brand_file_is_calibration_not_doctrine() -> None:
    content = Path("skills/brand/founder-personal-brand.md").read_text(encoding="utf-8")

    for phrase in [
        "founder calibration layer",
        "not as a doctrine layer",
        "must not override",
        "preserve SoulMap doctrine first and founder fit second",
        "symbolic mirror, not as fate",
    ]:
        assert phrase in content


def test_brand_skill_explicitly_scopes_founder_context() -> None:
    content = Path("skills/brand/SKILL.md").read_text(encoding="utf-8")
    assert "Treat `founder-personal-brand.md` as a founder calibration layer" in content
