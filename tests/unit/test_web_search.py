from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import cast

import pytest

from soulmap.web import catalog
from soulmap.web.catalog import (
    _normalise_search_text,
    _search_tokens,
    catalog_search_json,
    search_catalog,
)


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"entries": {}}, "Catalog entries must be a list"),
        ({"entries": [None]}, "Catalog entry must be an object"),
        (
            {
                "entries": [
                    {
                        "slug": "broken",
                        "directory": "broken",
                        "featured_file": "SKILL.md",
                        "locales": {"en": {}},
                    }
                ]
            },
            "Catalog locale parity failed",
        ),
        (
            {
                "entries": [
                    {
                        "slug": "broken",
                        "directory": "broken",
                        "featured_file": "SKILL.md",
                        "locales": {
                            locale: dict.fromkeys(("group", "title"), "value")
                            for locale in ("en", "vi", "ko")
                        },
                    }
                ]
            },
            "Catalog field parity failed",
        ),
        (
            {
                "entries": [
                    {
                        "slug": "broken",
                        "directory": "broken",
                        "featured_file": "SKILL.md",
                        "locales": {
                            locale: {
                                "group": "group",
                                "title": "title",
                                "summary": "summary",
                                "use_when": "use when",
                                "best_for": "best for",
                                "boundary": 1,
                            }
                            for locale in ("en", "vi", "ko")
                        },
                    }
                ]
            },
            "Catalog values must be strings",
        ),
    ],
)
def test_catalog_validation_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, object],
    message: str,
) -> None:
    monkeypatch.setattr(catalog, "_DATA", payload)

    with pytest.raises(ValueError, match=message):
        catalog._build_catalog()


def test_raw_copy_fails_closed_for_missing_locale_catalog(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(catalog, "_RAW_COPY", {"en": {"bundle_title": "title"}})

    with pytest.raises(ValueError, match="Invalid raw copy locale data"):
        catalog._raw_copy("vi")


def test_catalog_json_can_omit_raw_base_url() -> None:
    payload = json.loads(catalog.catalog_json(raw_base_url=""))

    assert payload["skills"]
    assert all(item["raw_url"] == "" for item in payload["skills"])


def test_raw_markdown_omits_prompt_section_when_skill_has_no_scenarios(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skill_dir = tmp_path / "skills" / catalog.CATALOG[0].directory
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Public skill\n", encoding="utf-8")
    monkeypatch.setattr(catalog, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(catalog, "scenarios_for", lambda _slug: ())

    body = catalog.raw_markdown(catalog.CATALOG[0])

    assert "# Public skill" in body
    assert "Suggested prompts by context" not in body


def test_raw_markdown_reports_missing_runtime_bundle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(catalog, "_repo_root", lambda: tmp_path)

    body = catalog.raw_markdown(catalog.CATALOG[0])

    assert "This raw bundle is not available" in body


def test_normalise_search_text_folds_vietnamese_d_and_combining_marks() -> None:
    composed = "Đang buồn ở Việt Nam"
    decomposed = unicodedata.normalize("NFD", composed)

    assert _normalise_search_text(composed) == "dang buon o viet nam"
    assert _normalise_search_text(decomposed) == "dang buon o viet nam"
    assert _normalise_search_text("  ĐIỀU-PHỐI! ") == "dieu phoi"


def test_search_tokens_are_stable_for_accented_vietnamese_queries() -> None:
    assert _search_tokens("Tôi đang buồn") == ("toi", "dang", "buon")
    assert _search_tokens("đ/Đ") == ()


def test_skill_entry_localized_properties_expose_catalog_fields() -> None:
    entry = catalog.CATALOG[0]

    assert entry.group
    assert entry.group_vi
    assert entry.title_en
    assert entry.title_vi
    assert entry.summary_en
    assert entry.summary_vi
    assert entry.use_when_en
    assert entry.use_when_vi
    assert entry.best_for_en
    assert entry.best_for_vi
    assert entry.boundary_en
    assert entry.boundary_vi


def test_exact_title_search_gets_relevance_priority_without_duplicate_fields() -> None:
    entry = catalog.CATALOG[0]

    results = search_catalog("en", entry.title_en)

    assert results[0]["slug"] == entry.slug
    assert cast(int, results[0]["score"]) >= 900
    assert cast(list[str], results[0]["matched_fields"]).count("title") == 1


def test_vietnamese_search_matches_accented_and_unaccented_queries() -> None:
    accented = search_catalog("vi", "khung")
    unaccented = search_catalog("vi", "dieu phoi")
    with_diacritics = search_catalog("vi", "đang buồn")
    without_diacritics = search_catalog("vi", "dang buon")

    assert accented
    assert accented[0]["slug"] == "frameworks"
    assert accented[0]["group"] == "Phản chiếu"
    assert unaccented
    assert unaccented[0]["slug"] == "meta"
    assert [item["slug"] for item in with_diacritics] == [
        item["slug"] for item in without_diacritics
    ]
    assert "frameworks" in [item["slug"] for item in with_diacritics]


def test_ask_mode_json_contains_localized_scenarios_for_every_skill() -> None:
    payload = json.loads(catalog_search_json("vi"))

    assert payload["locale"] == "vi"
    assert payload["total"] == 6
    assert all(result["prompt_scenarios"] for result in payload["results"])
    frameworks = next(
        result for result in payload["results"] if result["slug"] == "frameworks"
    )
    sadness = next(
        scenario
        for scenario in frameworks["prompt_scenarios"]
        if scenario["id"] == "frameworks-sadness"
    )

    assert sadness["title"] == "Buồn, mất mát hoặc đau buồn"
    assert sadness["question"].startswith("Tôi đang cảm thấy")
    assert sadness["prompt"]


def test_ask_mode_exposes_safety_and_boundary_scenarios_without_generating_answers() -> (
    None
):
    payload = json.loads(catalog_search_json("vi"))
    safety = next(result for result in payload["results"] if result["slug"] == "safety")
    scenario_ids = {scenario["id"] for scenario in safety["prompt_scenarios"]}

    assert {"safety-crisis", "safety-boundary", "safety-override"} <= scenario_ids
    assert all("answer" not in scenario for scenario in safety["prompt_scenarios"])
    assert all("diagnosis" not in scenario for scenario in safety["prompt_scenarios"])


def test_search_json_preserves_unicode_and_total_before_limit() -> None:
    payload = json.loads(catalog_search_json("vi", limit=1))
    serialized = catalog_search_json("vi", limit=1)

    assert payload["limit"] == 1
    assert payload["total"] == 6
    assert len(payload["results"]) == 1
    assert "Phản" in serialized
    assert "\\u" not in serialized
