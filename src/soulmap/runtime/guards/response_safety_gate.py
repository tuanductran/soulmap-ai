"""Apply independent safety overrides after framework selection."""

from __future__ import annotations

import json

from soulmap.runtime.detectors.crisis_detector import detect_crisis
from soulmap.runtime.detectors.dependency_detector import analyze_dependency
from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_memory_selection_fields,
)
from soulmap.runtime.routing.scope_classifier import classify_message


def apply_safety_gate(
    message: str,
    history: list[dict[str, str]],
    memory: dict[str, object] | None,
    selection: dict[str, object],
) -> dict[str, object]:
    _ = memory
    # Independent of the selector's early check, re-derive crisis from the raw
    # message here so a selector-side miss cannot bypass the highest-priority
    # override. See ADR 0001 for the defense-in-depth rationale.
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
        if scope.get("category") == "system_extraction":
            return {
                "status": "BLOCK",
                "reason": "system_prompt_extraction",
                "flags": ["prompt_extraction"],
                "selection": selection,
            }
        return {
            "status": "BLOCK",
            "reason": "out_of_scope",
            "flags": ["scope"],
            "selection": selection,
        }

    return {
        "status": "PASS",
        "reason": "no_override",
        "flags": [],
        "selection": selection,
    }


def main() -> int:
    data = read_stdin_json()
    message, history, memory, selection = (
        require_message_history_memory_selection_fields(data)
    )
    result = apply_safety_gate(message, history, memory, selection)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print_json_error(error, ensure_ascii=False)
        raise SystemExit(1) from error
