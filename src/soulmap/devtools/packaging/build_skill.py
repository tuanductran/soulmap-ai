"""Build both SoulMap AI distribution artifacts from the canonical source set.

The default command always creates the standard ZIP and the Claude-oriented
.skill archive. Their only packaging difference is the preserved plugin metadata.
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

from soulmap.devtools.packaging.members import is_ignored as _is_ignored
from soulmap.devtools.packaging.members import load_distignore as _load_distignore
from soulmap.devtools.packaging.members import source_paths
from soulmap.devtools.support.repo import REPO_ROOT


def _iter_inputs(repo_root: Path) -> list[Path]:
    """Return files shared by the ZIP and .skill archives."""
    return source_paths(repo_root, include_plugin=False)


def _iter_claude_plugin_inputs(repo_root: Path) -> list[Path]:
    """Return plugin files preserved only in the .skill archive."""
    return [
        path
        for path in source_paths(repo_root, include_plugin=True)
        if path.relative_to(repo_root).as_posix().startswith(".claude-plugin/")
    ]


def _assert_single_skill_entrypoint(repo_root: Path) -> None:
    """Reject distributable Skill sources with multiple SKILL.md entrypoints."""
    skill_files = [path for path in _iter_inputs(repo_root) if path.name == "SKILL.md"]
    if (
        len(skill_files) != 1
        or skill_files[0].relative_to(repo_root).as_posix() != "SKILL.md"
    ):
        paths = ", ".join(
            path.relative_to(repo_root).as_posix() for path in skill_files
        )
        raise ValueError(
            "SoulMap distribution requires exactly one root SKILL.md; "
            f"found: {paths or 'none'}"
        )


def _build_archive(
    repo_root: Path,
    output_name: str,
    label: str,
    *,
    include_claude_plugin: bool,
) -> Path:
    """Build an archive from the canonical shipped files."""
    out_dir = repo_root / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / output_name

    patterns = _load_distignore(repo_root)
    inputs = _iter_inputs(repo_root)
    if include_claude_plugin:
        _assert_single_skill_entrypoint(repo_root)
        inputs = sorted(set(inputs + _iter_claude_plugin_inputs(repo_root)))

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in inputs:
            relative = path.relative_to(repo_root).as_posix()
            if not _is_ignored(relative, patterns):
                archive.write(path, arcname=relative)

    size_kb = out_path.stat().st_size // 1024
    print(f"OK ({label}): {out_path}  (~{size_kb}KB)")
    return out_path


def build_zip(repo_root: Path) -> Path:
    """Build dist/soulmap-ai.zip without Claude plugin metadata."""
    return _build_archive(
        repo_root,
        "soulmap-ai.zip",
        "zip",
        include_claude_plugin=False,
    )


def build_skill(repo_root: Path) -> Path:
    """Build dist/soulmap-ai.skill with Claude plugin metadata preserved."""
    return _build_archive(
        repo_root,
        "soulmap-ai.skill",
        "skill",
        include_claude_plugin=True,
    )


def build_all(repo_root: Path) -> tuple[Path, Path]:
    """Build and return both supported distribution artifacts."""
    return build_zip(repo_root), build_skill(repo_root)


def main(argv: list[str] | None = None) -> int:
    """Build both distribution artifacts; artifact selection is not configurable."""
    parser = argparse.ArgumentParser(
        prog="soulmap build",
        description="Build both SoulMap AI distribution artifacts.",
    )
    parser.parse_args(argv)
    build_all(REPO_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
