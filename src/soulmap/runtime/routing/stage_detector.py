"""Estimate the SoulMap user journey stage from conversation history."""

from __future__ import annotations

import json
import sys
from typing import cast

from soulmap.runtime.io.cli_payload import print_json_error, read_stdin_json_value
from soulmap.runtime.knowledge.stage_classifier import (
    StageClassifierRules,
    load_stage_classifier,
)

ConversationMessage = dict[str, str]


def _memory_minimum_stage(
    memory: dict[str, object], rules: StageClassifierRules
) -> int:
    """Apply memory-based minimum-stage adjustments from Markdown."""
    minimum = 1
    session_count = memory.get("session_count")
    if (
        isinstance(session_count, int)
        and session_count >= 10
        and "session_count_ge_10" in rules.memory_minimums
    ):
        minimum = max(minimum, rules.memory_minimums["session_count_ge_10"])
    if memory.get("prior_session_showed_pattern_recognition") is True:
        minimum = max(minimum, rules.memory_minimums["prior_pattern_recognition"])
    if memory.get("prior_session_showed_breakthrough") is True:
        minimum = max(minimum, rules.memory_minimums["prior_breakthrough"])
    return minimum


def _lower_stage_message_count(
    user_messages: list[str], rules: StageClassifierRules, prior_stage: int
) -> int:
    """Count recent messages carrying signals from stages below prior_stage."""
    lower_stages = tuple(stage for stage in rules.stages if stage.number < prior_stage)
    count = 0
    for message in user_messages[-5:]:
        if any(
            any(keyword in message for keyword in stage.keywords)
            for stage in lower_stages
        ):
            count += 1
    return count


def _score_stages(
    user_messages: list[str], rules: StageClassifierRules
) -> tuple[dict[int, float], dict[int, list[str]]]:
    """Score the most recent five user messages using Markdown rules."""
    recent = user_messages[-5:]
    scores = {stage.number: 0.0 for stage in rules.stages}
    signals = {stage.number: [] for stage in rules.stages}
    multipliers = rules.recency_multipliers[-len(recent) :]
    for message, multiplier in zip(recent, multipliers, strict=True):
        for stage in rules.stages:
            for keyword in stage.keywords:
                if keyword in message:
                    scores[stage.number] += stage.weight * multiplier
                    if keyword not in signals[stage.number]:
                        signals[stage.number].append(keyword)
    return scores, signals


def _select_stage(
    scores: dict[int, float], rules: StageClassifierRules, minimum_stage: int
) -> tuple[int, float]:
    """Select the highest eligible stage and resolve close scores conservatively."""
    eligible = [
        stage
        for stage in scores
        if stage >= minimum_stage and scores[stage] >= rules.thresholds[stage]
    ]
    if not eligible:
        return minimum_stage, scores[minimum_stage]
    ranked = sorted(eligible, key=lambda stage: (-scores[stage], stage))
    best = ranked[0]
    if (
        len(ranked) > 1
        and abs(scores[best] - scores[ranked[1]]) <= rules.close_score_delta
    ):
        best = min(best, ranked[1])
    return best, scores[best]


def _confidence(stage: int, score: float, rules: StageClassifierRules) -> str:
    if stage == 1 and score == 0:
        return "LOW"
    return "HIGH" if score >= rules.thresholds[stage] * 1.5 else "MODERATE"


def detect_stage(
    conversation_messages: list[ConversationMessage],
    memory: dict[str, object] | None = None,
) -> dict[str, object]:
    """Classify the recent conversation against stage-classifier.md."""
    memory = memory or {}
    user_messages = [
        str(message.get("content", "")).lower()
        for message in conversation_messages
        if isinstance(message, dict) and message.get("role") == "user"
    ]
    rules = load_stage_classifier()
    if not user_messages:
        selected_stage = 1
        score = 0.0
        confidence = "DEFAULT"
        signals: dict[int, list[str]] | list[str] = []
    else:
        scores, signals_by_stage = _score_stages(user_messages, rules)
        signals = signals_by_stage
        if len(user_messages) == 1 and not memory:
            selected_stage = 1
            score = scores[1]
            confidence = "LOW"
        else:
            selected_stage, score = _select_stage(
                scores, rules, _memory_minimum_stage(memory, rules)
            )
            if not memory:
                selected_stage = min(selected_stage, rules.first_session_max_stage)
                score = scores[selected_stage]
            prior_stage = memory.get("prior_stage")
            if (
                isinstance(prior_stage, int)
                and 1 <= prior_stage <= 6
                and selected_stage < prior_stage
            ):
                destabilized = bool(memory.get("destabilization_signals"))
                lower_signal_messages = _lower_stage_message_count(
                    user_messages, rules, prior_stage
                )
                if (
                    not destabilized
                    or lower_signal_messages
                    < rules.anti_regression_min_lower_stage_messages
                ):
                    selected_stage = prior_stage
                    score = scores.get(prior_stage, 0.0)
            confidence = _confidence(selected_stage, score, rules)
    stage_rule = next(stage for stage in rules.stages if stage.number == selected_stage)
    return {
        "stage": selected_stage,
        "name": stage_rule.name,
        "confidence": confidence,
        "soulmap_role": rules.stage_roles[selected_stage],
        "signals": signals if isinstance(signals, list) else signals[selected_stage],
        "score": score,
        "recommendation": rules.stage_recommendations[selected_stage],
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json_value(strip=True)
        if isinstance(data, list):
            messages = cast(list[ConversationMessage], data)
            memory = {}
        else:
            messages = cast(list[ConversationMessage], data.get("messages", []))
            value = data.get("memory", {})
            memory = value if isinstance(value, dict) else {}
        print(json.dumps(detect_stage(messages, memory), ensure_ascii=False, indent=2))
    except ValueError as error:
        print_json_error(error)
        sys.exit(1)
    except Exception as error:
        print_json_error(error)
        sys.exit(1)
