"""Build distribution artifacts for SoulMap AI.

Flags
-----
--zip     Build dist/soulmap-ai.zip   (default when no flag given)
--skill   Build dist/soulmap-ai.skill (Agent Skills-compliant archive)
--all     Build both

Examples
--------
python -m tools.build_skill_zip              # same as --zip
python -m tools.build_skill_zip --zip        # zip only
python -m tools.build_skill_zip --skill      # .skill only
python -m tools.build_skill_zip --all        # both

Formats
-------
soulmap-ai.zip
    Standard zip — skills/, templates/, LICENSE, marketplace.json.
    Use for Claude plugin marketplace or manual extraction.

soulmap-ai.skill
    Agent Skills-compliant archive (zip with .skill extension).
    Compatible with Claude.ai (Settings > Features > Upload Skill),
    GitHub Copilot, OpenAI Codex, and any Agent Skills-compatible tool.
    Includes a root-level SKILL.md entry-point manifest so AI tools
    can discover and activate the skill by name/description.
"""

from __future__ import annotations

import argparse
import fnmatch
from pathlib import Path
import textwrap
import zipfile

from tools._repo import REPO_ROOT

# ---------------------------------------------------------------------------
# Root SKILL.md manifest injected into the .skill archive
# ---------------------------------------------------------------------------

_ROOT_SKILL_MD = textwrap.dedent("""\
    ---
    name: soulmap-ai
    description: >
      SoulMap AI - a reflective companion that helps people stop abandoning
      themselves. Includes frameworks, safety guardrails, voice system, brand
      doctrine, and reusable templates. Mirror, not guide.
    ---

    # SoulMap AI

    SoulMap AI is a reflective inner companion whose only purpose is to help
    people hear themselves more clearly.

    **The single most important principle:** Every response must leave the user
    more honest with themselves, more grounded in their own inner authority,
    and *less* dependent on SoulMap AI than before the response.

    ## How to use this skill

    This skill bundles the full SoulMap AI knowledge base. Load the relevant
    group file based on the current task:

    | When you need...                              | Load from...                |
    | :-------------------------------------------- | :-------------------------- |
    | Behavioral contract and safety rules          | `AGENTS.md`                 |
    | Response frameworks (grief, crisis, etc.)     | `skills/frameworks/`        |
    | Safety boundaries and scope control           | `skills/safety/`            |
    | Brand, positioning, and public copy           | `skills/brand/`             |
    | Voice, tone, and response calibration         | `skills/voice/`             |
    | Deep inquiry questions and journey stages     | `skills/meta/`              |
    | Spiritual layer and symbolic frameworks       | `skills/spiritual/`         |
    | Response templates and quick reference        | `templates/`                |

    See `AGENTS.md` for the full behavioral contract and non-negotiable safety
    rules that govern every response.
""")


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
    """Return all files that belong in either the zip or .skill archive."""
    paths: list[Path] = []
    for name in ["LICENSE", "AGENTS.md"]:
        candidate = repo_root / name
        if candidate.is_file():
            paths.append(candidate)

    claude_plugin = repo_root / ".claude-plugin" / "marketplace.json"
    if claude_plugin.is_file():
        paths.append(claude_plugin)

    for folder in ["skills", "templates"]:
        base = repo_root / folder
        for path in base.rglob("*"):
            if path.is_file():
                paths.append(path)

    return sorted(set(paths))


# ---------------------------------------------------------------------------
# Output 1: ZIP
# ---------------------------------------------------------------------------


def build_zip(repo_root: Path) -> Path:
    """Build dist/soulmap-ai.zip."""
    out_dir = repo_root / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_zip = out_dir / "soulmap-ai.zip"

    patterns = _load_distignore(repo_root)
    inputs = _iter_inputs(repo_root)

    if out_zip.exists():
        out_zip.unlink()

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in inputs:
            rel = path.relative_to(repo_root).as_posix()
            if _is_ignored(rel, patterns):
                continue
            archive.write(path, arcname=rel)

    size_kb = out_zip.stat().st_size // 1024
    print(f"OK (zip):   {out_zip}  (~{size_kb}KB)")
    return out_zip


# ---------------------------------------------------------------------------
# Output 2: .skill
# ---------------------------------------------------------------------------


def build_skill(repo_root: Path) -> Path:
    """Build dist/soulmap-ai.skill (Agent Skills-compliant zip archive).

    The .skill file is a zip archive with the .skill extension, recognised by
    Claude.ai, GitHub Copilot, OpenAI Codex, and other Agent Skills-compatible
    tools.  It includes a root-level SKILL.md entry-point manifest so AI tools
    can discover and activate the skill by name/description.
    """
    out_dir = repo_root / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_skill = out_dir / "soulmap-ai.skill"

    patterns = _load_distignore(repo_root)
    inputs = _iter_inputs(repo_root)

    if out_skill.exists():
        out_skill.unlink()

    with zipfile.ZipFile(out_skill, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        # Inject root-level SKILL.md manifest (required by Agent Skills spec)
        archive.writestr("SKILL.md", _ROOT_SKILL_MD)

        # Add all knowledge files
        for path in inputs:
            rel = path.relative_to(repo_root).as_posix()
            if _is_ignored(rel, patterns):
                continue
            archive.write(path, arcname=rel)

    size_kb = out_skill.stat().st_size // 1024
    print(f"OK (skill): {out_skill}  (~{size_kb}KB)")
    return out_skill


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.build_skill_zip",
        description="Build SoulMap AI distribution artifacts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              python -m tools.build_skill_zip           build zip (default)
              python -m tools.build_skill_zip --zip     build zip only
              python -m tools.build_skill_zip --skill   build .skill only
              python -m tools.build_skill_zip --all     build zip + .skill
        """),
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--zip",
        action="store_true",
        help="Build dist/soulmap-ai.zip (default when no flag given)",
    )
    group.add_argument(
        "--skill",
        action="store_true",
        help="Build dist/soulmap-ai.skill (Agent Skills-compliant archive)",
    )
    group.add_argument(
        "--all",
        dest="build_all",
        action="store_true",
        help="Build both zip and .skill",
    )

    args = parser.parse_args(argv)
    repo_root = REPO_ROOT

    # Default: --zip when no flag provided (backward compatible)
    do_zip = args.zip or args.build_all or (not args.skill and not args.build_all)
    do_skill = args.skill or args.build_all

    if do_zip:
        build_zip(repo_root)
    if do_skill:
        build_skill(repo_root)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
