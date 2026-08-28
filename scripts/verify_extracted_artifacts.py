"""Verify the extracted shape and content boundary of SoulMap distribution artifacts."""

from __future__ import annotations

import argparse
import fnmatch
import sys
import zipfile
from pathlib import Path, PurePosixPath


class ExtractedArtifactError(ValueError):
    """Raised when an archive violates the shipped package contract."""


CORE_FILES = {"LICENSE", "AGENTS.md", "SKILL.md"}
PLUGIN_PREFIX = ".claude-plugin/"
FORBIDDEN_MEMBER_PREFIXES = (
    ".claude/",
    "docs/",
    "dist/",
    "library/",
    "scripts/",
    "src/",
    "templates/",
    "tests/",
)
FORBIDDEN_SKILL_REFERENCES = (
    "src/soulmap/",
    "docs/engineering/",
    "tests/",
    ".claude/",
    ".github/",
    "templates/",
    "scripts/",
    "library/",
    "pyproject.toml",
    "uv.lock",
    ".py",
)


def _distignore_patterns(repo_root: Path) -> list[str]:
    path = repo_root / ".distignore"
    if not path.is_file():
        return []
    return [
        line
        for raw in path.read_text(encoding="utf-8").splitlines()
        if (line := raw.strip()) and not line.startswith("#")
    ]


def _is_ignored(relative: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(relative, pattern) for pattern in patterns)


def _source_members(repo_root: Path, *, include_plugin: bool) -> set[str]:
    patterns = _distignore_patterns(repo_root)
    paths: set[Path] = set()
    for name in CORE_FILES:
        candidate = repo_root / name
        if candidate.is_file():
            paths.add(candidate)
    skills_root = repo_root / "skills"
    if skills_root.is_dir():
        paths.update(path for path in skills_root.rglob("*") if path.is_file())
    if include_plugin:
        plugin_root = repo_root / ".claude-plugin"
        if plugin_root.is_dir():
            paths.update(path for path in plugin_root.rglob("*") if path.is_file())

    members: set[str] = set()
    for path in paths:
        relative = path.relative_to(repo_root).as_posix()
        if not _is_ignored(relative, patterns):
            members.add(relative)
    return members


def _read_members(archive_path: Path) -> tuple[set[str], zipfile.ZipFile]:
    if not archive_path.is_file():
        raise ExtractedArtifactError(f"artifact not found: {archive_path}")
    try:
        archive = zipfile.ZipFile(archive_path)
    except zipfile.BadZipFile as exc:
        raise ExtractedArtifactError(
            f"not a valid ZIP archive: {archive_path}"
        ) from exc
    names = set(archive.namelist())
    for name in names:
        parsed = PurePosixPath(name)
        if name.startswith("/") or ".." in parsed.parts:
            archive.close()
            raise ExtractedArtifactError(f"unsafe archive member path: {name}")
    return names, archive


def _assert_expected_members(
    archive_path: Path,
    *,
    repo_root: Path,
    include_plugin: bool,
) -> None:
    actual, archive = _read_members(archive_path)
    try:
        expected = _source_members(repo_root, include_plugin=include_plugin)
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        if missing:
            raise ExtractedArtifactError(
                f"{archive_path.name} is missing shipped members: {missing}"
            )
        if unexpected:
            raise ExtractedArtifactError(
                f"{archive_path.name} contains unexpected members: {unexpected}"
            )

        if not actual >= CORE_FILES:
            raise ExtractedArtifactError(
                f"{archive_path.name} must contain {sorted(CORE_FILES)}"
            )

        if include_plugin:
            if ".claude-plugin/marketplace.json" not in actual:
                raise ExtractedArtifactError(
                    ".skill artifact must preserve .claude-plugin/marketplace.json"
                )
        elif any(name.startswith(PLUGIN_PREFIX) for name in actual):
            raise ExtractedArtifactError("standard ZIP must exclude .claude-plugin/")

        forbidden_members = sorted(
            name for name in actual if name.startswith(FORBIDDEN_MEMBER_PREFIXES)
        )
        if forbidden_members:
            raise ExtractedArtifactError(
                f"{archive_path.name} contains repository-only members: {forbidden_members}"
            )

        for name in sorted(actual):
            if not name.startswith("skills/") or not name.endswith(".md"):
                continue
            content = archive.read(name).decode("utf-8")
            violations = [
                reference
                for reference in FORBIDDEN_SKILL_REFERENCES
                if reference in content
            ]
            if violations:
                raise ExtractedArtifactError(
                    f"{archive_path.name}:{name} contains forbidden shipped references: "
                    f"{violations}"
                )
    finally:
        archive.close()


def verify_artifacts(repo_root: Path) -> None:
    """Verify both generated artifacts against the repository package contract."""
    dist = repo_root / "dist"
    _assert_expected_members(
        dist / "soulmap-ai.zip",
        repo_root=repo_root,
        include_plugin=False,
    )
    _assert_expected_members(
        dist / "soulmap-ai.skill",
        repo_root=repo_root,
        include_plugin=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify extracted SoulMap ZIP and .skill artifact boundaries."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(),
        help="Repository root containing dist/ and skills/ (default: current directory)",
    )
    args = parser.parse_args(argv)
    try:
        verify_artifacts(args.root.resolve())
    except ExtractedArtifactError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("PASS extracted artifact boundary: dist/soulmap-ai.zip")
    print("PASS extracted artifact boundary: dist/soulmap-ai.skill")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
