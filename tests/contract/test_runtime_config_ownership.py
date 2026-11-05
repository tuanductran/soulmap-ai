"""Keep Python-owned executable configuration out of shipped Skill Markdown."""

import re
from pathlib import Path

from soulmap.runtime.knowledge.framework_template_source import load_template_rules
from soulmap.runtime.knowledge.keyword_lists import default_skill_path
from soulmap.runtime.knowledge.runtime_config import (
    CELEBRATION_SCORING,
    DEPENDENCY_SCORING,
    DETECTOR_CONFIG,
    DETECTOR_PRIORITY_CONFIG,
    FRAMEWORK_TEMPLATE_ROWS,
    ORCHESTRATION_CONFIG,
    STAGE_CLASSIFIER_CONFIG,
)


def test_runtime_configuration_is_centralized_in_python() -> None:
    """Verify executable runtime policy remains centralized in Python."""
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
    dependency_template = next(
        row for row in FRAMEWORK_TEMPLATE_ROWS if row[0] == "Dependency"
    )
    assert dependency_template[2] == "60-80"
    assert len(DETECTOR_CONFIG) == 24
    assert set(DETECTOR_PRIORITY_CONFIG) == {"existential", "insight"}
    assert DETECTOR_CONFIG["grief"]["Sustained history threshold"] == 2
    assert DETECTOR_CONFIG["conversation_synthesis"]["minimum_user_messages"] == 6
    assert DETECTOR_CONFIG["conversation_synthesis"]["automatic_user_messages"] == 10
    assert all(
        values and all(type(value) is int for value in values.values())
        for values in DETECTOR_CONFIG.values()
    )


def test_skill_markdown_contains_no_python_runtime_configuration_tables() -> None:
    """Ensure Skill Markdown does not duplicate runtime configuration tables."""
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
    """Ensure stage knowledge does not repeat numeric runtime policy."""
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
    """Ensure prompt guidance omits Python-owned thresholds."""
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
    """Ensure template knowledge omits Python-owned length and exchange limits."""
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
    """Ensure framework sources do not duplicate configured template ranges."""
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
    """Ensure detector policy tables remain in Python configuration."""
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
    numeric_policy_row = re.compile(r"^\|\s*[^|]+\s*\|\s*\d+\s*\|\s*$", re.MULTILINE)
    for path in detector_sources:
        content = default_skill_path(path).read_text(encoding="utf-8")
        assert numeric_policy_row.search(content) is None, (
            f"{path} still contains a Python-consumed numeric policy table"
        )


def test_synthesis_markdown_does_not_duplicate_numeric_runtime_limits() -> None:
    """Ensure synthesis knowledge does not duplicate runtime limits."""
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


def test_skill_markdown_uses_display_labels_not_runtime_state_tokens() -> None:
    """Ensure Skills use display labels instead of runtime state tokens."""
    skills_root = Path(__file__).resolve().parents[2] / "skills"
    runtime_state_tokens = (
        "MIRROR",
        "HIGH",
        "MODERATE",
        "NORMAL",
        "PEER",
        "BLOCK",
        "CLEAR",
    )
    for path in sorted(skills_root.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        for token in runtime_state_tokens:
            assert not re.search(rf"\b{token}\b", content), (
                f"{path.relative_to(skills_root)} contains Python-facing "
                f"state token {token!r}"
            )


def test_dependency_response_ceiling_matches_runtime_configuration() -> None:
    """Verify dependency response guidance matches the configured ceiling."""
    dependency = next(row for row in FRAMEWORK_TEMPLATE_ROWS if row[0] == "Dependency")
    content = default_skill_path("skills/voice/response-calibrator.md").read_text(
        encoding="utf-8"
    )
    expected = rf"^\|\s*Dependency\s*\|\s*{re.escape(dependency[2])}\s+words\b"
    assert re.search(expected, content, re.MULTILINE), (
        "response-calibrator.md must preserve the Python-owned Dependency "
        f"word range {dependency[2]!r}"
    )


def test_framework_template_registry_is_complete_and_collision_free() -> None:
    """Verify framework template mappings are complete and unique."""
    rules = load_template_rules()
    framework_names = [rule.framework.strip().casefold() for rule in rules]

    assert len(rules) == 31
    assert len(set(framework_names)) == len(framework_names)
    assert all(
        rule.mode.strip()
        and rule.word_range.strip()
        and rule.question_rule.strip()
        and rule.source_file.strip()
        for rule in rules
    )


def test_portable_skills_do_not_depend_on_unshipped_runtime_configuration() -> None:
    """Ensure portable Skills do not reference unshipped runtime configuration."""
    skills_root = Path(__file__).resolve().parents[2] / "skills"
    forbidden = (
        "configured response-length rules",
        "configured response-length range",
        "configured initial grief window",
        "configured dependency response-length ceiling",
        "runtime_config.py",
        "src/soulmap/runtime/",
    )
    for path in skills_root.rglob("*.md"):
        content = path.read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            assert phrase not in content, (
                f"{path.relative_to(skills_root)} depends on unshipped "
                f"runtime configuration: {phrase}"
            )


def test_dependency_context_cues_are_markdown_owned() -> None:
    from soulmap.runtime.knowledge import runtime_config
    from soulmap.runtime.knowledge.keyword_lists import load_labeled_groups
    from soulmap.runtime.knowledge.runtime_config import DEPENDENCY_CONTEXT_POLICY
    from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

    assert not hasattr(runtime_config, "DEPENDENCY_CONTEXT_CUES")
    groups = load_labeled_groups(
        runtime_skill_path("dependency-detection"), "Context exclusion cues"
    )
    assert set(groups) == set(DEPENDENCY_CONTEXT_POLICY)
    assert all(groups.values())


def test_skill_guidance_does_not_expose_python_owned_scoring_or_thresholds() -> None:
    """Ensure Skill guidance does not expose scoring internals."""
    forbidden = {
        "skills/meta/stage-classifier.md": (
            "weighted score",
            "Scoring Algorithm",
            "Base Scoring",
            "configured scoring and recency policy",
            "recency weighting",
        ),
        "skills/meta/orchestration.md": (
            "configured fallback stage",
            "High dependency score detected",
            "configured peer-stage threshold",
            "configured first-contact window",
        ),
        "skills/safety/dependency-detection.md": ("Scoring approach",),
    }
    for path, phrases in forbidden.items():
        content = default_skill_path(path).read_text(encoding="utf-8")
        for phrase in phrases:
            assert phrase not in content, (
                f"{path} still exposes Python-owned runtime policy: {phrase}"
            )

    orchestration = default_skill_path("skills/meta/orchestration.md").read_text(
        encoding="utf-8"
    )
    assert (
        "Clear dependency evidence appears in the user's own language or context"
        in orchestration
    )


def test_acute_grief_question_timing_is_python_owned_and_readiness_gated() -> None:
    """Verify acute-grief timing remains readiness-gated by runtime policy."""
    rule = next(row for row in FRAMEWORK_TEMPLATE_ROWS if row[0] == "Grief (acute)")
    assert "first 2-3 exchanges" in rule[3]
    assert "readiness" in rule[3].lower()

    documentation = (
        "skills/frameworks/grief-companion.md",
        "skills/voice/response-calibrator.md",
        "skills/meta/deep-inquiry-bank.md",
        "skills/meta/master-prompt.md",
        "skills/meta/framework-template-map.md",
    )
    for path in documentation:
        content = default_skill_path(path).read_text(encoding="utf-8").lower()
        assert "first 2-3 exchanges" not in content, (
            f"{path} duplicates the Python-owned acute-grief timing window"
        )
        assert "initial acute-grief period" in content, (
            f"{path} does not describe the acute-grief timing policy"
        )
        assert "readiness" in content, (
            f"{path} omits the readiness condition for grief questions"
        )


def test_agent_markdown_does_not_expose_python_implementation_details() -> None:
    """Keep shipped knowledge free of Python-owned runtime implementation notes."""
    repository_root = Path(__file__).resolve().parents[2]
    markdown_paths = [
        *sorted((repository_root / "skills").rglob("*.md")),
        repository_root / "SOULMAP.md",
        repository_root / "SKILL.md",
    ]
    forbidden_phrases = (
        "runtime detection contract",
        "executable detection policy",
        "runtime scoring",
        "scoring weights and thresholds are centrally configured",
        "detection weights, thresholds, and history limits are centrally configured",
        "configured history window",
        "configured word limit",
        "configured maximum",
        "configured minimum user-message threshold",
        "no dedicated phrase-matching detector",
        "the ai model applies this framework through language understanding",
        "signals from other detectors",
        "runtime framing-marker scanner",
        "runtime blocking and refusal wording coverage",
        "scoring or routing configuration",
        "secondary scoring",
        "adds extra weight",
        "operational configuration is normative knowledge",
        "covered by focused contract tests",
        "operational insight-detection policy",
        "operational shadow-pattern detection policy",
        "operational spiritual-bypass detection policy",
        "executable source of truth for synthesis",
        "runtime may execute these values",
    )
    for path in markdown_paths:
        content = path.read_text(encoding="utf-8").casefold()
        for phrase in forbidden_phrases:
            assert phrase not in content, (
                f"{path.relative_to(repository_root)} exposes Python implementation "
                f"details through {phrase!r}"
            )
