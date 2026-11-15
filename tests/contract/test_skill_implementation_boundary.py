from pathlib import Path

from soulmap.devtools.checks.skills_boundary import audit


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_audit_accepts_implementation_neutral_shipped_markdown(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "SKILL.md", "# SoulMap\\n\\nReflective content.\\n")
    _write(tmp_path / "SOULMAP.md", "# Doctrine\\n\\nStay grounded.\\n")
    _write(tmp_path / "skills/example/guide.md", "# Guide\\n\\nReflective content.\\n")

    assert audit(tmp_path) == []


def test_audit_checks_root_entrypoints_and_nested_skill_markdown(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "SKILL.md", "# Skill\\n\\nPython should not appear here.\\n")
    _write(tmp_path / "SOULMAP.md", "# Doctrine\\n\\nStay grounded.\\n")
    _write(tmp_path / "skills/example/guide.md", "# Guide\\n\\nReflective content.\\n")

    findings = audit(tmp_path)

    assert any("SKILL.md" in finding and "Python" in finding for finding in findings)


def test_audit_rejects_programming_language_names_in_shipped_content(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "SKILL.md", "# Skill\\n\\nJavaScript and TypeScript are not product guidance.\\n")
    _write(tmp_path / "SOULMAP.md", "# Doctrine\\n\\nStay grounded.\\n")
    _write(tmp_path / "skills/example/guide.md", "# Guide\\n\\nReflective content.\\n")

    findings = audit(tmp_path)

    assert any("JavaScript" in finding for finding in findings)
    assert any("TypeScript" in finding for finding in findings)


def test_audit_rejects_implementation_commands_and_executable_code(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "skills/example/SKILL.md", "# Example\\n\\nUse uv run for this task.\\n")
    _write(tmp_path / "skills/example/extra.md", "```bash\\necho unsafe\\n```\\n")

    findings = audit(tmp_path)

    assert any("uv run" in finding for finding in findings)
    assert any("executable code fence" in finding for finding in findings)
