from pathlib import Path

from soulmap.devtools.checks.skills_boundary import audit


def test_audit_accepts_domain_markdown_without_implementation_details(
    tmp_path: Path,
) -> None:
    skills = tmp_path / "skills" / "example"
    skills.mkdir(parents=True)
    (skills / "SKILL.md").write_text(
        "---\nname: example\ndescription: Example\n---\n\n# Example\n\nReflective content.\n",
        encoding="utf-8",
    )

    assert audit(tmp_path) == []


def test_audit_rejects_implementation_commands_and_executable_code(
    tmp_path: Path,
) -> None:
    skills = tmp_path / "skills" / "example"
    skills.mkdir(parents=True)
    (skills / "SKILL.md").write_text(
        "---\nname: example\ndescription: Example\n---\n\n# Example\n\n"
        "Python is used in psychological research, but run uv run.\n\n"
        + chr(96) * 3
        + "python\nprint('x')\n"
        + chr(96) * 3
        + "\n",
        encoding="utf-8",
    )

    findings = audit(tmp_path)

    assert any("uv run" in finding for finding in findings)
    assert any("executable code fence" in finding for finding in findings)


def test_runtime_integration_folder_is_not_domain_scanned(tmp_path: Path) -> None:
    runtime = tmp_path / "skills" / "runtime"
    runtime.mkdir(parents=True)
    (runtime / "contract.md").write_text(
        "Python runtime integration may reference src/soulmap/.\n",
        encoding="utf-8",
    )

    assert audit(tmp_path) == []
