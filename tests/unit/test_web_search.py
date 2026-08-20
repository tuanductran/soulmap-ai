from __future__ import annotations

import json
import unicodedata

from soulmap.web.catalog import (
    _normalise_search_text,
    _search_tokens,
    catalog_search_json,
    search_catalog,
)


def test_normalise_search_text_folds_vietnamese_d_and_combining_marks() -> None:
    composed = "Đang buồn ở Việt Nam"
    decomposed = unicodedata.normalize("NFD", composed)

    assert _normalise_search_text(composed) == "dang buon o viet nam"
    assert _normalise_search_text(decomposed) == "dang buon o viet nam"
    assert _normalise_search_text("  ĐIỀU-PHỐI! ") == "dieu phoi"


def test_search_tokens_are_stable_for_accented_vietnamese_queries() -> None:
    assert _search_tokens("Tôi đang buồn") == ("toi", "dang", "buon")
    assert _search_tokens("đ/Đ") == ()


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
