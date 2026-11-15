from soulmap.devtools.checks.skills_boundary import audit_markdown


def test_implementation_language_is_forbidden_in_plain_prose() -> None:
    text = """
Python is sometimes used in psychological research.
A class can describe a social category without referring to executable code.
"""
    findings = audit_markdown("skills/example.md", text)

    assert any("implementation reference" in finding for finding in findings)
    assert all("class" not in finding for finding in findings)


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
