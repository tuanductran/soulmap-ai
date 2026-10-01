from pathlib import Path

from soulmap.devtools.audit.ownership import audit
from soulmap.devtools.packaging.members import source_members


def test_real_knowledge_ownership_has_no_errors() -> None:
    findings = audit(Path(__file__).resolve().parents[2])
    assert not [item for item in findings if item.kind != "shared-domain-source"], findings


def test_domain_router_missing_source_is_reported(tmp_path: Path) -> None:
    router = tmp_path / "skills/domains/example/SKILL.md"
    router.parent.mkdir(parents=True)
    router.write_text(
        "---\nname: example\n---\n\n"
        "## Canonical sources\n\n"
        "- [missing](../../frameworks/missing.md)\n",
        encoding="utf-8",
    )
    (tmp_path / "src/soulmap/runtime").mkdir(parents=True)
    (tmp_path / "skills/runtime").mkdir(parents=True)
    (tmp_path / "skills/runtime/source-registry.md").write_text(
        "# SoulMap runtime source registry\n\n"
        "| Source | Path | Signals | Runtime contract | Guidance |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n",
        encoding="utf-8",
    )
    findings = audit(tmp_path)
    assert any(item.kind == "missing-domain-source" for item in findings)


def test_source_members_exclude_runtime_and_honor_plugin_boundary(tmp_path: Path) -> None:
    for name in ("LICENSE", "SOULMAP.md", "SKILL.md"):
        (tmp_path / name).write_text("", encoding="utf-8")
    (tmp_path / "skills/frameworks").mkdir(parents=True)
    (tmp_path / "skills/frameworks/example.md").write_text("", encoding="utf-8")
    (tmp_path / "skills/runtime").mkdir(parents=True)
    (tmp_path / "skills/runtime/source-registry.md").write_text("", encoding="utf-8")
    (tmp_path / ".claude-plugin").mkdir(parents=True)
    (tmp_path / ".claude-plugin/marketplace.json").write_text("{}", encoding="utf-8")

    assert source_members(tmp_path, include_plugin=False) == {
        "LICENSE",
        "SOULMAP.md",
        "SKILL.md",
        "skills/frameworks/example.md",
    }
    assert source_members(tmp_path, include_plugin=True) == {
        "LICENSE",
        "SOULMAP.md",
        "SKILL.md",
        "skills/frameworks/example.md",
        ".claude-plugin/marketplace.json",
    }
