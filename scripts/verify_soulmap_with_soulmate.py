from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

from soulmap.devtools.packaging.composition import (
    CompositionError,
    _artifact_files,
    _scope_entries,
)


class CompositionVerificationError(ValueError):
    """Raised when a composed artifact is not an exact approved projection."""


def _verify(path: Path, *, include_plugin: bool) -> dict[str, Any]:
    if not path.is_file():
        raise CompositionVerificationError(f"missing artifact: {path}")
    expected = _artifact_files(include_plugin=include_plugin)
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise CompositionVerificationError("duplicate archive members")
            actual = {name: archive.read(name) for name in names}
    except (OSError, zipfile.BadZipFile, RuntimeError) as error:
        raise CompositionVerificationError(f"cannot read artifact: {path}") from error
    expected_names = set(expected)
    actual_names = set(actual)
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        raise CompositionVerificationError(
            f"member parity failed: missing={missing} extra={extra}"
        )
    for name, content in expected.items():
        if actual[name] != content:
            raise CompositionVerificationError(f"byte parity failed: {name}")
    forbidden_fragments = (
        "src/soulmap/runtime/knowledge/soulmate_consumer_scope.json",
        "packages/soulmate/skills",
        "scripts/build_soulmap_with_soulmate.py",
        "soulmap_consumer_scope.json",
    )
    for name, content in actual.items():
        if any(fragment.encode() in content for fragment in forbidden_fragments):
            raise CompositionVerificationError(
                f"source-only metadata leaked into {name}"
            )
    expected_entries = _scope_entries()
    projection = json.loads(actual["soulmate/manifest.json"].decode("utf-8"))
    if [entry["id"] for entry in projection["entries"]] != [
        entry["id"] for entry in expected_entries
    ]:
        raise CompositionVerificationError(
            "composition projection order or ids drifted"
        )
    return {
        "artifact": str(path),
        "members": len(names),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "soulmate_entries": len(expected_entries),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify SoulMap-with-Soulmate artifacts"
    )
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument("--skill", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        results = [
            _verify(args.zip, include_plugin=False),
            _verify(args.skill, include_plugin=True),
        ]
    except (
        CompositionError,
        CompositionVerificationError,
        KeyError,
        json.JSONDecodeError,
    ) as error:
        print(f"ERROR composed artifact verification: {error}", file=sys.stderr)
        return 1
    for result in results:
        print(
            f"PASS composed artifact: {result['artifact']} "
            f"members={result['members']} entries={result['soulmate_entries']} "
            f"sha256={result['sha256']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
