from pathlib import Path

import pytest

import soulmap.devtools.audit.ownership as ownership
from soulmap.devtools.packaging.members import source_members


def test_real_knowledge_ownership_has_no_errors() -> None:
    findings = ownership.audit(Path(__file__).resolve().parents[2])
    assert not findings



def test_source_members_exclude_runtime_contract_and_honor_plugin_boundary(
    tmp_path: Path,
) -> None:
    for name in ("LICENSE", "SOULMAP.md", "SKILL.md"):
        (tmp_path / name).write_text("", encoding="utf-8")
    (tmp_path / "skills/frameworks").mkdir(parents=True)
    (tmp_path / "skills/frameworks/example.md").write_text("", encoding="utf-8")
    (tmp_path / "src/soulmap/runtime").mkdir(parents=True)
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


def test_runtime_registry_orphan_and_direct_path_are_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime = tmp_path / "src/soulmap/runtime"
    runtime.mkdir(parents=True)
    monkeypatch.setattr(
        ownership,
        "_registry",
        lambda _root: {"orphan": ("skills/frameworks/example.md", "-", "-", "-")},
    )
    (tmp_path / "skills/frameworks").mkdir(parents=True)
    (tmp_path / "skills/frameworks/example.md").write_text(
        "# Example\n", encoding="utf-8"
    )
    (runtime / "example.py").write_text(
        "from soulmap.runtime.knowledge.keyword_lists import default_skill_path\n"
        "PATH = default_skill_path('skills/frameworks/example.md')\n",
        encoding="utf-8",
    )

    findings = ownership.audit(tmp_path)
    kinds = {item.kind for item in findings}
    assert "direct-source-path" in kinds
    assert "unconsumed-registry-source" in kinds


def test_runtime_audit_uses_supplied_root_registry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime = tmp_path / "src/soulmap/runtime"
    runtime.mkdir(parents=True)
    monkeypatch.setattr(
        ownership,
        "_registry",
        lambda _root: {"example": ("skills/frameworks/example.md", "-", "-", "-")},
    )
    (tmp_path / "skills/frameworks").mkdir(parents=True)
    (tmp_path / "skills/frameworks/example.md").write_text(
        "# Example\n", encoding="utf-8"
    )
    (runtime / "example.py").write_text(
        "from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path\n"
        "PATH = runtime_skill_path('example')\n",
        encoding="utf-8",
    )

    findings = ownership.audit(tmp_path)
    assert not findings
