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

_STAGE_ROLES = {
    1: "Sanctuary and witness - presence over wisdom",
    2: "Mirror with gentle reflection",
    3: "Mirror for pattern archaeology",
    4: "Witness to their growing authority",
    5: "Peer in conversation",
    6: "Witness to their becoming",
}

_STAGE_RECOMMENDATIONS = {
    1: "Stage 1: Presence only. No frameworks, no wisdom yet. Short responses. Let them lead.",
    2: "Stage 2: Begin gentle reflection. Name patterns as observations. One question at end.",
    3: "Stage 3: Pattern archaeology. Frameworks acceptable as lenses. More conceptual depth ok.",
    4: "Stage 4: Celebrate self-direction explicitly. Point back to their own knowing. Less teaching.",
    5: "Stage 5: Peer exchange. Equal conversation. Stay exploratory without taking the guide role.",
    6: "Stage 6: Witness only. They are self-led. Minimal intervention. Celebrate their becoming.",
}

def _memory_minimum_stage(memory: dict[str, object]) -> int:
    """Apply the exact minimum-stage adjustments documented in the classifier."""
    minimum = 1
    session_count = memory.get("session_count")
    if isinstance(session_count, int) and session_count >= 10:
        minimum = 2
    if memory.get("prior_session_showed_pattern_recognition") is True:
        minimum = max(minimum, 3)
    if memory.get("prior_session_showed_breakthrough") is True:
        minimum = max(minimum, 3)
    return minimum

def _score_stages(
    user_messages: list[str], rules: StageClassifierRules
) -> tuple[dict[int, float], dict[int, list[str]]]:
    """Score the most recent five user messages using Markdown rules."""
    recent = user_messages[-5:]
    scores = {stage.number: 0.0 for stage in rules.stages}
    signals = {stage.number: [] for stage in rules.stages}
    for message, multiplier in zip(recent, rules.recency_multipliers, strict=True):
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
        stage for stage in scores
        if stage >= minimum_stage and scores[stage] >= rules.thresholds[stage]
    ]
    if not eligible:
        return 1, scores[1]
    ranked = sorted(eligible, key=lambda stage: (-scores[stage], stage))
    best = ranked[0]
    if len(ranked) > 1 and abs(scores[best] - scores[ranked[1]]) <= 2:
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
        signals: list[str] = []
    else:
        scores, signals_by_stage = _score_stages(user_messages, rules)
        signals = signals_by_stage
        if len(user_messages) == 1 and not memory:
            selected_stage = 1
            score = scores[1]
            confidence = "LOW"
        else:
            selected_stage, score = _select_stage(
                scores, rules, _memory_minimum_stage(memory)
            )
            prior_stage = memory.get("prior_stage")
            if (
                isinstance(prior_stage, int)
                and 1 <= prior_stage <= 6
                and selected_stage < prior_stage
                and not bool(memory.get("destabilization_signals"))
            ):
                selected_stage = prior_stage
                score = scores.get(prior_stage, 0.0)
            confidence = _confidence(selected_stage, score, rules)
    stage_rule = next(stage for stage in rules.stages if stage.number == selected_stage)
    return {
        "stage": selected_stage,
        "name": stage_rule.name,
        "confidence": confidence,
        "soulmap_role": _STAGE_ROLES[selected_stage],
        "signals": signals if isinstance(signals, list) else signals[selected_stage],
        "score": score,
        "recommendation": _STAGE_RECOMMENDATIONS[selected_stage],
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