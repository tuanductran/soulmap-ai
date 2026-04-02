"""Run the framework selector locally from the command line."""

from __future__ import annotations

import argparse
import json

from soulmap.runtime.io.cli_payload import print_json_error, read_stdin_json
from soulmap.runtime.routing.framework_selector import select_framework


def run_selector(payload: dict[str, object]) -> dict[str, object]:
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

    return select_framework(message, history, memory)


def main(argv: list[str] | None = None) -> int:
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
