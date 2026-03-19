"""Runs automated safety red-teaming across detectors to enforce AGENTS.md bounds."""

from __future__ import annotations

import json
import os
import sys

# Assume script run from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.crisis_detector import detect_crisis
from modules.dependency_detector import analyze_dependency
from modules.resource_sanitizer import check_banned_language


def run_tests() -> int:
    with open("tests/safety_test_cases.json", encoding="utf-8") as file:
        cases = json.load(file)

    failed = 0
    print("Running Soulmap Safety Red-Teaming...\n")

    for case in cases:
        print(f"Executing {case['id']} ({case['category']})... ", end="")
        if case["category"] == "CRISIS":
            result = detect_crisis(case["input"])
            if result.get("tier") == 1:
                print("PASS")
            else:
                print("FAIL")
                failed += 1

        elif case["category"] == "DEPENDENCY":
            result = analyze_dependency(case["history"])
            if result.get("level") == "HIGH_DEPENDENCY":
                print("PASS")
            else:
                print("FAIL")
                failed += 1

        elif case["category"] == "NO_ADVICE":
            result = check_banned_language(case["output"])
            if result.get("status") == "FAIL_REWRITE_REQUIRED":
                print("PASS")
            else:
                print("FAIL")
                failed += 1

    print(
        f"\nTotal Cases: {len(cases)} | Passed: {len(cases) - failed} | Failed: {failed}"
    )
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(run_tests())
