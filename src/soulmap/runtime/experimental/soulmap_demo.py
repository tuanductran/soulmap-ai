"""Run the framework selector locally from the command line."""

from __future__ import annotations

import argparse
import json

from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_list_field,
)
from soulmap.runtime.routing.framework_selector import select_framework


def run_selector(payload: dict[str, object]) -> dict[str, object]:
    """Validate a demo payload and route it through the framework selector.

    Args:
        payload: Object holding ``message``, ``history``, and ``memory``.

    Returns:
        The selector result.

    Raises:
        RuntimeError: If a field is missing or has the wrong type. This is a
            local demo entry point, so it reports the problem in plain terms
            rather than raising a parse error from deeper in the stack.
    """
    try:
        message = payload["message"]
        history = payload["history"]
        memory = payload["memory"]
    except KeyError as error:
        raise RuntimeError(f"Missing required field: {error.args[0]}") from error

    if not isinstance(message, str):
        raise RuntimeError("Field 'message' must be a string.")
    if not isinstance(history, list):
        raise RuntimeError("Field 'history' must be a list.")
    if not isinstance(memory, dict):
        raise RuntimeError("Field 'memory' must be an object.")

    # Checking that history is a list is not enough. The detectors and the
    # safety gate index each entry as m["content"], so a malformed item
    # crashed the gate with a KeyError rather than being reported here. Every
    # other entry point normalizes through this shared helper, which is what
    # kept them safe.
    normalized_history = require_list_field({"history": history}, "history")

    return select_framework(message, normalized_history, memory)


def main(argv: list[str] | None = None) -> int:
    """Run the framework selector from the command line.

    Accepts either a single message argument or a JSON payload on standard
    input.

    Args:
        argv: Command-line arguments, or None to read from ``sys.argv``.

    Returns:
        0 on success, 1 when the payload is invalid.
    """
    parser = argparse.ArgumentParser(description="Run SoulMap AI framework selector.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--message", type=str, help="Single user message.")
    group.add_argument(
        "--stdin", action="store_true", help="Read JSON payload from stdin."
    )
    args = parser.parse_args(argv)

    if args.stdin:
        try:
            payload = read_stdin_json(strip=True)
        except ValueError as error:
            print_json_error(error)
            return 1
    else:
        payload = {
            "message": args.message,
            "history": [{"role": "user", "content": args.message}],
            "memory": {},
        }

    try:
        data = run_selector(payload)
    except RuntimeError as error:
        print_json_error(error)
        return 1

    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
