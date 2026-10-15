"""Build, verify, and extract local SoulMap artifacts for development."""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path, PurePosixPath

from soulmap.devtools.packaging import build_skill
from soulmap.devtools.packaging.members import source_members
from soulmap.devtools.support.repo import REPO_ROOT


def _verify_archive(
    archive_path: Path, expected_members: set[str], source_root: Path
) -> None:
    """Reject corrupt, stale, unexpected, or unsafe archive contents."""
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
        stale_members = [
            name
            for name in names
            if archive.read(name) != (source_root / name).read_bytes()
        ]
        if stale_members:
            raise ValueError(
                f"Archive content differs from source for {archive_path}: "
                f"{stale_members[:5]}"
            )


def _extract_verified(
    archive_path: Path, destination: Path, source_root: Path
) -> int:
    """Verify an archive against the package contract, then refresh its output tree."""
    include_plugin = archive_path.name == "soulmap-ai.skill"
    expected_members = source_members(source_root, include_plugin=include_plugin)
    _verify_archive(archive_path, expected_members, source_root)

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
    for archive_path, output_name in zip(archives, ("zip", "skill"), strict=True):
        total_files += _extract_verified(
            archive_path,
            output_root / output_name,
            repo_root,
        )
    print(f"OK (dev): {total_files} packaged file entries verified under {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
