"""Keep Python-owned executable configuration out of shipped Skill Markdown."""

import re

from soulmap.runtime.knowledge.keyword_lists import default_skill_path
from soulmap.runtime.knowledge.runtime_config import (
    CELEBRATION_SCORING,
    DEPENDENCY_SCORING,
    DETECTOR_CONFIG,
    FRAMEWORK_TEMPLATE_ROWS,
    ORCHESTRATION_CONFIG,
    STAGE_CLASSIFIER_CONFIG,
)


def test_runtime_configuration_is_centralized_in_python() -> None:
    assert len(STAGE_CLASSIFIER_CONFIG["thresholds"]) == 6
    assert STAGE_CLASSIFIER_CONFIG["recent_message_window"] == 5
    assert STAGE_CLASSIFIER_CONFIG["memory_session_count_threshold"] == 10
    assert STAGE_CLASSIFIER_CONFIG["first_session_default_stage"] == 1
    assert STAGE_CLASSIFIER_CONFIG["first_session_max_stage"] == 3
    assert STAGE_CLASSIFIER_CONFIG["close_score_delta"] == 2
    assert STAGE_CLASSIFIER_CONFIG["anti_regression_min_lower_stage_messages"] == 2
    assert len(ORCHESTRATION_CONFIG["primary_priority"]) == 21
    assert len(DEPENDENCY_SCORING) == 8
    assert len(CELEBRATION_SCORING) == 8
    assert len(FRAMEWORK_TEMPLATE_ROWS) == 31
    assert len(DETECTOR_CONFIG) == 24
    assert DETECTOR_CONFIG["grief"]["Sustained history threshold"] == 2
    assert DETECTOR_CONFIG["conversation_synthesis"]["minimum_user_messages"] == 6
    assert DETECTOR_CONFIG["conversation_synthesis"]["automatic_user_messages"] == 10
    assert all(
        values and all(isinstance(value, int) for value in values.values())
        for values in DETECTOR_CONFIG.values()
    )


def test_skill_markdown_contains_no_python_runtime_configuration_tables() -> None:
    forbidden = {
        "stage-classifier": (
            "Minimum Thresholds",
            "Enforcement settings",
            "Stage roles",
            "Stage recommendations",
            "most recent 5 user messages",
            "most recent five user messages",
            "within 2 points",
            "10 or more",
            "two or more messages showing lower-stage signals",
            "Never classify higher than Stage 3",
            "Default to Stage 1 regardless of signals",
        ),
        "orchestration": (
            "Operational limits",
            "Primary framework priority",
            "Secondary layer priority",
            "Intensity fallback",
        ),
        "dependency-detection": (
            "Regex patterns",
            "Context exclusion policy",
            "Clause boundaries",
            "Dependency keyword weight",
        ),
        "integration-celebration": (
            "Win or completion weight",
            "Detection threshold",
            "Confirmation score",
        ),
        "framework-template-map": ("Core mapping table",),
    }
    for skill, phrases in forbidden.items():
        path = {
            "stage-classifier": "skills/meta/stage-classifier.md",
            "orchestration": "skills/meta/orchestration.md",
            "dependency-detection": "skills/safety/dependency-detection.md",
            "integration-celebration": "skills/frameworks/integration-celebration.md",
            "framework-template-map": "skills/meta/framework-template-map.md",
        }[skill]
        content = default_skill_path(path).read_text(encoding="utf-8")
        for phrase in phrases:
            assert phrase not in content, (
                f"{skill} still contains runtime configuration: {phrase}"
            )


def test_stage_markdown_does_not_restate_numeric_runtime_policy() -> None:
    content = default_skill_path("skills/meta/stage-classifier.md").read_text(
        encoding="utf-8"
    )
    forbidden_patterns = [
        r"most recent\s+\d+\s+user messages",
        r"within\s+\d+\s+points",
        r"session count.{0,40}\d+",
        r"two or more messages.{0,80}downgrad",
        r"first session.{0,100}(?:default|maximum|higher than)\s+stage\s+\d+",
        r"first \d+-\d+ exchanges",
    ]
    for pattern in forbidden_patterns:
        assert re.search(pattern, content, re.IGNORECASE) is None, (
            f"stage-classifier.md still duplicates runtime policy: {pattern}"
        )


def test_prompt_markdown_does_not_restate_python_owned_runtime_thresholds() -> None:
    forbidden_patterns = {
        "skills/meta/master-prompt.md": [
            r"default to stage\s+1 if unclear",
            r"never exceed stage\s+3 in the first session",
            r"\b(?:40|60|70|80|100|140|200|220) words\b",
            r"first\s+3 exchanges",
            r"2\+ stories",
        ],
        "skills/meta/orchestration.md": [
            r"default to stage\s+1",
            r"dependency score\s*>=\s*2",
            r"repeat signals across\s+2\+ stories",
            r"stage\s+5 or above",
            r"stage is\s+5 or higher",
            r"first or second",
        ],
    }
    for path, patterns in forbidden_patterns.items():
        content = default_skill_path(path).read_text(encoding="utf-8")
        for pattern in patterns:
            assert re.search(pattern, content, re.IGNORECASE) is None, (
                f"{path} still duplicates Python-owned runtime policy: {pattern}"
            )


def test_template_markdown_does_not_restate_python_owned_length_or_exchange_limits() -> (
    None
):
    checks = {
        "skills/meta/framework-template-map.md": [
            r"\b\d+\s*-\s*\d+\s*words\b",
            r"first\s+2-3\s+exchanges",
            r"no question for first\s+2-3\s+exchanges",
        ],
        "skills/frameworks/integration-celebration.md": [
            r"\b\d+\s*-\s*\d+\s*words\b",
        ],
    }
    for path, patterns in checks.items():
        content = default_skill_path(path).read_text(encoding="utf-8")
        for pattern in patterns:
            assert re.search(pattern, content, re.IGNORECASE) is None, (
                f"{path} still duplicates Python-owned template constraints: {pattern}"
            )


def test_framework_source_markdown_does_not_restate_template_ranges() -> None:
    framework_sources = (
        "skills/frameworks/ancestral-patterns.md",
        "skills/frameworks/fear-of-visibility.md",
        "skills/frameworks/creative-drought.md",
        "skills/frameworks/empath-boundary.md",
        "skills/frameworks/perfectionism-paralysis.md",
        "skills/frameworks/grief-companion.md",
    )
    for path in framework_sources:
        content = default_skill_path(path).read_text(encoding="utf-8")
        assert (
            re.search(r"\b\d+\s*-\s*\d+\s*words\b", content, re.IGNORECASE) is None
        ), f"{path} still duplicates Python-owned word ranges"
        assert re.search(r"first\s+2-3\s+exchanges", content, re.IGNORECASE) is None, (
            f"{path} still duplicates the configured acute-grief exchange window"
        )


def test_detector_numeric_policy_tables_are_python_owned() -> None:
    detector_sources = (
        "skills/frameworks/anger-companion.md",
        "skills/frameworks/ancestral-patterns.md",
        "skills/frameworks/creative-drought.md",
        "skills/frameworks/dark-night-of-soul.md",
        "skills/frameworks/divine-guidance.md",
        "skills/frameworks/emotional-deescalation.md",
        "skills/frameworks/empath-boundary.md",
        "skills/frameworks/existential-companion.md",
        "skills/frameworks/fear-of-visibility.md",
        "skills/frameworks/grief-companion.md",
        "skills/frameworks/inner-parts.md",
        "skills/frameworks/meaning-integration.md",
        "skills/frameworks/perfectionism-paralysis.md",
        "skills/soulmate/partnership-patterns.md",
        "skills/frameworks/pattern-mapper.md",
        "skills/frameworks/sacred-feminine-masculine.md",
        "skills/frameworks/shadow-patterns.md",
        "skills/frameworks/somatic-wellbeing.md",
        "skills/soulmate/soulmate-longing.md",
        "skills/frameworks/soul-nourishment.md",
        "skills/spiritual/spiritual-discernment.md",
        "skills/frameworks/spiritual-purpose.md",
        "skills/frameworks/life-direction.md",
        "skills/frameworks/conversation-synthesis.md",
    )
    numeric_policy_row = re.compile(
        r"^\|\s*[^|]+\s*\|\s*\d+\s*\|\s*$", re.MULTILINE
    )
    for path in detector_sources:
        content = default_skill_path(path).read_text(encoding="utf-8")
        assert numeric_policy_row.search(content) is None, (
            f"{path} still contains a Python-consumed numeric policy table"
        )


def test_synthesis_markdown_does_not_duplicate_numeric_runtime_limits() -> None:
    content = default_skill_path(
        "skills/frameworks/conversation-synthesis.md"
    ).read_text(encoding="utf-8")
    forbidden_patterns = (
        r"\b6 user messages\b",
        r"\b10 user messages\b",
        r"\b3\+ sessions\b",
        r"two or more distinct themes",
        r"name 2-3 themes",
        r"do not list more than 3",
    )
    for pattern in forbidden_patterns:
        assert re.search(pattern, content, re.IGNORECASE) is None, (
            f"conversation-synthesis.md still duplicates runtime limits: {pattern}"
        )
