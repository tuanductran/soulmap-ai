from __future__ import annotations

import json
from importlib.resources import files
from typing import cast

import pytest

from soulmap.web import prompt_pack
from soulmap.web.catalog import CATALOG, raw_markdown
from soulmap.web.i18n import SUPPORTED_LOCALES
from soulmap.web.prompt_pack import PROMPT_PACKS


@pytest.fixture(scope="module")
def catalog_data() -> dict[str, object]:
    return json.loads(
        files("soulmap.web").joinpath("catalog_data.json").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="module")
def prompt_data() -> dict[str, object]:
    return json.loads(
        files("soulmap.web").joinpath("prompt_data.json").read_text(encoding="utf-8")
    )


def test_catalog_json_has_exact_entry_and_locale_parity(
    catalog_data: dict[str, object],
) -> None:
    entries = catalog_data["entries"]
    assert isinstance(entries, list)
    assert [entry["slug"] for entry in entries] == [entry.slug for entry in CATALOG]
    assert all(set(entry["locales"]) == set(SUPPORTED_LOCALES) for entry in entries)
    assert all(
        all(
            set(entry["locales"][locale])
            == {"group", "title", "summary", "use_when", "best_for", "boundary"}
            for locale in SUPPORTED_LOCALES
        )
        for entry in entries
    )


def test_prompt_json_has_exact_pack_scenario_and_locale_parity(
    prompt_data: dict[str, object],
) -> None:
    packs = cast(dict[str, dict[str, object]], prompt_data["packs"])
    assert set(packs) == set(PROMPT_PACKS)
    for slug, pack in packs.items():
        scenarios = cast(list[dict[str, object]], pack["scenarios"])
        scenario_ids = [scenario["id"] for scenario in scenarios]
        assert scenario_ids == [scenario.scenario_id for scenario in PROMPT_PACKS[slug]]
        for scenario in scenarios:
            locales = cast(dict[str, dict[str, str]], scenario["locales"])
            assert set(locales) == set(SUPPORTED_LOCALES)
            assert all(
                set(locales[locale]) == {"title", "when", "prompt", "question"}
                for locale in SUPPORTED_LOCALES
            )


@pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
def test_catalog_and_prompt_runtime_expose_localized_korean_safe_values(
    locale: str,
) -> None:
    assert all(entry.locales[locale]["title"] for entry in CATALOG)
    assert all(
        scenario.localized(locale)["question"]
        for pack in PROMPT_PACKS.values()
        for scenario in pack
    )


def test_prompt_scenario_properties_and_unknown_locale_fallback() -> None:
    scenario = next(iter(next(iter(PROMPT_PACKS.values()))))

    assert scenario.localized("fr") == scenario.localized("en")
    assert scenario.title_en
    assert scenario.title_vi
    assert scenario.when_en
    assert scenario.when_vi
    assert scenario.prompt_en
    assert scenario.prompt_vi
    assert scenario.question_en
    assert scenario.question_vi


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"packs": []}, "Prompt packs must be an object"),
        (
            {"packs": {"broken": {"scenarios": "not-a-list"}}},
            "Invalid prompt pack",
        ),
        (
            {"packs": {"broken": {"scenarios": [None]}}},
            "Invalid prompt scenario",
        ),
        (
            {
                "packs": {
                    "broken": {
                        "scenarios": [
                            {
                                "id": "scenario",
                                "locales": {
                                    "en": {
                                        "title": "title",
                                        "when": "when",
                                        "prompt": "prompt",
                                        "question": "question",
                                    }
                                },
                            }
                        ]
                    }
                }
            },
            "Prompt locale parity failed",
        ),
        (
            {
                "packs": {
                    "broken": {
                        "scenarios": [
                            {
                                "id": "scenario",
                                "locales": {
                                    locale: {
                                        "title": "title",
                                        "when": "when",
                                        "prompt": "prompt",
                                    }
                                    for locale in SUPPORTED_LOCALES
                                },
                            }
                        ]
                    }
                }
            },
            "Prompt field parity failed",
        ),
        (
            {
                "packs": {
                    "broken": {
                        "scenarios": [
                            {
                                "id": "scenario",
                                "locales": {
                                    locale: {
                                        "title": "title",
                                        "when": "when",
                                        "prompt": "prompt",
                                        "question": 1,
                                    }
                                    for locale in SUPPORTED_LOCALES
                                },
                            }
                        ]
                    }
                }
            },
            "Prompt values must be strings",
        ),
    ],
)
def test_prompt_pack_validation_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, object],
    message: str,
) -> None:
    monkeypatch.setattr(prompt_pack, "_DATA", payload)

    with pytest.raises(ValueError, match=message):
        prompt_pack._build_prompt_packs()


def test_raw_markdown_uses_localized_catalog_and_prompt_labels() -> None:
    korean = raw_markdown(CATALOG[0], "ko")
    vietnamese = raw_markdown(CATALOG[0], "vi")

    assert "SoulMap Skill 번들" in korean
    assert "상황별 추천 프롬프트" in korean
    assert "Gói Skill SoulMap" in vietnamese
    assert "Prompt gợi ý theo bối cảnh" in vietnamese
