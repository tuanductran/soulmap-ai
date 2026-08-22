import json
from typing import Any

import pytest

from soulmap.web import prompt_pack
from soulmap.web.prompt_pack import PromptScenario, scenarios_for


class _Resource:
    def __init__(self, payload: str) -> None:
        self.payload = payload

    def joinpath(self, _name: str) -> "_Resource":
        return self

    def read_text(self, *, encoding: str) -> str:
        assert encoding == "utf-8"
        return self.payload


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"version": 2, "packs": {}},
        {"packs": {}},
    ],
)
def test_load_prompt_data_rejects_invalid_root_or_version(
    monkeypatch: pytest.MonkeyPatch, payload: Any
) -> None:
    monkeypatch.setattr(
        prompt_pack,
        "files",
        lambda _package: _Resource(json.dumps(payload)),
    )

    with pytest.raises(ValueError, match="Invalid prompt data version"):
        prompt_pack._load_prompt_data()


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"packs": []}, "Prompt packs must be an object"),
        ({"packs": {"broken": []}}, "Invalid prompt pack: broken"),
        (
            {"packs": {"broken": {"scenarios": "not-a-list"}}},
            "Invalid prompt pack: broken",
        ),
        (
            {"packs": {"broken": {"scenarios": [None]}}},
            "Invalid prompt scenario: broken",
        ),
        (
            {
                "packs": {
                    "broken": {
                        "scenarios": [
                            {"id": "broken", "locales": []},
                        ]
                    }
                }
            },
            "Prompt locale parity failed: broken/broken",
        ),
        (
            {
                "packs": {
                    "broken": {
                        "scenarios": [
                            {"id": "broken", "locales": {"en": {}}},
                        ]
                    }
                }
            },
            "Prompt locale parity failed: broken/broken",
        ),
        (
            {
                "packs": {
                    "broken": {
                        "scenarios": [
                            {
                                "id": "broken",
                                "locales": {
                                    locale: [] for locale in ("en", "vi", "ko")
                                },
                            }
                        ]
                    }
                }
            },
            "Prompt field parity failed: broken/en",
        ),
        (
            {
                "packs": {
                    "broken": {
                        "scenarios": [
                            {
                                "id": "broken",
                                "locales": {
                                    locale: {"title": "only"}
                                    for locale in ("en", "vi", "ko")
                                },
                            }
                        ]
                    }
                }
            },
            "Prompt field parity failed: broken/en",
        ),
        (
            {
                "packs": {
                    "broken": {
                        "scenarios": [
                            {
                                "id": "broken",
                                "locales": {
                                    locale: {
                                        "title": "title",
                                        "when": "when",
                                        "prompt": "prompt",
                                        "question": 1,
                                    }
                                    for locale in ("en", "vi", "ko")
                                },
                            }
                        ]
                    }
                }
            },
            "Prompt values must be strings: broken/en",
        ),
    ],
)
def test_build_prompt_packs_rejects_invalid_shapes(
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, object],
    message: str,
) -> None:
    monkeypatch.setattr(prompt_pack, "_DATA", payload)

    with pytest.raises(ValueError, match=message):
        prompt_pack._build_prompt_packs()


def test_prompt_scenario_falls_back_per_field_and_for_unknown_locale() -> None:
    scenario = PromptScenario(
        "example",
        {
            "en": {
                "title": "English title",
                "when": "English when",
                "prompt": "English prompt",
                "question": "English question",
            },
            "vi": {"title": "Tiêu đề"},
            "ko": {},
        },
    )

    vietnamese = scenario.localized("vi")
    unknown = scenario.localized("fr")

    assert vietnamese == {
        "id": "example",
        "title": "Tiêu đề",
        "when": "English when",
        "prompt": "English prompt",
        "question": "English question",
    }
    assert unknown == {
        "id": "example",
        "title": "English title",
        "when": "English when",
        "prompt": "English prompt",
        "question": "English question",
    }
    assert scenario.title_en == "English title"
    assert scenario.title_vi == "Tiêu đề"
    assert scenario.when_en == "English when"
    assert scenario.when_vi == "English when"
    assert scenario.prompt_en == "English prompt"
    assert scenario.prompt_vi == "English prompt"
    assert scenario.question_en == "English question"
    assert scenario.question_vi == "English question"


def test_scenarios_for_unknown_slug_is_empty_and_known_slug_is_loaded() -> None:
    assert scenarios_for("not-a-real-skill") == ()
    assert scenarios_for("meta")
