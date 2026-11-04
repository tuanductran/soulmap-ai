"""Keep Python-owned executable configuration out of shipped Skill Markdown."""

from soulmap.runtime.knowledge.keyword_lists import default_skill_path
from soulmap.runtime.knowledge.runtime_config import (
    CELEBRATION_SCORING,
    DEPENDENCY_SCORING,
    FRAMEWORK_TEMPLATE_ROWS,
    ORCHESTRATION_CONFIG,
    STAGE_CLASSIFIER_CONFIG,
)


def test_runtime_configuration_is_centralized_in_python() -> None:
    assert len(STAGE_CLASSIFIER_CONFIG["thresholds"]) == 6
    assert STAGE_CLASSIFIER_CONFIG["recent_message_window"] == 5
    assert STAGE_CLASSIFIER_CONFIG["memory_session_count_threshold"] == 10
    assert len(ORCHESTRATION_CONFIG["primary_priority"]) == 21
    assert len(DEPENDENCY_SCORING) == 8
    assert len(CELEBRATION_SCORING) == 8
    assert len(FRAMEWORK_TEMPLATE_ROWS) == 31


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
