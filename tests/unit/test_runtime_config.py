"""Validate the structure of Python-owned runtime configuration."""

from soulmap.runtime.knowledge.runtime_config import (
    CELEBRATION_SCORING,
    DEPENDENCY_CLAUSE_BOUNDARIES,
    DEPENDENCY_CONTEXT_POLICY,
    DEPENDENCY_SCORING,
    DETECTOR_CONFIG,
    DETECTOR_PRIORITY_CONFIG,
    FRAMEWORK_TEMPLATE_ROWS,
    ORCHESTRATION_CONFIG,
    STAGE_CLASSIFIER_CONFIG,
)


def test_stage_classifier_configuration_has_a_stable_shape() -> None:
    """Keep stage-classifier runtime settings explicit and well-formed."""
    assert set(STAGE_CLASSIFIER_CONFIG) == {
        "recent_message_window",
        "memory_session_count_threshold",
        "keyword_weights",
        "thresholds",
        "recency_multipliers",
        "memory_minimums",
        "close_score_delta",
        "first_session_default_stage",
        "first_session_max_stage",
        "anti_regression_min_lower_stage_messages",
    }
    assert all(
        isinstance(row, list)
        and len(row) == 2
        and all(type(value) is int for value in row)
        for row in STAGE_CLASSIFIER_CONFIG["thresholds"]
    )
    assert all(
        type(value) in {int, float}
        for value in STAGE_CLASSIFIER_CONFIG["recency_multipliers"]
    )
    assert all(
        type(value) is int
        for value in STAGE_CLASSIFIER_CONFIG["memory_minimums"].values()
    )


def test_orchestration_configuration_has_expected_sections() -> None:
    """Keep orchestration runtime policy grouped by its execution concern."""
    assert set(ORCHESTRATION_CONFIG) == {
        "scalars",
        "intensity_fallback",
        "primary_priority",
        "secondary_priority",
    }
    assert len(ORCHESTRATION_CONFIG["primary_priority"]) == 21
    assert all(
        isinstance(row, list) and len(row) == 6
        for row in ORCHESTRATION_CONFIG["primary_priority"]
    )
    assert all(
        isinstance(row, list) and len(row) == 4
        for row in ORCHESTRATION_CONFIG["intensity_fallback"]
    )
    assert all(
        isinstance(row, list) and len(row) == 2
        for row in ORCHESTRATION_CONFIG["secondary_priority"]
    )


def test_detector_scoring_configuration_contains_only_integer_weights() -> None:
    """Keep detector weights and thresholds machine-readable and typed."""
    assert DEPENDENCY_SCORING
    assert CELEBRATION_SCORING
    assert all(type(value) is int for value in DEPENDENCY_SCORING.values())
    assert all(type(value) is int for value in CELEBRATION_SCORING.values())
    assert len(DETECTOR_CONFIG) == 24
    assert all(
        config and all(type(value) is int for value in config.values())
        for config in DETECTOR_CONFIG.values()
    )
    assert set(DETECTOR_PRIORITY_CONFIG) == {"existential", "insight"}
    assert all(
        isinstance(value, str) and value
        for config in DETECTOR_PRIORITY_CONFIG.values()
        for value in config.values()
    )


def test_dependency_context_policy_is_explicit() -> None:
    """Keep dependency-context inclusion policy and clause boundaries explicit."""
    assert DEPENDENCY_CONTEXT_POLICY == {
        "third-party attribution": False,
        "hypothetical framing": False,
        "negation of an assertion": True,
    }
    assert DEPENDENCY_CLAUSE_BOUNDARIES
    assert all(
        isinstance(boundary, str) and boundary
        for boundary in DEPENDENCY_CLAUSE_BOUNDARIES
    )


def test_framework_template_rows_are_complete_and_unique() -> None:
    """Keep framework template mappings complete and collision-free."""
    assert len(FRAMEWORK_TEMPLATE_ROWS) == 31
    assert all(
        isinstance(row, list)
        and len(row) == 5
        and all(isinstance(value, str) and value.strip() for value in row)
        for row in FRAMEWORK_TEMPLATE_ROWS
    )
    names = [row[0].casefold() for row in FRAMEWORK_TEMPLATE_ROWS]
    assert len(names) == len(set(names))
