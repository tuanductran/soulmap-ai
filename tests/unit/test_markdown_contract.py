from __future__ import annotations

from pathlib import Path

import pytest

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
    capsys: pytest.CaptureFixture[str],
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
    doctrine_source: str = "SOULMAP.md",
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

    assert "Integration doctrine_source must be SOULMAP.md" in messages
    assert (
        "Integration soulmap_version must match pyproject.toml version "
        "(expected 0.8.0, got 0.7.0)"
    ) in messages


def test_markdown_contract_flags_duplicate_phrase_within_one_group(
    tmp_path: Path,
) -> None:
    """A phrase repeated inside one labeled group is a content defect.

    The loaders deduplicate, so the repeat is invisible at runtime while it
    still ships in the extracted package. It also sets a trap: a maintainer
    editing one copy leaves the other stale.
    """
    doc = tmp_path / "anger-companion.md"
    doc.write_text(
        "---\nname: anger\ndescription: test\n---\n\n"
        "# Anger\n\n"
        "## Detection signals\n\n"
        "Active anger:\n\n"
        '- "i am so angry"\n'
        '- "i am furious"\n'
        '- "i am so angry"\n',
        encoding="utf-8",
    )

    issues = markdown_contract.check_markdown_file(doc, tmp_path)

    duplicates = [i for i in issues if "Duplicate detection phrase" in i.message]
    assert len(duplicates) == 1
    assert "i am so angry" in duplicates[0].message


def test_markdown_contract_allows_the_same_phrase_in_two_groups(
    tmp_path: Path,
) -> None:
    """Each labeled group owns its own phrase namespace.

    The knowledge loader keys results by label, so a phrase under two labels
    is two real entries, not a duplicate. Flagging it would push a maintainer
    into deleting one and silently changing what that group matches.
    """
    doc = tmp_path / "emotional-deescalation.md"
    doc.write_text(
        "---\nname: deescalation\ndescription: test\n---\n\n"
        "# De-escalation\n\n"
        "## Detection signals\n\n"
        "Flooding:\n\n"
        '- "head is spinning"\n\n'
        "Overwhelm:\n\n"
        '- "head is spinning"\n',
        encoding="utf-8",
    )

    issues = markdown_contract.check_markdown_file(doc, tmp_path)

    assert not [i for i in issues if "Duplicate detection phrase" in i.message]


# --- Agent Skills front-matter constraints ---
#
# The presence check above only asks whether `name` and `description` exist.
# These cover what a consumer of the skill actually depends on: a name it can
# resolve, a description short enough to load, and no key that looks right but
# is spelled wrong.


def _manifest(body: str) -> str:
    return f"---\n{body}\n---\n\n# Demo\n\nText\n"


def _check(tmp_path: Path, rel: str, body: str) -> list[str]:
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_manifest(body), encoding="utf-8")
    return _messages(markdown_contract.check_markdown_file(path, tmp_path))


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ('name: "wrong"\ndescription: "d"', "must match its directory"),
        ('name: "Demo"\ndescription: "d"', "lowercase letters, digits"),
        ('name: "de--mo"\ndescription: "d"', "lowercase letters, digits"),
        ('name: "-demo"\ndescription: "d"', "lowercase letters, digits"),
        ('name: "claude-demo"\ndescription: "d"', "reserved word"),
        (f'name: "{"a" * 65}"\ndescription: "d"', "exceeds 64"),
        (f'name: "demo"\ndescription: "{"x" * 1025}"', "over the 1024 limit"),
        ('name: "demo"\ndescription: "d"\nlicence: "x"', "Unknown front matter key"),
        ('name: "demo"\nno-colon-here\ndescription: "d"', "not `key: value`"),
    ],
    ids=[
        "name-directory-mismatch",
        "name-uppercase",
        "name-doubled-hyphen",
        "name-leading-hyphen",
        "name-reserved-word",
        "name-too-long",
        "description-too-long",
        "misspelled-key",
        "malformed-line",
    ],
)
def test_front_matter_violations_are_reported(
    tmp_path: Path, body: str, expected: str
) -> None:
    messages = _check(tmp_path, "skills/demo/SKILL.md", body)

    assert any(expected in message for message in messages), messages


def test_a_content_file_may_differ_from_its_directory_name(tmp_path: Path) -> None:
    """Only a SKILL.md manifest names its directory.

    `skills/meta/quick-reference.md` is content inside the meta skill, not a
    skill of its own, so its name legitimately differs from `meta`. Applying
    the directory rule to every file would fail most of the knowledge base.
    """
    messages = _check(
        tmp_path,
        "skills/meta/quick-reference.md",
        'name: "quick-reference"\ndescription: "d"',
    )

    assert not any("must match its directory" in message for message in messages)


def test_the_root_manifest_keeps_the_package_name(tmp_path: Path) -> None:
    """The root SKILL.md is exempt from the directory rule.

    Its name is the package name, and once the archive is extracted the root
    itself is the skill directory, so there is no parent to match.
    """
    messages = _check(tmp_path, "SKILL.md", 'name: "soulmap-ai"\ndescription: "d"')

    assert not any("must match its directory" in message for message in messages)


@pytest.mark.parametrize(
    ("body", "label"),
    [
        (f'name: "demo"\ndescription: "{"x" * 1024}"', "description exactly at limit"),
        ('name: "demo"\ndescription: "d"\n\n# comment', "blank line and comment"),
        (
            (
                'name: "demo"\ndescription: "d"\nversion: "0.10.0"\nlicense: "x"\n'
                'disable-model-invocation: true\ntime_scope: "2026"\n'
                'reviewed: "2026-09-02"'
            ),
            "every optional key the repo uses",
        ),
        (
            'name: "demo"\ndescription: "d"\nreviewed: "2026-09-02"',
            "the freshness re-check date on its own",
        ),
    ],
    ids=[
        "at-the-limit",
        "comment-and-blank",
        "all-optional-keys",
        "reviewed-alone",
    ],
)
def test_valid_front_matter_stays_clean(tmp_path: Path, body: str, label: str) -> None:
    """Boundaries and legal shapes must not be flagged.

    A rule that fires one character early, or on a comment, would make the
    contract untrustworthy for the files it already passes.
    """
    messages = _check(tmp_path, "skills/demo/SKILL.md", body)

    front_matter = [
        message
        for message in messages
        if "front matter" in message.lower() or "directory" in message
    ]
    assert not front_matter, f"{label}: {front_matter}"
