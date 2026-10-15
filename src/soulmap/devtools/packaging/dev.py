"""Build, verify, and extract local SoulMap artifacts for development."""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path, PurePosixPath

from soulmap.devtools.packaging import build_skill
from soulmap.devtools.packaging.members import source_members
from soulmap.devtools.support.repo import REPO_ROOT

OUTPUTS = (
    ("soulmap-ai.zip", "zip", False),
    ("soulmap-ai.skill", "skill", True),
)


def _verify_archive(archive_path: Path, expected_members: set[str]) -> None:
    """Reject corrupt archives, unexpected files, and unsafe extraction paths."""
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError(f"Archive contains duplicate members: {archive_path}")
        unsafe = [
            name
            for name in names
            if PurePosixPath(name).is_absolute()
            or "\\" in name
            or ".." in PurePosixPath(name).parts
        ]
        if unsafe:
            raise ValueError(
                f"Archive contains unsafe member paths in {archive_path}: {unsafe[:5]}"
            )
        actual_members = set(names)
        missing = sorted(expected_members - actual_members)
        unexpected = sorted(actual_members - expected_members)
        if missing or unexpected:
            raise ValueError(
                f"Archive member mismatch for {archive_path}: "
                f"missing={missing[:5]}, unexpected={unexpected[:5]}"
            )
        corrupt_member = archive.testzip()
        if corrupt_member is not None:
            raise ValueError(
                f"Archive CRC check failed for {archive_path}: {corrupt_member}"
            )


def _extract_verified(archive_path: Path, destination: Path) -> int:
    """Verify an archive against the package contract, then refresh its output tree."""
    include_plugin = archive_path.name == "soulmap-ai.skill"
    expected_members = source_members(
        archive_path.parents[1], include_plugin=include_plugin
    )
    _verify_archive(archive_path, expected_members)

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(destination)
    print(f"OK (dev extract): {archive_path.name} -> {destination}")
    return len(expected_members)


def main(argv: list[str] | None = None) -> int:
    """Build both artifacts and refresh their verified trees under .soulmap/."""
    parser = argparse.ArgumentParser(
        prog="soulmap dev",
        description=(
            "Build both SoulMap artifacts, verify their contents, and extract them "
            "under .soulmap/ for local inspection. This command does not start a server."
        ),
    )
    parser.parse_args(argv)

    repo_root = REPO_ROOT
    archives = build_skill.build_all(repo_root)
    output_root = repo_root / ".soulmap"
    total_files = 0
    for archive_path, (_, output_name, _) in zip(archives, OUTPUTS, strict=True):
        total_files += _extract_verified(
            archive_path,
            output_root / output_name,
        )
    print(f"OK (dev): {total_files} packaged file entries verified under {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
