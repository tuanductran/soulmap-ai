"""Capture observed dependency-detector results for the Issue #710 matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

CASES: tuple[dict[str, str], ...] = (
    {
        "id": "quoted_issue_example",
        "text": 'My friend said, "you are all I have"; how should I respond?',
    },
    {
        "id": "quoted_known_keyword",
        "text": 'My friend said, "you are all I have"; how should I respond?',
    },
    {
        "id": "third_party_issue_example",
        "text": "My sister says she doesn't need anyone else because her chatbot understands her.",
    },
    {
        "id": "third_party_known_keyword",
        "text": "My coworker told his chatbot you're the only one who understands me.",
    },
    {
        "id": "hypothetical_issue_example",
        "text": "What would count as an unhealthy dependency signal in a fictional example?",
    },
    {
        "id": "hypothetical_known_keyword",
        "text": "If I ever said you are all I have, that would be a fictional example.",
    },
    {
        "id": "user_endorsed_issue_example",
        "text": "I feel like you are all I have, and I have no one else.",
    },
    {
        "id": "negation_issue_example",
        "text": "I don't feel that you are the only one who understands me.",
    },
)


def _capture() -> dict[str, Any]:
    """Run the imported detector against every fixed case."""
    from soulmap.runtime.detectors.dependency_detector import analyze_dependency

    results: list[dict[str, Any]] = []
    for case in CASES:
        observed = analyze_dependency(
            [{"role": "user", "content": case["text"]}]
        )
        results.append(
            {
                "id": case["id"],
                "text": case["text"],
                "score": observed.get("score"),
                "level": observed.get("level"),
                "signals": observed.get("signals", []),
            }
        )
    return {"cases": results}


def _compare(baseline_path: Path, candidate_path: Path, report_path: Path | None) -> int:
    """Compare captured baseline and candidate observations."""
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    baseline_by_id = {case["id"]: case for case in baseline["cases"]}
    candidate_by_id = {case["id"]: case for case in candidate["cases"]}

    comparisons: list[dict[str, Any]] = []
    for case in CASES:
        before = baseline_by_id.get(case["id"])
        after = candidate_by_id.get(case["id"])
        comparisons.append(
            {
                "id": case["id"],
                "text": case["text"],
                "baseline": before,
                "candidate": after,
                "changed": before != after,
            }
        )

    report = {
        "baseline_file": str(baseline_path),
        "candidate_file": str(candidate_path),
        "changed_case_count": sum(item["changed"] for item in comparisons),
        "comparisons": comparisons,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0


def main() -> int:
    """Capture observations or compare two captured matrices."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write observed results as JSON.")
    parser.add_argument(
        "--compare",
        nargs=2,
        type=Path,
        metavar=("BASELINE_JSON", "CANDIDATE_JSON"),
        help="Compare two previously captured matrices.",
    )
    parser.add_argument("--report", type=Path, help="Optional comparison report path.")
    args = parser.parse_args()

    if args.compare:
        return _compare(args.compare[0], args.compare[1], args.report)

    result = _capture()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
