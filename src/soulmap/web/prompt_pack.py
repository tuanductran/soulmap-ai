"""JSON-backed public prompt scenarios for Skill provider handoffs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files

from soulmap.web.i18n import SUPPORTED_LOCALES

_PROMPT_FIELDS = ("title", "when", "prompt", "question")


def _load_prompt_data() -> dict[str, object]:
    payload = json.loads(
        files("soulmap.web").joinpath("prompt_data.json").read_text(encoding="utf-8")
    )
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("Invalid prompt data version")
    return payload


_DATA = _load_prompt_data()


@dataclass(frozen=True)
class PromptScenario:
    """One public prompt scenario for a Skill group."""

    scenario_id: str
    locales: dict[str, dict[str, str]]

    def localized(self, locale: str) -> dict[str, str]:
        language = locale if locale in SUPPORTED_LOCALES else "en"
        english = self.locales["en"]
        selected = self.locales.get(language, {})
        return {
            "id": self.scenario_id,
            **{field: selected.get(field, english[field]) for field in _PROMPT_FIELDS},
        }

    def _field(self, field: str, locale: str) -> str:
        return self.localized(locale)[field]

    @property
    def title_en(self) -> str:
        return self._field("title", "en")

    @property
    def title_vi(self) -> str:
        return self._field("title", "vi")

    @property
    def when_en(self) -> str:
        return self._field("when", "en")

    @property
    def when_vi(self) -> str:
        return self._field("when", "vi")

    @property
    def prompt_en(self) -> str:
        return self._field("prompt", "en")

    @property
    def prompt_vi(self) -> str:
        return self._field("prompt", "vi")

    @property
    def question_en(self) -> str:
        return self._field("question", "en")

    @property
    def question_vi(self) -> str:
        return self._field("question", "vi")


def _build_prompt_packs() -> dict[str, tuple[PromptScenario, ...]]:
    packs = _DATA.get("packs")
    if not isinstance(packs, dict):
        raise ValueError("Prompt packs must be an object")
    result: dict[str, tuple[PromptScenario, ...]] = {}
    for slug, raw_pack in packs.items():
        if not isinstance(raw_pack, dict) or not isinstance(
            raw_pack.get("scenarios"), list
        ):
            raise ValueError(f"Invalid prompt pack: {slug}")
        scenarios: list[PromptScenario] = []
        for raw_scenario in raw_pack["scenarios"]:
            if not isinstance(raw_scenario, dict):
                raise ValueError(f"Invalid prompt scenario: {slug}")
            locales = raw_scenario.get("locales")
            if not isinstance(locales, dict) or set(locales) != set(SUPPORTED_LOCALES):
                raise ValueError(
                    f"Prompt locale parity failed: {slug}/{raw_scenario.get('id')}"
                )
            normalized: dict[str, dict[str, str]] = {}
            for locale in SUPPORTED_LOCALES:
                fields = locales[locale]
                if not isinstance(fields, dict) or set(fields) != set(_PROMPT_FIELDS):
                    raise ValueError(f"Prompt field parity failed: {slug}/{locale}")
                if not all(isinstance(value, str) for value in fields.values()):
                    raise ValueError(f"Prompt values must be strings: {slug}/{locale}")
                normalized[locale] = dict(fields)
            scenarios.append(PromptScenario(str(raw_scenario["id"]), normalized))
        result[slug] = tuple(scenarios)
    return result


PROMPT_PACKS = _build_prompt_packs()


def scenarios_for(slug: str) -> tuple[PromptScenario, ...]:
    """Return the public scenario list for a Skill slug."""
    return PROMPT_PACKS.get(slug, ())
