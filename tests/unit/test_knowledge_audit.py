from __future__ import annotations

from pathlib import Path

import pytest

from soulmap.devtools.audit import knowledge as audit
from soulmap.runtime.knowledge.consistency import ConfigUsage, KnowledgeDuplicate


def _duplicate(
    root: Path, classification: str = "knowledge_duplicate"
) -> KnowledgeDuplicate:
    return KnowledgeDuplicate(
        phrase="hold this gently",
        python_path=root / "src" / "config.py",
        constant="PHRASES",
        markdown_path=root / "skills" / "framework.md",
        markdown_section="Detection signals",
        markdown_group="reflective",
        source_kind="config",
        classification=classification,
    )


def test_format_inventory_groups_entries_and_reports_runtime_loader(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    duplicate = _duplicate(tmp_path)
    loader = tmp_path / "src" / "loader.py"

    monkeypatch.setattr(audit, "markdown_consumers", lambda _root, _path: (loader,))

    output = audit._format_inventory((duplicate,), tmp_path)
    normalized = output.replace("\\", "/")

    assert "Knowledge consistency inventory" in normalized
    assert "total overlaps: 1" in normalized
    assert "[knowledge_duplicate] 1" in normalized
    assert "src/config.py::PHRASES" in normalized
    assert "ownership: skills/framework.md" in normalized
    assert "loaded by: src/loader.py" in normalized
    assert "'hold this gently' -> skills/framework.md [Detection signals]" in normalized


def test_format_inventory_reports_missing_runtime_loader(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(audit, "markdown_consumers", lambda _root, _path: ())

    output = audit._format_inventory((_duplicate(tmp_path),), tmp_path)

    assert "loaded by: no runtime loader found" in output


def test_format_usage_separates_active_and_orphaned_constants(tmp_path: Path) -> None:
    active = ConfigUsage(
        python_path=tmp_path / "src" / "active.py",
        constant="ACTIVE",
        referenced_from=(tmp_path / "src" / "consumer.py",),
    )
    orphaned = ConfigUsage(
        python_path=tmp_path / "src" / "orphaned.py",
        constant="ORPHANED",
        referenced_from=(),
    )

    output = audit._format_usage((active, orphaned), tmp_path)
    normalized = output.replace("\\", "/")

    assert "active constants: 1" in normalized
    assert "orphaned constants: 1" in normalized
    assert "[active]" in normalized
    assert "src/active.py::ACTIVE" in normalized
    assert "- src/consumer.py" in normalized
    assert "[orphaned]" in normalized
    assert "src/orphaned.py::ORPHANED" in normalized


def test_audit_cli_honors_duplicate_threshold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    duplicate = _duplicate(tmp_path)
    active = ConfigUsage(
        python_path=tmp_path / "src" / "active.py",
        constant="ACTIVE",
        referenced_from=(tmp_path / "src" / "consumer.py",),
    )

    monkeypatch.setattr(
        audit, "find_python_markdown_duplicates", lambda _root: (duplicate,)
    )
    monkeypatch.setattr(audit, "find_config_usage", lambda _root: (active,))
    monkeypatch.setattr(audit, "markdown_consumers", lambda _root, _path: ())

    assert audit.main(["--root", str(tmp_path), "--max-knowledge-duplicates", "0"]) == 1
    assert "1 knowledge duplicates exceed 0" in capsys.readouterr().out


def test_audit_cli_passes_without_a_threshold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(audit, "find_python_markdown_duplicates", lambda _root: ())
    monkeypatch.setattr(audit, "find_config_usage", lambda _root: ())

    assert audit.main(["--root", str(tmp_path)]) == 0
