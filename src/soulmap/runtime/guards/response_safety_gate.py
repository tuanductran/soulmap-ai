"""Apply independent safety overrides after framework selection."""
from __future__ import annotations
import json
from soulmap.runtime.detectors.crisis_detector import detect_crisis
from soulmap.runtime.detectors.dependency_detector import analyze_dependency
from soulmap.runtime.io.cli_payload import print_json_error, read_stdin_json, require_message_history_memory_selection_fields
from soulmap.runtime.routing.scope_classifier import classify_message

_DEPENDENCY_LEVELS = {"NO_DATA", "LOW_DEPENDENCY", "MODERATE_DEPENDENCY", "HIGH_DEPENDENCY"}
_SCOPE_ACTIONS = {
    "BLACKLIST_PROHIBITED": "DECLINE_AND_REDIRECT",
    "BLACKLIST_LAYER1": "DECLINE_WITH_CLEAN_EXIT",
    "WHITELIST_TIER1": "RESPOND_FULLY",
    "WHITELIST_TIER2": "ASK_INNER_CONNECTION",
    "AMBIGUOUS": "EXPLORE_GENTLY",
}

def _require_dependency_result(result: object) -> dict:
    """Reject malformed dependency output rather than treating it as no signal."""
    if not isinstance(result, dict):
        raise ValueError("Dependency detector returned an invalid result.")
    level, score = result.get("level"), result.get("score")
    signals, recommendation = result.get("signals"), result.get("recommendation")
    if (
        not isinstance(level, str) or level not in _DEPENDENCY_LEVELS
        or type(score) is not int or score < 0
        or not isinstance(signals, list)
        or any(not isinstance(signal, str) for signal in signals)
        or not isinstance(recommendation, str)
    ):
        raise ValueError("Dependency detector returned an invalid result.")
    return result

def _require_scope_result(result: object) -> dict:
    """Validate scope tier/action pairing before applying a routing decision."""
    if not isinstance(result, dict):
        raise ValueError("Scope classifier returned an invalid result.")
    tier, category = result.get("tier"), result.get("category")
    action, explanation = result.get("action"), result.get("explanation")
    if (
        not isinstance(tier, str) or tier not in _SCOPE_ACTIONS
        or action != _SCOPE_ACTIONS[tier]
        or not isinstance(category, str) or not category.strip()
        or not isinstance(explanation, str) or not explanation.strip()
    ):
        raise ValueError("Scope classifier returned an invalid result.")
    return result

def apply_safety_gate(
    message: str,
    history: list[dict[str, str]],
    memory: dict[str, object] | None,
    selection: dict[str, object],
) -> dict[str, object]:
    """Re-derive safety signals independently after framework selection."""
    _ = memory
    crisis = detect_crisis(message)
    if (
        not isinstance(crisis, dict)
        or type(crisis.get("tier")) is not int
        or crisis["tier"] not in {0, 1, 2}
    ):
        raise ValueError("Crisis detector returned an invalid tier.")
    if crisis["tier"] == 1:
        return {
            "status": "OVERRIDE", "reason": "tier1_crisis", "flags": ["crisis"],
            "selection": {
                "primary_framework": "CRISIS", "secondary_layer": None,
                "mode": "CRISIS", "context": crisis,
                "instruction": (
                    "IMMEDIATE CRISIS RESPONSE. Use CRISIS_RESPONSE[lang] from "
                    "skills/frameworks/emotional-deescalation.md. No other framework. "
                    "No question."
                ),
                "blocked": ["ALL"],
            },
        }

    dependency = _require_dependency_result(
        analyze_dependency(history, current_message=message)
    )
    if dependency["level"] == "HIGH_DEPENDENCY":
        return {
            "status": "OVERRIDE", "reason": "high_dependency",
            "flags": ["dependency"],
            "selection": {
                "primary_framework": "DEPENDENCY", "secondary_layer": None,
                "mode": "MIRROR", "context": dependency,
                "instruction": (
                    "Dependency redirect. Use DEP_REDIRECT from "
                    "skills/frameworks/emotional-deescalation.md. Warm, direct, one "
                    "question pointing toward real-world support."
                ),
                "blocked": ["ALL_FRAMEWORKS"],
            },
        }

    scope = _require_scope_result(classify_message(message))
    if scope["tier"].startswith("BLACKLIST"):
        if scope["category"] == "system_extraction":
            return {
                "status": "BLOCK", "reason": "system_prompt_extraction",
                "flags": ["prompt_extraction"], "selection": selection,
            }
        return {
            "status": "BLOCK", "reason": "out_of_scope",
            "flags": ["scope"], "selection": selection,
        }

    return {
        "status": "PASS", "reason": "no_override",
        "flags": [], "selection": selection,
    }

def main() -> int:
    """Run the safety gate over a JSON payload on standard input."""
    data = read_stdin_json()
    message, history, memory, selection = require_message_history_memory_selection_fields(data)
    result = apply_safety_gate(message, history, memory, selection)
    print(json.dumps(result, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print_json_error(error, ensure_ascii=False)
        raise SystemExit(1) from error
