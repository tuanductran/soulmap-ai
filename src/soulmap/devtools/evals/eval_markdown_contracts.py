from __future__ import annotations

import argparse
import json
from typing import NotRequired, TypedDict

from soulmap.devtools.support.repo import REPO_ROOT


class FileRule(TypedDict):
    path: str
    must_include_all: NotRequired[list[str]]
    must_include_any: NotRequired[list[str]]
    must_not_include_any: NotRequired[list[str]]


class ContractCase(TypedDict):
    id: str
    summary: str
    markdown_targets: NotRequired[list[FileRule]]
    runtime_targets: NotRequired[list[FileRule]]


def _load_cases() -> list[ContractCase]:
    path = REPO_ROOT / "evals" / "datasets" / "markdown_contract_cases.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _evaluate_rule(rule: FileRule) -> dict[str, object]:
    rel_path = rule["path"]
    path = REPO_ROOT / rel_path
    exists = path.exists()
    text = path.read_text(encoding="utf-8") if exists else ""

    must_include_all = rule.get("must_include_all", [])
    must_include_any = rule.get("must_include_any", [])
    must_not_include_any = rule.get("must_not_include_any", [])

    matched_all = [snippet for snippet in must_include_all if snippet in text]
    matched_any = [snippet for snippet in must_include_any if snippet in text]
    blocked_hits = [snippet for snippet in must_not_include_any if snippet in text]

    include_all_ok = len(matched_all) == len(must_include_all)
    include_any_ok = not must_include_any or bool(matched_any)
    exclude_ok = not blocked_hits
    ok = exists and include_all_ok and include_any_ok and exclude_ok

    return {
        "path": rel_path,
        "exists": exists,
        "chars": len(text),
        "must_include_all": must_include_all,
        "matched_all": matched_all,
        "must_include_any": must_include_any,
        "matched_any": matched_any,
        "must_not_include_any": must_not_include_any,
        "blocked_hits": blocked_hits,
        "ok": ok,
    }


def run_markdown_contract_eval(*, case_id: str | None = None) -> dict[str, object]:
    cases = _load_cases()
    if case_id is not None:
        cases = [case for case in cases if case["id"] == case_id]

    results: list[dict[str, object]] = []
    failed_checks = 0
    total_rules = 0

    for case in cases:
        runtime_results = [
            _evaluate_rule(rule) for rule in case.get("runtime_targets", [])
        ]
        markdown_results = [
            _evaluate_rule(rule) for rule in case.get("markdown_targets", [])
        ]
        case_results = runtime_results + markdown_results
        total_rules += len(case_results)
        case_failed_checks = sum(1 for item in case_results if not item["ok"])
        failed_checks += case_failed_checks

        results.append(
            {
                "id": case["id"],
                "summary": case["summary"],
                "runtime_targets": runtime_results,
                "markdown_targets": markdown_results,
                "ok": case_failed_checks == 0,
            }
        )

    return {
        "ok": failed_checks == 0,
        "summary": {
            "cases": len(cases),
            "rules": total_rules,
            "failed_checks": failed_checks,
        },
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run markdown contract sync checks from "
            "evals/datasets/markdown_contract_cases.json."
        )
    )
    parser.add_argument(
        "--case", dest="case_id", help="Only evaluate one contract case."
    )
    args = parser.parse_args(argv)

    result = run_markdown_contract_eval(case_id=args.case_id)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
