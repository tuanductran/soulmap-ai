from pathlib import Path

from soulmap.devtools.checks.skills_boundary import audit


def test_audit_accepts_domain_markdown_without_implementation_details(
    tmp_path: Path,
) -> None:
    skills = tmp_path / "skills" / "example"
    skills.mkdir(parents=True)
    (skills / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: example",
                "description: Example",
                "---",
                "",
                "# Example",
                "",
                "Reflective content.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    assert audit(tmp_path) == []


def test_audit_rejects_implementation_language_commands_and_executable_code(
    tmp_path: Path,
) -> None:
    skills = tmp_path / "skills" / "example"
    skills.mkdir(parents=True)
    (skills / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: example",
                "description: Example",
                "---",
                "",
                "# Example",
                "",
                "Python is used in psychological research, but run uv run.",
                "",
                "\x60\x60\x60python",
                "print('x')",
                "\x60\x60\x60",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    findings = audit(tmp_path)

    assert any("implementation reference" in finding for finding in findings)
    assert any("uv run" in finding for finding in findings)
    assert any("executable code fence" in finding for finding in findings)


def test_audit_includes_root_shipped_entrypoints(tmp_path: Path) -> None:
    (tmp_path / "SKILL.md").write_text(
        "# Entry point\n\nPython is an implementation detail.\n",
        encoding="utf-8",
    )
    (tmp_path / "SOULMAP.md").write_text(
        "# Doctrine\n\nKeep the user-facing contract clear.\n",
        encoding="utf-8",
    )

    findings = audit(tmp_path)

    assert any(finding.startswith("SKILL.md:") for finding in findings)
