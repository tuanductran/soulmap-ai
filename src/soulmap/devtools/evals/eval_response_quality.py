"""Deterministic response-quality evaluation runner.

This suite evaluates generated/reference responses against a source-backed
quality rubric. It deliberately reports quality separately from the existing
safety contract: quality is advisory and never replaces deterministic safety
enforcement.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import cast

from soulmap.devtools.evals.eval_responses import (
    _compose_response,
    _load_json,
)
from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.guards.response_contract import grade_response_contract
from soulmap.runtime.guards.response_safety_contract import (
    check_response_safety_contract,
)
from soulmap.runtime.routing.framework_selector import select_framework
from soulmap.runtime.routing.scope_classifier import classify_message

ADVICE_PATTERNS: tuple[str, ...] = (
    r"\byou should\b",
    r"\byou need to\b",
    r"\byou must\b",
    r"\bi recommend\b",
    r"\bthe right thing to do is\b",
    r"\bthe best thing for you is\b",
)

DEPENDENCY_PATTERNS: tuple[str, ...] = (
    r"\bi'?m always here for you\b",
    r"\bcome back anytime\b",
    r"\balways here when you need me\b",
    r"\byou only need me\b",
)

TONE_PATTERNS: tuple[str, ...] = (
    r"\beverything happens for a reason\b",
    r"\btime heals\b",
    r"\bbetter place\b",
    r"\bi'?m sorry for your loss\b",
)

OWNERSHIP_PATTERNS: tuple[str, ...] = (
    r"\bi know exactly what you(?:'re| are) feeling\b",
    r"\bi know what(?:'s| is) best for you\b",
    r"\bthis is what you really feel\b",
)

CERTAINTY_PATTERNS: tuple[str, ...] = (
    r"\bdefinitely\b",
    r"\bwithout doubt\b",
    r"\bthis proves\b",
    r"\bthis confirms\b",
    r"\byou are destined to\b",
)

EXPECTED_FRAMEWORKS = {
    "DE_ESCALATION",
    "MIRROR",
    "CRISIS",
    "DEPENDENCY",
    "GRIEF",
    "EXISTENTIAL",
    "INNER_PARTS",
    "DIRECTION",
    "SHADOW",
    "MEANING_INTEGRATION",
    "SYNTHESIS",
}


def _matches_any(response: str, patterns: tuple[str, ...]) -> bool:
    lowered = response.lower()
    return any(re.search(pattern, lowered) for pattern in patterns)


def grade_response_quality(
    response: str,
    selection: dict[str, object],
    *,
    expected_framework: str,
    epistemic_required: bool = False,
) -> dict[str, object]:
    """Grade response quality without deciding whether the response is safe."""
    contract = grade_response_contract(response, selection)
    framework_ok = selection.get("primary_framework") == expected_framework
    mirror_ok = not _matches_any(response, ADVICE_PATTERNS)
    ownership_ok = not _matches_any(response, OWNERSHIP_PATTERNS)
    tone_ok = not _matches_any(response, TONE_PATTERNS)
    independence_ok = not _matches_any(response, DEPENDENCY_PATTERNS)
    epistemic_ok = not epistemic_required or not _matches_any(
        response, CERTAINTY_PATTERNS
    )

    dimensions = {
        "framework_alignment": framework_ok,
        "mirror_posture": mirror_ok,
        "user_ownership": ownership_ok,
        "response_shape": bool(contract["ok"]),
        "tone_voice": tone_ok,
        "epistemic_framing": epistemic_ok,
        "independence": independence_ok,
    }
    return {
        "status": "PASS" if all(dimensions.values()) else "FAIL",
        "dimensions": dimensions,
        "violations": [name for name, passed in dimensions.items() if not passed],
    }


def _load_quality_fixtures(path: Path) -> list[dict[str, object]]:
    return _load_json(path)


def _evaluate_case(case: dict[str, object], response: str) -> dict[str, object]:
    message = cast(str, case["message"])
    history = cast(
        list[dict[str, str]],
        case.get("history", [{"role": "user", "content": message}]),
    )
    memory = cast(dict[str, object] | None, case.get("memory", {}))
    selection = select_framework(message, history, memory)
    quality = grade_response_quality(
        response,
        selection,
        expected_framework=str(case["expected_primary_framework"]),
        epistemic_required=bool(case.get("epistemic_required", False)),
    )
    safety = check_response_safety_contract(response)
    expected_quality = str(case.get("expected_quality_status", "PASS"))
    expected_safety = str(case.get("expected_safety_status", "PASS"))
    expected_safety_status = (
        "PASS" if expected_safety in {"PASS", "OVERRIDE"} else "FAIL_REWRITE_REQUIRED"
    )
    passed = (
        quality["status"] == expected_quality
        and safety["status"] == expected_safety_status
    )
    return {
        "id": case["id"],
        "ok": passed,
        "quality": quality,
        "safety": {
            "status": safety["status"],
            "categories": safety.get("categories", []),
        },
        "expected": {
            "quality_status": expected_quality,
            "safety_status": expected_safety_status,
        },
    }


def main(argv: list[str] | None = None) -> int:
    """Run the advisory response-quality suite and print JSON results."""
    parser = argparse.ArgumentParser(
        description="Run deterministic response-quality evaluation fixtures."
    )
    parser.parse_args(argv)

    response_cases = _load_json(
        REPO_ROOT / "evals" / "datasets" / "response_generation_cases.json"
    )
    quality_cases = _load_quality_fixtures(
        REPO_ROOT / "evals" / "datasets" / "response_quality_cases.json"
    )

    results: list[dict[str, object]] = []
    framework_set: set[str] = set()
    for case in response_cases:
        message = cast(str, case["message"])
        history = cast(
            list[dict[str, str]],
            case.get("history", [{"role": "user", "content": message}]),
        )
        memory = cast(dict[str, object] | None, case.get("memory", {}))
        selection = select_framework(message, history, memory)
        scope = classify_message(message)
        framework_set.add(str(selection["primary_framework"]))
        response = _compose_response(message, selection, scope)
        enriched = {
            **case,
            "expected_quality_status": "PASS",
            "expected_safety_status": case["expected_safety_status"],
            "epistemic_required": bool(case.get("epistemic_required", False)),
        }
        results.append(_evaluate_case(enriched, response))

    for case in quality_cases:
        results.append(_evaluate_case(case, str(case["response"])))

    coverage_ok = framework_set == EXPECTED_FRAMEWORKS
    all_ok = coverage_ok and all(bool(result["ok"]) for result in results)
    output = {
        "suite": "response_quality",
        "status": "PASS" if all_ok else "FAIL",
        "blocking": False,
        "advisory": True,
        "framework_coverage": sorted(framework_set),
        "framework_coverage_ok": coverage_ok,
        "case_count": len(results),
        "results": results,
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
