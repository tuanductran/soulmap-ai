"""Run the framework selector locally from the command line."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

from modules.cli_payload import print_json_error, read_stdin_json


def run_selector(payload: dict[str, object]) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, "-m", "modules.framework_selector"],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    if result.returncode != 0:
        if stdout:
            try:
                data = json.loads(stdout)
            except json.JSONDecodeError:
                data = None
            if isinstance(data, dict) and isinstance(data.get("error"), str):
                raise RuntimeError(data["error"])
        raise RuntimeError(stderr or "framework_selector failed")
    if not stdout:
        raise RuntimeError("framework_selector produced no output")
    return json.loads(stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SoulMap AI framework selector.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--message", type=str, help="Single user message.")
    group.add_argument(
        "--stdin", action="store_true", help="Read JSON payload from stdin."
    )
    args = parser.parse_args()

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
