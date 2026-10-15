from __future__ import annotations

from pathlib import Path

import pytest

from scripts.audit_resource_inventory import audit, main


def test_inventory_keeps_unreferenced_resources_review_only(tmp_path: Path) -> None:
    (tmp_path / "skills/frameworks").mkdir(parents=True)
    (tmp_path / "skills/frameworks/example.md").write_text(
        "# Example\n", encoding="utf-8"
    )
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates/internal.md").write_text("# Internal\n", encoding="utf-8")
    (tmp_path / "SKILL.md").write_text("# Entry\n", encoding="utf-8")
    (tmp_path / "SOULMAP.md").write_text("# Doctrine\n", encoding="utf-8")

    findings = {item.path: item for item in audit(tmp_path)}

    assert (
        "shipped-package-contract" in findings["skills/frameworks/example.md"].evidence
    )
    assert "shipped-package-contract" in findings["SKILL.md"].evidence
    assert "local-maintainer-surface" in findings["templates/internal.md"].evidence
    assert (
        "review-only-no-static-edge" not in findings["templates/internal.md"].evidence
    )


def test_inventory_resolves_registry_edges_and_reports_missing_targets(
    tmp_path: Path,
) -> None:
    registry = tmp_path / "src/soulmap/runtime"
    registry.mkdir(parents=True)
    (registry / "source_registry.py").write_text(
        'REGISTRY = {"example": ("skills/frameworks/example.md", "Signals")}\n',
        encoding="utf-8",
    )
    (tmp_path / "skills/frameworks").mkdir(parents=True)
    (tmp_path / "skills/frameworks/example.md").write_text(
        "# Example\n", encoding="utf-8"
    )

    findings = {item.path: item for item in audit(tmp_path)}

    assert (
        "canonical-runtime-registry"
        in findings["skills/frameworks/example.md"].evidence
    )
    assert "missing-resource" not in findings

    (registry / "source_registry.py").write_text(
        'REGISTRY = {"missing": ("skills/frameworks/absent.md", "Signals")}\n',
        encoding="utf-8",
    )
    findings = audit(tmp_path)

    assert any(
        item.path == "skills/frameworks/absent.md"
        and item.category == "missing-resource"
        for item in findings
    )


def test_inventory_tracks_local_markdown_links(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills/knowledge.md").write_text("# Knowledge\n", encoding="utf-8")
    (tmp_path / "docs/guide.md").write_text(
        "[Knowledge](../skills/knowledge.md)\n", encoding="utf-8"
    )

    findings = {item.path: item for item in audit(tmp_path)}

    assert "local-markdown-link" in findings["skills/knowledge.md"].evidence


def test_repository_registry_targets_exist() -> None:
    root = Path(__file__).resolve().parents[2]

    findings = audit(root)

    assert any("canonical-runtime-registry" in item.evidence for item in findings)
    assert not any(item.category == "missing-resource" for item in findings)


def test_inventory_uses_paths_relative_to_repository_root(tmp_path: Path) -> None:
    root = tmp_path / "build" / "repo"
    registry = root / "src/soulmap/runtime"
    registry.mkdir(parents=True)
    (registry / "source_registry.py").write_text(
        'REGISTRY = {"example": ("skills/frameworks/example.md", "Signals")}\n',
        encoding="utf-8",
    )
    resource = root / "skills/frameworks/example.md"
    resource.parent.mkdir(parents=True)
    resource.write_text("# Example\n", encoding="utf-8")

    findings = {item.path: item for item in audit(root)}

    assert "skills/frameworks/example.md" in findings
    assert (
        "canonical-runtime-registry"
        in findings["skills/frameworks/example.md"].evidence
    )
    assert not any(item.category == "missing-resource" for item in findings.values())


def test_main_returns_incomplete_status_for_unreadable_source_and_missing_registry(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "unreadable.md").write_bytes(b"\xff\xfe\xfa")

    exit_code = main(["--root", str(tmp_path)])
    output = capsys.readouterr().out

    assert exit_code == 2
    assert "canonical runtime registry file is missing" in output
    assert "source file could not be read (UnicodeDecodeError)" in output
    assert "INCOMPLETE:" in output


def test_main_returns_error_for_missing_registry_target(tmp_path: Path) -> None:
    registry = tmp_path / "src/soulmap/runtime"
    registry.mkdir(parents=True)
    (registry / "source_registry.py").write_text(
        'REGISTRY = {"missing": ("skills/frameworks/absent.md", "Signals")}\n',
        encoding="utf-8",
    )

    assert main(["--root", str(tmp_path)]) == 1


def test_registry_invalid_entry_marks_inventory_incomplete(tmp_path: Path) -> None:
    registry = tmp_path / "src/soulmap/runtime"
    registry.mkdir(parents=True)
    (registry / "source_registry.py").write_text(
        'REGISTRY = {"valid": ("skills/valid.md", "Signals", "Contract", "Guidance"), '
        '"invalid": ("skills/invalid.md",)}\\n',
        encoding="utf-8",
    )
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills/valid.md").write_text("# Valid\\n", encoding="utf-8")

    findings = audit(tmp_path)

    assert any(
        item.category == "audit-limitation"
        and "runtime registry contains invalid entries" in " ".join(item.evidence)
        for item in findings
    )
    assert not any(item.category == "missing-resource" for item in findings)
    assert main(["--root", str(tmp_path)]) == 2
