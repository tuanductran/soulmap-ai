"""Contract checks for local `.claude/` workflow docs and skills."""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
CLAUDE_DIR = ROOT / ".claude"

MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
CODE_SPAN_RE = re.compile(r"`([^`]+)`")


def _read_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    frontmatter: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return frontmatter
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    return {}


def _iter_claude_markdown_files() -> list[Path]:
    return sorted(CLAUDE_DIR.rglob("*.md"))


def _resolve_repo_path(raw: str, source: Path) -> Path | None:
    target = raw.strip()
    if not target or target.startswith("#"):
        return None
    if "://" in target or target.startswith(("mailto:", "tel:")):
        return None
    if target.startswith("/"):
        return None
    target = target.split("#", 1)[0]
    if not target:
        return None
    return (source.parent / target).resolve()


def _looks_like_repo_path(token: str) -> bool:
    token = token.strip()
    if not token or " " in token:
        return False
    if token.startswith(("http://", "https://", "mailto:", "tel:")):
        return False
    if token.endswith("/..."):
        return False
    if token in {"AGENTS.md", "README.md", "CHANGELOG.md"}:
        return True
    repo_prefixes = (
        ".claude/",
        ".claude-plugin/",
        "docs/",
        "skills/",
        "templates/",
        "modules/",
        "tests/",
        "tools/",
        "scripts/",
        "dist/",
        ".github/",
    )
    if token.startswith(repo_prefixes):
        return True
    return token.endswith((".md", ".py", ".json", ".sh", ".toml", ".zip"))


def test_claude_baseline_files_exist() -> None:
    expected_paths = [
        Path(".claude/rules/repo-workflow.md"),
        Path(".claude/rules/python-tooling.md"),
        Path(".claude/rules/markdown-portability.md"),
        Path(".claude/rules/source-character-safety.md"),
        Path(".claude/rules/git-and-release.md"),
        Path(".claude/skills/README.md"),
    ]
    for rel_path in expected_paths:
        assert (ROOT / rel_path).is_file(), f"Missing baseline file: {rel_path}"


def test_claude_rule_docs_have_frontmatter_and_heading() -> None:
    for path in sorted((CLAUDE_DIR / "rules").glob("*.md")):
        content = path.read_text(encoding="utf-8")
        assert content.startswith("---\n"), f"{path} must start with front matter"
        frontmatter = _read_frontmatter(path)
        assert "paths" in frontmatter, f"{path} front matter must include paths"
        assert "\n# " in content, f"{path} must include a top-level heading"


def test_claude_skill_docs_have_required_metadata_and_sections() -> None:
    skill_paths = sorted((CLAUDE_DIR / "skills").glob("*/SKILL.md"))
    assert skill_paths, "Expected local .claude skill files."

    for path in skill_paths:
        content = path.read_text(encoding="utf-8")
        frontmatter = _read_frontmatter(path)
        assert frontmatter.get("name") == path.parent.name
        assert frontmatter.get("description"), f"{path} must include description"
        assert "\n# " in content, f"{path} must include a title"
        assert "Use this skill" in content, f"{path} must explain when to use the skill"
        assert "Workflow" in content, f"{path} must include a workflow section"
        assert "## Definition Of Done" in content, (
            f"{path} must include a definition of done"
        )


def test_claude_markdown_links_and_repo_paths_resolve() -> None:
    for path in _iter_claude_markdown_files():
        content = path.read_text(encoding="utf-8")

        for _label, target in MD_LINK_RE.findall(content):
            resolved = _resolve_repo_path(target, path)
            if resolved is None:
                continue
            assert resolved.exists(), f"{path} has broken link target: {target}"

        for token in CODE_SPAN_RE.findall(content):
            if not _looks_like_repo_path(token):
                continue
            candidates = []
            resolved = _resolve_repo_path(token, path)
            if resolved is not None:
                candidates.append(resolved)
            candidates.append((ROOT / token).resolve())
            assert any(candidate.exists() for candidate in candidates), (
                f"{path} references missing repo path: {token}"
            )


def test_claude_skills_readme_matches_actual_skill_directories() -> None:
    readme = (CLAUDE_DIR / "skills" / "README.md").read_text(encoding="utf-8")
    actual = sorted(
        path.name
        for path in (CLAUDE_DIR / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    listed = sorted(re.findall(r"^- `([a-z0-9-]+)`$", readme, flags=re.MULTILINE))
    assert listed == actual, (
        ".claude/skills/README.md should list exactly the local skill directories"
    )


def test_readme_and_repo_workflow_reflect_actual_claude_structure() -> None:
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    workflow = (CLAUDE_DIR / "rules" / "repo-workflow.md").read_text(encoding="utf-8")

    assert "check root [`.claude/skills/`](.claude/skills/) for cross-repo skills" in (
        root_readme
    )
    assert "modules/.claude" not in root_readme
    assert "tests/.claude" not in root_readme
    assert "tools/.claude" not in root_readme
    assert "Check the root `.claude/skills/` directory for a matching skill first." in (
        workflow
    )
    assert "nearest `.claude/skills/` directory" not in workflow
