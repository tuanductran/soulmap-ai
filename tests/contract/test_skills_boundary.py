from soulmap.devtools.checks.skills_boundary import audit_markdown, audit_text


def test_implementation_language_in_plain_prose_is_rejected() -> None:
    text = """
Python is sometimes used in psychological research.
A class can describe a social category without referring to executable code.
"""
    findings = audit_markdown("skills/example.md", text)
    assert any("implementation language reference" in finding for finding in findings)


def test_generic_words_are_not_treated_as_implementation_leakage() -> None:
    text = (
        "A class can describe a social category without referring to executable code."
    )
    assert audit_markdown("skills/example.md", text) == []


def test_executable_markdown_constructs_are_rejected() -> None:
    text = """
```python
print("hello")
```

Use `src/soulmap/runtime/detectors/foo.py` only as a test fixture.
"""
    findings = audit_markdown("skills/example.md", text)

    assert any("executable code fence" in finding for finding in findings)
    assert any("inline code" in finding for finding in findings)


def test_repository_paths_in_prose_remain_forbidden() -> None:
    text = "The implementation lives in src/soulmap/runtime/."
    findings = audit_markdown("skills/example.md", text)

    assert any("src/soulmap/" in finding for finding in findings)


def test_non_markdown_shipped_metadata_rejects_implementation_languages() -> None:
    text = '{"description": "Python runtime and JavaScript integration"}'
    findings = audit_text(".claude-plugin/marketplace.json", text)

    assert any("Python" in finding for finding in findings)
    assert any("JavaScript" in finding for finding in findings)

def test_audit_covers_all_build_members_and_respects_distignore(tmp_path) -> None:
    from pathlib import Path

    from soulmap.devtools.checks.skills_boundary import audit

    files = {
        "SKILL.md": "# Skill\\n\\nPython must not leak into shipped guidance.\\n",
        "SOULMAP.md": "# Doctrine\\n\\nJavaScript is an implementation detail.\\n",
        "LICENSE": "Rust implementation details are not part of this package.\\n",
        "skills/example/guide.md": "# Guide\\n\\nTypeScript must not appear here.\\n",
        ".claude-plugin/marketplace.json": (
            '{"description": "Ruby implementation details are forbidden"}'
        ),
        "skills/private/internal.md": "# Private\\n\\nPython\\n",
        "docs/internal.md": "# Internal\\n\\nPython\\n",
    }
    for relative, content in files.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    (tmp_path / ".distignore").write_text(
        "skills/private/internal.md\\n", encoding="utf-8"
    )

    findings = audit(Path(tmp_path))
    found_paths = {finding.split(":", maxsplit=1)[0] for finding in findings}

    assert {
        "SKILL.md",
        "SOULMAP.md",
        "LICENSE",
        "skills/example/guide.md",
        ".claude-plugin/marketplace.json",
    } <= found_paths
    assert "skills/private/internal.md" not in found_paths
    assert "docs/internal.md" not in found_paths
\n