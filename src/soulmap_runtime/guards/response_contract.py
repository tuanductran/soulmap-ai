"""Check response-level SoulMap contract rules."""

from __future__ import annotations

import json
import re
import sys

from soulmap_runtime.io.cli_payload import (
    parse_json_object,
    require_dict_field,
    require_str_field,
)

QUESTION_RE = re.compile(r"\?")


def grade_response_contract(
    response: str,
    selection: dict[str, object],
) -> dict[str, object]:
    violations: list[str] = []
    stripped = response.strip()

    question_count = len(QUESTION_RE.findall(stripped))
    if question_count > 1:
        violations.append("multiple_questions")
    if question_count == 1 and not stripped.endswith("?"):
        violations.append("question_not_last")
    if stripped.startswith("?"):
        violations.append("starts_with_question")
    if ";" in stripped:
        violations.append("semicolon")
    if "\n-" in stripped or stripped.startswith("- "):
        violations.append("bullets")

    primary = str(selection.get("primary_framework", ""))
    mode = str(selection.get("mode", ""))
    if primary == "CRISIS" and question_count:
        violations.append("crisis_no_question")
    if mode == "SANCTUARY" and question_count:
        violations.append("sanctuary_no_question")

    return {"ok": not violations, "violations": violations}


def main() -> int:
    data = parse_json_object(sys.stdin.read())
    response = require_str_field(data, "response")
    selection = require_dict_field(data, "selection")
    result = grade_response_contract(response, selection)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        raise SystemExit(1) from error
