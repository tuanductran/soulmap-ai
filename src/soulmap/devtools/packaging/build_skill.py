"""Build distribution artifacts for SoulMap AI.

Flags
-----
default   Build dist/soulmap-ai.zip   (when no flag is given)
--skill   Build dist/soulmap-ai.skill

Examples
--------
uv run soulmap build                  # zip build
uv run soulmap build --skill          # .skill build

Formats
-------
soulmap-ai.zip
    Standard distribution zip for manual extraction and document-based tools.
    Includes root SKILL.md, AGENTS.md, LICENSE, and skills/.
    Excludes .claude-plugin/ and templates/ (internal-only, not shipped).

soulmap-ai.skill
    Skill-oriented archive with the same core knowledge files as the zip build.
    Also includes the full .claude-plugin/ directory without rewriting it.
    Excludes templates/ (internal-only, not shipped).
"""

from __future__ import annotations

import argparse
import fnmatch
import textwrap
import zipfile
from pathlib import Path

from soulmap.devtools.support.repo import REPO_ROOT

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _load_distignore(repo_root: Path) -> list[str]:
    distignore = repo_root / ".distignore"
    if not distignore.is_file():
        return []
    patterns: list[str] = []
    for raw in distignore.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _is_ignored(rel: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, pat) for pat in patterns)


def _iter_inputs(repo_root: Path) -> list[Path]:
    """Return files shared by the zip and .skill archives."""
    paths: list[Path] = []
    for name in ["LICENSE", "AGENTS.md", "SKILL.md"]:
        candidate = repo_root / name
        if candidate.is_file():
            paths.append(candidate)

    for folder in ["skills"]:
        base = repo_root / folder
        for path in base.rglob("*"):
            if path.is_file():
                paths.append(path)

    return sorted(set(paths))


def _iter_claude_plugin_inputs(repo_root: Path) -> list[Path]:
    """Return the .claude-plugin files preserved only in the .skill archive."""
    base = repo_root / ".claude-plugin"
    if not base.is_dir():
        return []
    return sorted(path for path in base.rglob("*") if path.is_file())


def _build_archive(
    repo_root: Path,
    output_name: str,
    label: str,
    *,
    include_claude_plugin: bool,
) -> Path:
    """Build an archive from the requested file set using the requested filename."""
    out_dir = repo_root / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / output_name

    patterns = _load_distignore(repo_root)
    inputs = _iter_inputs(repo_root)
    if include_claude_plugin:
        inputs = sorted(set(inputs + _iter_claude_plugin_inputs(repo_root)))

    if out_path.exists():
        out_path.unlink()

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in inputs:
            rel = path.relative_to(repo_root).as_posix()
            if _is_ignored(rel, patterns):
                continue
            archive.write(path, arcname=rel)

    size_kb = out_path.stat().st_size // 1024
    print(f"OK ({label}): {out_path}  (~{size_kb}KB)")
    return out_path


# ---------------------------------------------------------------------------
# Output 1: ZIP
# ---------------------------------------------------------------------------


def build_zip(repo_root: Path) -> Path:
    """Build dist/soulmap-ai.zip."""
    return _build_archive(
        repo_root,
        "soulmap-ai.zip",
        "zip",
        include_claude_plugin=False,
    )


# ---------------------------------------------------------------------------
# Output 2: .skill
# ---------------------------------------------------------------------------


def build_skill(repo_root: Path) -> Path:
    """Build dist/soulmap-ai.skill with .claude-plugin preserved."""
    return _build_archive(
        repo_root,
        "soulmap-ai.skill",
        "skill",
        include_claude_plugin=True,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="soulmap build",
        description="Build SoulMap AI distribution artifacts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              uv run soulmap build           build the standard zip
              uv run soulmap build --skill   build the .skill package
        """),
    )
    parser.add_argument(
        "--skill",
        action="store_true",
        help="Build dist/soulmap-ai.skill with .claude-plugin preserved",
    )

    args = parser.parse_args(argv)
    repo_root = REPO_ROOT

    if args.skill:
        build_skill(repo_root)
    else:
        build_zip(repo_root)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
