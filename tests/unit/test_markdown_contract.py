from __future__ import annotations

from pathlib import Path

from soulmap.runtime.guards import markdown_contract


def _messages(issues: list[markdown_contract.Issue]) -> list[str]:
    return [issue.message for issue in issues]


def test_markdown_contract_flags_filename_metadata_unicode_and_headings(
    tmp_path: Path,
) -> None:
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    source = skills_dir / "bad_name.md"
    source.write_text(
        "##Bad heading\nText with a curly apostrophe: \u2019\n",
        encoding="utf-8",
    )

    messages = _messages(markdown_contract.check_markdown_file(source, tmp_path))

    assert "Markdown filename should not contain '_' (use '-')" in messages
    assert any("Missing YAML front matter metadata" in message for message in messages)
    assert (
        "Banned Unicode character: U+2019 RIGHT SINGLE QUOTATION MARK (use ASCII apostrophe ')"
        in messages
    )
    assert "ATX heading missing a space after '#'" in messages
    assert "Heading should be followed by a blank line" in messages


def test_markdown_contract_skips_invalid_markdown_inside_fenced_code(
    tmp_path: Path,
) -> None:
    source = tmp_path / "README.md"
    source.write_text(
        "# Valid\n\n```md\n##Bad heading\n<!-- unclosed\n![](image.png)\n"
        "[Unsafe](javascript:alert(1))\n1. First\n3. Third\n```\n\n## Also valid\n",
        encoding="utf-8",
    )

    assert markdown_contract.check_markdown_file(source, tmp_path) == []


def test_markdown_contract_flags_unbalanced_comment_and_missing_image_alt_text(
    tmp_path: Path,
) -> None:
    source = tmp_path / "README.md"
    source.write_text(
        "# Title\n\n<!-- missing close\n\n![](assets/logo.png)\n",
        encoding="utf-8",
    )

    messages = _messages(markdown_contract.check_markdown_file(source, tmp_path))

    assert "Unbalanced HTML comment markers (<!--: 1, -->: 0)" in messages
    assert "Image missing alt text: assets/logo.png" in messages


def test_markdown_contract_enforces_sequential_ordered_lists(tmp_path: Path) -> None:
    source = tmp_path / "README.md"
    source.write_text(
        "1. First\n3. Third\n\nParagraph breaks the list.\n\n2. New list\n",
        encoding="utf-8",
    )

    messages = _messages(markdown_contract.check_markdown_file(source, tmp_path))

    assert (
        "Ordered list numbering should stay sequential (expected 2., got 3.)"
        in messages
    )
    assert "Ordered lists must start at 1." in messages


def test_markdown_contract_allows_ordered_list_continuations(tmp_path: Path) -> None:
    source = tmp_path / "README.md"
    source.write_text(
        "1. First\n   Continuation text.\n2. Second\n",
        encoding="utf-8",
    )

    assert markdown_contract.check_markdown_file(source, tmp_path) == []


def test_markdown_contract_flags_unsafe_and_unresolvable_links(tmp_path: Path) -> None:
    target = tmp_path / "guide.md"
    target.write_text("# Guide\n\n## Details\n", encoding="utf-8")
    source = tmp_path / "README.md"
    source.write_text(
        "# Source\n\n[Broken file](missing.md)\n[Broken anchor](#missing)\n"
        "[Broken cross-file anchor](guide.md#missing)\n[Unsafe JavaScript](javascript:alert(1))\n"
        "[Unsafe data](data:text/plain,hello)\n[Escapes root](../outside.md)\n",
        encoding="utf-8",
    )

    messages = _messages(markdown_contract.check_markdown_file(source, tmp_path))

    assert "Broken relative link: missing.md" in messages
    assert "Broken anchor link: #missing" in messages
    assert "Broken cross-file anchor: guide.md#missing" in messages
    assert messages.count("Disallowed link scheme") == 2
    assert "Link escapes repo root" in messages


def test_markdown_contract_check_repo_and_cli_report_relative_path(
    tmp_path: Path,
    capsys,
) -> None:
    source = tmp_path / "bad.md"
    source.write_text("# Title\n\n```python\n", encoding="utf-8")

    issues = markdown_contract.check_repo(tmp_path)

    assert len(issues) == 1
    assert issues[0].message == "Unclosed fenced code block"
    assert markdown_contract.main(["--root", str(tmp_path)]) == 1
    assert "bad.md:3: Unclosed fenced code block" in capsys.readouterr().out


def _write_integration_guide(
    root: Path,
    *,
    doctrine_source: str = "AGENTS.md",
    soulmap_version: str = "0.8.0",
) -> Path:
    guide_dir = root / "docs" / "integrations"
    guide_dir.mkdir(parents=True)
    source = guide_dir / "chatgpt-instructions.md"
    source.write_text(
        "---\n"
        'title: "Integration guide"\n'
        'description: "A compatibility-tested platform guide."\n'
        f'doctrine_source: "{doctrine_source}"\n'
        f'soulmap_version: "{soulmap_version}"\n'
        "---\n\n"
        "# Integration guide\n",
        encoding="utf-8",
    )
    return source


def test_markdown_contract_accepts_matching_integration_metadata(
    tmp_path: Path,
) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nversion = "0.8.0"\n', encoding="utf-8"
    )
    source = _write_integration_guide(tmp_path)

    assert markdown_contract.check_markdown_file(source, tmp_path) == []


def test_markdown_contract_flags_missing_integration_metadata(tmp_path: Path) -> None:
    guide_dir = tmp_path / "docs" / "integrations"
    guide_dir.mkdir(parents=True)
    source = guide_dir / "poe-system-prompt.md"
    source.write_text(
        "---\n"
        'title: "Poe guide"\n'
        'description: "A platform guide."\n'
        "---\n\n"
        "# Poe guide\n",
        encoding="utf-8",
    )

    messages = _messages(markdown_contract.check_markdown_file(source, tmp_path))

    assert "Missing integration metadata: doctrine_source" in messages
    assert "Missing integration metadata: soulmap_version" in messages


def test_markdown_contract_flags_integration_doctrine_and_version_drift(
    tmp_path: Path,
) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nversion = "0.8.0"\n', encoding="utf-8"
    )
    source = _write_integration_guide(
        tmp_path,
        doctrine_source="docs/AGENTS-copy.md",
        soulmap_version="0.7.0",
    )

    messages = _messages(markdown_contract.check_markdown_file(source, tmp_path))

    assert "Integration doctrine_source must be AGENTS.md" in messages
    assert (
        "Integration soulmap_version must match pyproject.toml version "
        "(expected 0.8.0, got 0.7.0)"
    ) in messages
