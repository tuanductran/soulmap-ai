"""Apply independent safety overrides after framework selection."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import (
    parse_json_object,
    require_dict_field,
    require_list_field,
    require_str_field,
)
from modules.crisis_detector import detect_crisis
from modules.dependency_detector import analyze_dependency
from modules.scope_classifier import classify_message


def apply_safety_gate(
    message: str,
    history: list[dict[str, str]],
    memory: dict[str, object] | None,
    selection: dict[str, object],
) -> dict[str, object]:
    _ = memory
    crisis = detect_crisis(message)
    if crisis.get("tier") == 1:
        return {
            "status": "OVERRIDE",
            "reason": "tier1_crisis",
            "flags": ["crisis"],
            "selection": {
                "primary_framework": "CRISIS",
                "secondary_layer": None,
                "mode": "CRISIS",
                "context": crisis,
                "instruction": (
                    "IMMEDIATE CRISIS RESPONSE. Use CRISIS_RESPONSE[lang] from "
                    "skills/frameworks/emotional-deescalation.md. No other framework. "
                    "No question."
                ),
                "blocked": ["ALL"],
            },
        }

    dependency = analyze_dependency(history)
    if dependency.get("level") == "HIGH_DEPENDENCY":
        return {
            "status": "OVERRIDE",
            "reason": "high_dependency",
            "flags": ["dependency"],
            "selection": {
                "primary_framework": "DEPENDENCY",
                "secondary_layer": None,
                "mode": "MIRROR",
                "context": dependency,
                "instruction": (
                    "Dependency redirect. Use DEP_REDIRECT from "
                    "skills/frameworks/emotional-deescalation.md. Warm, direct, one "
                    "question pointing toward real-world support."
                ),
                "blocked": ["ALL_FRAMEWORKS"],
            },
        }

    scope = classify_message(message)
    if str(scope.get("tier", "")).startswith("BLACKLIST"):
        return {
            "status": "BLOCK",
            "reason": "out_of_scope",
            "flags": ["scope"],
            "selection": selection,
        }

    if "system prompt" in message.lower() or "instructions" in message.lower():
        return {
            "status": "BLOCK",
            "reason": "system_prompt_extraction",
            "flags": ["prompt_extraction"],
            "selection": selection,
        }

    return {
        "status": "PASS",
        "reason": "no_override",
        "flags": [],
        "selection": selection,
    }


def main() -> int:
    data = parse_json_object(sys.stdin.read())
    message = require_str_field(data, "message")
    history = require_list_field(data, "history")
    memory = require_dict_field(data, "memory")
    selection = require_dict_field(data, "selection")
    result = apply_safety_gate(message, history, memory, selection)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        raise SystemExit(1) from error
