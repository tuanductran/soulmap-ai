"""Contracts for canonical English Skills and packaged Markdown locale references."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.knowledge import language_reference
from soulmap.runtime.knowledge.language_reference import load_locale_signal_groups

_VIETNAMESE_OR_HANGUL = re.compile(r"[À-ỹĐđ가-힣]")
_REQUIRED_GROUPS = {
    "bypass_dismissing_pain",
    "bypass_premature_acceptance",
    "bypass_spiritual_inflation",
    "bypass_accountability",
    "genuine_integration",
}


def test_shipped_skills_do_not_contain_locale_prose() -> None:
    offenders = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / "skills").rglob("*.md")
        if _VIETNAMESE_OR_HANGUL.search(path.read_text(encoding="utf-8"))
    }

    assert offenders == set()


def test_language_reference_tree_is_markdown_only() -> None:
    reference_files = [
        path
        for path in (REPO_ROOT / "reference/languages").rglob("*")
        if path.is_file() and path.name != "README.md"
    ]

    assert reference_files
    assert all(path.suffix == ".md" for path in reference_files)


def test_vietnamese_spiritual_reference_has_stable_markdown_schema() -> None:
    path = REPO_ROOT / "reference/languages/vi/spiritual-bypass.md"
    text = path.read_text(encoding="utf-8")
    metadata = language_reference._parse_front_matter(text, path)
    signals = load_locale_signal_groups(
        "spiritual-bypass.md", domain="spiritual_bypass"
    )

    assert metadata == {
        "schema_version": "1.0",
        "locale": "vi",
        "language": "Vietnamese",
        "domain": "spiritual_bypass",
        "source_policy": "human-authored-runtime-reference",
    }
    assert set(signals) == _REQUIRED_GROUPS
    assert all(phrases for phrases in signals.values())


@pytest.mark.parametrize(
    ("phrase", "group"),
    [
        ("mình là empath nên", "bypass_spiritual_inflation"),
        ("todo pasa por algo", "bypass_dismissing_pain"),
        ("je leur ai déjà pardonné", "bypass_premature_acceptance"),
        ("一切发生都有原因", "bypass_dismissing_pain"),
        ("모든 일에는 이유가 있어", "bypass_dismissing_pain"),
    ],
)
def test_locale_loader_preserves_supported_detection_evidence(
    phrase: str, group: str
) -> None:
    signals = load_locale_signal_groups(
        "spiritual-bypass.md", domain="spiritual_bypass"
    )

    assert phrase in signals[group]


def test_locale_loader_preserves_vietnamese_integration_evidence() -> None:
    signals = load_locale_signal_groups(
        "spiritual-bypass.md", domain="spiritual_bypass"
    )

    assert "mình vẫn đang xử lý" in signals["genuine_integration"]


def _write_reference_file(
    root: Path,
    locale_directory: str,
    text: str,
    filename: str = "signals.md",
) -> Path:
    path = root / locale_directory / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _valid_reference(locale: str, phrases: list[str]) -> str:
    lines = [
        "---",
        'schema_version: "1.0"',
        f'locale: "{locale}"',
        'language: "Test language"',
        'domain: "test"',
        'source_policy: "test"',
        "---",
        "",
        "# Test reference",
        "",
        "## Bypass: Dismissing Pain",
        "",
        *[f'- "{phrase}"' for phrase in phrases],
        "",
    ]
    return "\n".join(lines)


def test_locale_loader_merges_and_deduplicates_markdown_files(tmp_path: Path) -> None:
    reference_root = tmp_path / "reference/languages"
    _write_reference_file(
        reference_root, "en", _valid_reference("en", ["Shared", "english"])
    )
    _write_reference_file(
        reference_root,
        "vi",
        _valid_reference("vi", ["shared", "vietnamese"]),
    )

    original = language_reference._find_repo_file
    language_reference._find_repo_file = lambda _: reference_root
    try:
        signals = load_locale_signal_groups("signals.md", domain="test")
    finally:
        language_reference._find_repo_file = original

    assert signals == {"bypass_dismissing_pain": ("shared", "english", "vietnamese")}


@pytest.mark.parametrize(
    ("text", "error_fragment"),
    [
        ("# no front matter\n", "has no front matter"),
        (
            '---\nschema_version: "1.0"\ndomain: "test"\n---\n',
            "has no locale",
        ),
        (
            '---\nschema_version: "2.0"\nlocale: "en"\ndomain: "test"\n---\n',
            "unsupported schema",
        ),
        (
            '---\nschema_version: "1.0"\nlocale: "en"\ndomain: "wrong"\n---\n',
            "Expected domain",
        ),
        (
            '---\nschema_version: "1.0"\nlocale: "en"\ndomain: "test"\n---\n## Other\n',
            "no signal sections",
        ),
        (
            '---\nschema_version: "1.0"\nlocale: "en"\ndomain: "test"\n',
            "unclosed front matter",
        ),
        (
            "---\ninvalid-line\n---\n",
            "Invalid front matter",
        ),
    ],
)
def test_markdown_locale_document_validation_rejects_invalid_schema(
    tmp_path: Path, text: str, error_fragment: str
) -> None:
    path = _write_reference_file(tmp_path, "en", text)

    with pytest.raises(ValueError, match=error_fragment):
        language_reference._load_document(path, expected_domain="test")


def test_locale_loader_rejects_directory_locale_mismatch(tmp_path: Path) -> None:
    reference_root = tmp_path / "reference/languages"
    path = _write_reference_file(
        reference_root,
        "vi",
        _valid_reference("en", ["phrase"]),
    )
    original = language_reference._find_repo_file
    language_reference._find_repo_file = lambda _: reference_root
    try:
        with pytest.raises(ValueError, match="does not match directory"):
            load_locale_signal_groups("signals.md", domain="test")
    finally:
        language_reference._find_repo_file = original

    assert path.is_file()


def test_find_repo_file_uses_existing_environment_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reference_root = tmp_path / "reference/languages"
    reference_root.mkdir(parents=True)
    monkeypatch.setenv("SOULMAP_REPO_ROOT", str(tmp_path))

    assert language_reference._find_repo_file("reference/languages") == reference_root


def test_find_repo_file_raises_for_missing_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SOULMAP_REPO_ROOT", raising=False)

    with pytest.raises(FileNotFoundError, match="Could not locate"):
        language_reference._find_repo_file("reference/path-that-does-not-exist")


def test_locale_loader_returns_empty_mapping_when_no_locale_files(
    tmp_path: Path,
) -> None:
    reference_root = tmp_path / "reference/languages"
    reference_root.mkdir(parents=True)
    original = language_reference._find_repo_file
    language_reference._find_repo_file = lambda _: reference_root
    try:
        assert load_locale_signal_groups("signals.md", domain="test") == {}
    finally:
        language_reference._find_repo_file = original
