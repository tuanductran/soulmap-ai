"""Contracts for canonical English Skills and runtime locale evidence."""

from __future__ import annotations

import json
import re

from soulmap.devtools.support.repo import REPO_ROOT
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


def test_locale_loader_preserves_vietnamese_detection_evidence() -> None:
    signals = load_locale_signal_groups(
        "spiritual-bypass.json", domain="spiritual_bypass"
    )

    assert "mình là empath nên" in signals["bypass_spiritual_inflation"]
    assert "mình vẫn đang xử lý" in signals["genuine_integration"]
