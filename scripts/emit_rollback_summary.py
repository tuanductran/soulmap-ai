"""Emit a deterministic rollback verification summary for GitHub Actions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_summary(\n    verification: dict[str, object], release_ref: str\n) -> dict[str, object]:
    """Build the public rollback verification summary from release evidence."""
    status = verification.get("status")
    version = verification.get("version")
    if not isinstance(status, str):
        raise ValueError("release verification status must be a string")
    if not isinstance(version, str):
        raise ValueError("release verification version must be a string")
    return {
        "status": status,
        "release_ref": release_ref,
        "version": version,
        "rollback_ready": status == "pass",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(\n        "--verification", type=Path, default=Path("dist/release-verification.json")\n    )
    parser.add_argument("--release-ref", required=True)
    args = parser.parse_args()

    verification = json.loads(args.verification.read_text(encoding="utf-8"))
    if not isinstance(verification, dict):
        raise ValueError("release verification must be a JSON object")
    print(json.dumps(build_summary(verification, args.release_ref), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
