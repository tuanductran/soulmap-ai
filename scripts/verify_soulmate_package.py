"""Verify the isolated Soulmate wheel and source distribution boundaries."""

from __future__ import annotations

import argparse
import re
import sys
import tarfile
import zipfile
from pathlib import Path

_WHEEL_RE = re.compile(r"^soulmate_ai-(?P<version>[^-]+)-py3-none-any\.whl$")
_SDIST_RE = re.compile(r"^soulmate_ai-(?P<version>[^/]+)\.tar\.gz$")
_FORBIDDEN_MARKERS = ("soulmap", "skills", "reference")


def _version_from_name(path: Path, pattern: re.Pattern[str]) -> str:
    match = pattern.match(path.name)
    if match is None:
        raise ValueError(f"Unexpected Soulmate artifact name: {path.name}")
    return match.group("version")


def _verify_wheel(path: Path, version: str) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
    if any(
        any(marker in name.lower() for marker in _FORBIDDEN_MARKERS) for name in names
    ):
        raise ValueError(f"Wheel contains forbidden SoulMap content: {path}")
    expected_prefixes = (
        "soulmate/",
        f"soulmate_ai-{version}.dist-info/",
    )
    unexpected = [name for name in names if not name.startswith(expected_prefixes)]
    if unexpected:
        raise ValueError(f"Wheel contains unexpected paths: {unexpected}")
    if not any(name == "soulmate/__init__.py" for name in names):
        raise ValueError("Wheel is missing soulmate/__init__.py")


def _verify_sdist(path: Path, version: str) -> None:
    root = f"soulmate_ai-{version}/"
    with tarfile.open(path, "r:gz") as archive:
        names = archive.getnames()
    if any(
        any(marker in name.lower() for marker in _FORBIDDEN_MARKERS) for name in names
    ):
        raise ValueError(
            f"Source distribution contains forbidden SoulMap content: {path}"
        )
    expected_prefixes = (
        f"{root}README.md",
        f"{root}LICENSE",
        f"{root}pyproject.toml",
        f"{root}PKG-INFO",
        f"{root}src/soulmate/",
    )
    unexpected = [
        name
        for name in names
        if name != root.rstrip("/")
        and not any(
            name == prefix or name.startswith(prefix) for prefix in expected_prefixes
        )
    ]
    if unexpected:
        raise ValueError(f"Source distribution contains unexpected paths: {unexpected}")
    if f"{root}src/soulmate/__init__.py" not in names:
        raise ValueError("Source distribution is missing src/soulmate/__init__.py")


def verify(wheel: Path, sdist: Path, expected_version: str | None = None) -> None:
    wheel_version = _version_from_name(wheel, _WHEEL_RE)
    sdist_version = _version_from_name(sdist, _SDIST_RE)
    if wheel_version != sdist_version:
        raise ValueError("Wheel and source distribution versions do not match")
    if expected_version is not None and wheel_version != expected_version:
        raise ValueError(f"Expected version {expected_version}, found {wheel_version}")
    _verify_wheel(wheel, wheel_version)
    _verify_sdist(sdist, sdist_version)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--sdist", type=Path, required=True)
    parser.add_argument("--version")
    args = parser.parse_args(argv)
    verify(args.wheel, args.sdist, args.version)
    print(f"PASS: verified Soulmate package {args.version or 'artifacts'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1) from error
