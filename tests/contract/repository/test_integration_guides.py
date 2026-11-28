from __future__ import annotations

import json

from soulmap.devtools.packaging import build_skill
from soulmap.devtools.support.markdown import (
    is_external_markdown_target,
    iter_markdown_references,
    resolve_local_markdown_target,
    split_markdown_link_target,
)
from soulmap.devtools.support.repo import REPO_ROOT


def test_claude_plugin_manifest_declares_the_single_root_skill() -> None:
    manifest_path = REPO_ROOT / ".claude-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["name"] == "soulmap-ai"
    assert manifest["displayName"] == "SoulMap AI"
    assert manifest["skills"] == ["./"]
    assert manifest["version"] == json.loads(
        (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(
            encoding="utf-8"
        )
    )["version"]


def test_claude_integration_guide_documents_only_claude_workflows() -> None:
    guide = (REPO_ROOT / "docs" / "integrations" / "README.md").read_text(
        encoding="utf-8"
    )

    for anchor in (
        "Claude Code plugin",
        "Claude.ai Custom Skills",
        "claude plugin validate . --strict",
        "Claude API Skills",
        "plugin.json",
        "skills",
    ):
        assert anchor in guide

    for obsolete_platform in ("ChatGPT", "Gemini", "Poe"):
        assert f"## {obsolete_platform}" not in guide


def test_removed_non_claude_integration_guides_stay_removed() -> None:
    integration_root = REPO_ROOT / "docs" / "integrations"
    for filename in (
        "chatgpt-instructions.md",
        "gemini-instructions.md",
        "poe-system-prompt.md",
    ):
        assert not (integration_root / filename).exists()


def test_integration_readme_upload_references_ship_in_standard_archive() -> None:
    """Any package file linked from deployment guidance must be in the zip build."""
    guide = REPO_ROOT / "docs" / "integrations" / "README.md"
    shipped = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in build_skill._iter_inputs(REPO_ROOT)
        if not build_skill._is_ignored(
            path.relative_to(REPO_ROOT).as_posix(),
            build_skill._load_distignore(REPO_ROOT),
        )
    }
    package_references: set[str] = set()

    for reference in iter_markdown_references(
        guide.read_text(encoding="utf-8").splitlines()
    ):
        target_path, _fragment = split_markdown_link_target(reference.target)
        if not target_path or is_external_markdown_target(target_path):
            continue
        target = resolve_local_markdown_target(
            repo_root=REPO_ROOT,
            current_file=guide,
            target_path=target_path,
        )
        relative = target.relative_to(REPO_ROOT).as_posix()
        if relative in {"SOULMAP.md", "SKILL.md"} or relative.startswith("skills/"):
            package_references.add(relative)

    assert package_references
    assert package_references <= shipped
