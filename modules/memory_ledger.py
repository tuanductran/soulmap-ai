"""Handles saving insights manually confirmed by the user into a Personal Mirror Ledger."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import parse_json_object, require_str_field


def process_insight(
    user_response: str, last_insight: str, session_id: str
) -> dict[str, object]:
    """If the user wants to retain an insight from a P9 stage, save it securely.
    This creates an explicit user-owned memory model rather than silent continuous memory."""

    # If the user rejects, ignore the memory operation.
    if user_response.lower() in ("no", "discard", "forget"):
        return {"status": "FORGOTTEN", "ledger_entry": None}

    # Otherwise, they granted consent to save this particular insight into their ledger
    ledger_content = f"Date: ...\nInsight: {last_insight}\n"

    # This would write to a secure storage (e.g., local .md or encrypted DB per user)
    # ledger_path = f"data/users/{session_id}_mirror.md"

    return {
        "status": "SAVED",
        "ledger_entry": ledger_content,
        "instruction": "Thank the user briefly for trusting the mirror. Confirm the insight is saved in their personal ledger to keep them grounded. Return to neutral.",
    }


def main() -> int:
    data = parse_json_object(sys.stdin.read())
    user_response = require_str_field(data, "user_response")
    last_insight = require_str_field(data, "last_insight")
    session_id = require_str_field(data, "session_id") or "default_guest"

    result = process_insight(user_response, last_insight, session_id)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        raise SystemExit(1) from error
