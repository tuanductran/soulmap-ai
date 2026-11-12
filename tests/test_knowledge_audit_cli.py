from pathlib import Path

import pytest

from soulmap.devtools.audit import knowledge as knowledge_audit
from soulmap.runtime.knowledge.consistency import ConfigUsage


def _stub_audit_inputs(
    monkeypatch: pytest.MonkeyPatch, usage: tuple[ConfigUsage, ...]
) -> None:
    monkeypatch.setattr(knowledge_audit, "find_python_markdown_duplicates", lambda _: ())
    monkeypatch.setattr(knowledge_audit, "find_detector_markdown_duplicates", lambda _: ())
    monkeypatch.setattr(knowledge_audit, "find_config_usage", lambda _: usage)


def test_knowledge_audit_fails_on_unallowlisted_orphaned_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    config_path = tmp_path / "src/soulmap/runtime/config/meaning.py"
    usage = (ConfigUsage(config_path, "ORPHANED", ()),)
    _stub_audit_inputs(monkeypatch, usage)

    result = knowledge_audit.main(["--root", str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "orphaned config constant(s) are not allowlisted" in output
    assert "src/soulmap/runtime/config/meaning.py::ORPHANED" in output


def test_knowledge_audit_accepts_exact_orphan_allowlist_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = tmp_path / "src/soulmap/runtime/config/meaning.py"
    usage = (ConfigUsage(config_path, "ORPHANED", ()),)
    _stub_audit_inputs(monkeypatch, tmp_path, usage)

    result = knowledge_audit.main(
        [
            "--root",
            str(tmp_path),
            "--allow-orphaned-config",
            "src/soulmap/runtime/config/meaning.py::ORPHANED",
        ]
    )

    assert result == 0


def test_knowledge_audit_does_not_fail_for_active_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = tmp_path / "src/soulmap/runtime/config/meaning.py"
    consumer = tmp_path / "src/soulmap/runtime/detectors/example.py"
    usage = (ConfigUsage(config_path, "ACTIVE", (consumer,)),)
    _stub_audit_inputs(monkeypatch, tmp_path, usage)

    result = knowledge_audit.main(["--root", str(tmp_path)])

    assert result == 0
