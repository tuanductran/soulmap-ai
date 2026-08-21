"""Contracts for canonical English Skills and runtime locale evidence."""

from __future__ import annotations

import json
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


def test_vietnamese_spiritual_reference_has_stable_schema() -> None:
    path = REPO_ROOT / "reference/languages/vi/spiritual-bypass.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "1.0"
    assert payload["locale"] == "vi"
    assert payload["domain"] == "spiritual_bypass"
    assert set(payload["signals"]) == _REQUIRED_GROUPS
    assert all(
        isinstance(phrase, str)
        for phrases in payload["signals"].values()
        for phrase in phrases
    )


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
        "spiritual-bypass.json", domain="spiritual_bypass"
    )

    assert phrase in signals[group]


def test_locale_loader_preserves_vietnamese_integration_evidence() -> None:
    signals = load_locale_signal_groups(
        "spiritual-bypass.json", domain="spiritual_bypass"
    )

    assert "mình vẫn đang xử lý" in signals["genuine_integration"]


def _write_reference_file(
    root: Path, locale_directory: str, payload: object, filename: str = "signals.json"
) -> Path:
    path = root / locale_directory / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_locale_loader_merges_and_deduplicates_locale_files(tmp_path: Path) -> None:
    reference_root = tmp_path / "reference/languages"
    payload = {
        "schema_version": "1.0",
        "locale": "en",
        "domain": "test",
        "signals": {"group": ["Shared", "english"]},
    }
    _write_reference_file(reference_root, "en", payload)
    _write_reference_file(
        reference_root,
        "vi",
        {
            **payload,
            "locale": "vi",
            "signals": {"group": ["shared", "vietnamese"]},
        },
    )

    original = language_reference._find_repo_file
    language_reference._find_repo_file = lambda _: reference_root
    try:
        signals = load_locale_signal_groups("signals.json", domain="test")
    finally:
        language_reference._find_repo_file = original

    assert signals == {"group": ("shared", "english", "vietnamese")}


@pytest.mark.parametrize(
    ("payload", "error_fragment"),
    [
        ([], "must be an object"),
        ({"locale": "en", "domain": "test"}, "has no signals object"),
        ({"locale": "en", "domain": "wrong", "signals": {}}, "Expected domain"),
        ({"domain": "test", "signals": {}}, "has no locale"),
        ({"locale": "en", "domain": "test", "signals": []}, "no signals object"),
        (
            {"locale": "en", "domain": "test", "signals": {"group": "not-list"}},
            "Invalid signal group",
        ),
        (
            {"locale": "en", "domain": "test", "signals": {"group": [""]}},
            "Invalid phrase",
        ),
    ],
)
def test_locale_document_validation_rejects_invalid_schema(
    tmp_path: Path, payload: object, error_fragment: str
) -> None:
    path = _write_reference_file(tmp_path, "en", payload)

    with pytest.raises(ValueError, match=error_fragment):
        language_reference._load_document(path, expected_domain="test")


def test_locale_loader_rejects_directory_locale_mismatch(tmp_path: Path) -> None:
    reference_root = tmp_path / "reference/languages"
    path = _write_reference_file(
        reference_root,
        "vi",
        {
            "locale": "en",
            "domain": "test",
            "signals": {"group": ["phrase"]},
        },
    )
    original = language_reference._find_repo_file
    language_reference._find_repo_file = lambda _: reference_root
    try:
        with pytest.raises(ValueError, match="does not match directory"):
            load_locale_signal_groups("signals.json", domain="test")
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
        assert load_locale_signal_groups("signals.json", domain="test") == {}
    finally:
        language_reference._find_repo_file = original
