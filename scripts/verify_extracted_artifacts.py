"""Verify the extracted shape and content boundary of SoulMap distribution artifacts."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

from soulmap.devtools.packaging.artifact_integrity import (
    ArtifactContentError,
    verify_member_content,
)
from soulmap.devtools.packaging.members import CORE_FILES, PLUGIN_PREFIX, source_members


class ExtractedArtifactError(ValueError):
    """Raised when an archive violates the shipped package contract."""


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


def _markdown_members(actual: set[str]) -> tuple[str, ...]:
    """Return Markdown members that participate in the shipped reference graph."""
    return tuple(
        sorted(
            name
            for name in actual
            if name.endswith(".md") and not name.startswith(PLUGIN_PREFIX)
        )
    )


def _resolve_markdown_target(
    source: str, target: str, *, archive_prefix: str = ""
) -> str | None:
    """Resolve a shipped Markdown link using standard or repository-root semantics."""
    parsed = urlsplit(unquote(target))
    if parsed.scheme or parsed.netloc:
        return None
    raw_path = parsed.path
    if not raw_path:
        return None

    source_path = PurePosixPath(source)
    target_path = PurePosixPath(raw_path)
    if raw_path.startswith("/"):
        candidate = target_path.relative_to("/")
        if archive_prefix:
            candidate = PurePosixPath(archive_prefix) / candidate
    elif raw_path.startswith("skills/") or raw_path in CORE_FILES:
        candidate = (
            PurePosixPath(archive_prefix) / target_path
            if archive_prefix
            else target_path
        )
    else:
        candidate = source_path.parent / target_path

    normalized = PurePosixPath()
    for part in candidate.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if not normalized.parts:
                return None
            normalized = normalized.parent
        else:
            normalized /= part
    normalized_name = normalized.as_posix()
    if archive_prefix and not (
        normalized_name == archive_prefix.rstrip("/")
        or normalized_name.startswith(archive_prefix)
    ):
        return None
    return normalized_name


def _assert_markdown_references(
    archive: zipfile.ZipFile, actual: set[str], *, archive_prefix: str = ""
) -> None:
    """Require every shipped Markdown link to resolve inside the archive."""
    parser = MarkdownIt("commonmark")
    for source in _markdown_members(actual):
        content = archive.read(source).decode("utf-8")
        for token in parser.parse(content):
            if token.type != "inline" or not token.children:
                continue
            line_no = (token.map[0] + 1) if token.map else 1
            for child in token.children:
                if child.type != "link_open":
                    continue
                target = child.attrGet("href") or ""
                if target.startswith(("#", "mailto:", "tel:", "data:")):
                    continue
                parsed = urlsplit(unquote(target))
                if parsed.scheme or parsed.netloc:
                    continue
                resolved = _resolve_markdown_target(
                    source, target, archive_prefix=archive_prefix
                )
                if resolved is None:
                    raise ExtractedArtifactError(
                        f"{source}:{line_no}: link target escapes shipped package: {target!r}"
                    )
                if resolved not in actual and not any(
                    name.startswith(f"{resolved}/") for name in actual
                ):
                    raise ExtractedArtifactError(
                        f"{source}:{line_no}: broken shipped Markdown reference: "
                        f"{target!r} -> {resolved!r}"
                    )


def _assert_expected_members(
    archive_path: Path,
    *,
    repo_root: Path,
    include_plugin: bool,
    archive_prefix: str = "",
) -> None:
    actual, archive = _read_members(archive_path)
    try:
        source_names = source_members(repo_root, include_plugin=include_plugin)
        expected = {f"{archive_prefix}{name}" for name in source_names}
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

        required_core = {f"{archive_prefix}{name}" for name in CORE_FILES}
        if not actual >= required_core:
            raise ExtractedArtifactError(
                f"{archive_path.name} must contain {sorted(required_core)}"
            )

        try:
            verify_member_content(
                archive, repo_root, expected, archive_prefix=archive_prefix
            )
        except ArtifactContentError as exc:
            raise ExtractedArtifactError(f"{archive_path.name}: {exc}") from exc

        if include_plugin:
            if f"{PLUGIN_PREFIX}marketplace.json" not in actual:
                raise ExtractedArtifactError(
                    ".skill artifact must preserve .claude-plugin/marketplace.json"
                )
        elif any(name.startswith(PLUGIN_PREFIX) for name in actual):
            raise ExtractedArtifactError("standard ZIP must exclude .claude-plugin/")

        source_member_names = {
            name[len(archive_prefix) :] if archive_prefix else name for name in actual
        }
        forbidden_members = sorted(
            name
            for name in source_member_names
            if name.startswith(FORBIDDEN_MEMBER_PREFIXES)
        )
        if forbidden_members:
            raise ExtractedArtifactError(
                f"{archive_path.name} contains repository-only members: {forbidden_members}"
            )

        _assert_markdown_references(archive, actual, archive_prefix=archive_prefix)

        for name in sorted(actual):
            source_name = name[len(archive_prefix) :] if archive_prefix else name
            if not source_name.startswith("skills/") or not source_name.endswith(".md"):
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
    _assert_expected_members(
        dist / "soulmap-ai-claude.zip",
        repo_root=repo_root,
        include_plugin=False,
        archive_prefix="soulmap-ai/",
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
    print("PASS extracted artifact boundary: dist/soulmap-ai-claude.zip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
