from __future__ import annotations

import json
from pathlib import Path

from modules.framework_selector import select_framework
from modules.response_contract import grade_response_contract
from tools._repo import REPO_ROOT


def _load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    _ = argv
    selector_cases = _load_json(REPO_ROOT / "evals" / "selector_cases.json")
    response_cases = _load_json(REPO_ROOT / "evals" / "response_cases.json")
    results: list[dict[str, object]] = []
    ok = True

    for case in selector_cases:
        selection = select_framework(
            case["message"],
            case.get("history", [{"role": "user", "content": case["message"]}]),
            case.get("memory", {}),
        )
        passed = selection["primary_framework"] == case["expected_primary_framework"]
        ok = ok and passed
        results.append(
            {
                "suite": "selector",
                "id": case["id"],
                "ok": passed,
                "expected": case["expected_primary_framework"],
                "actual": selection["primary_framework"],
            }
        )

    for case in response_cases:
        grade = grade_response_contract(case["response"], case["selection"])
        passed = bool(grade["ok"]) is bool(case["expected_ok"])
        ok = ok and passed
        results.append(
            {
                "suite": "response_contract",
                "id": case["id"],
                "ok": passed,
                "expected": case["expected_ok"],
                "actual": grade["ok"],
            }
        )

    print(json.dumps({"ok": ok, "results": results}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
