"""JSON-backed public Skill catalog and safe static serializers."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import cast

from soulmap.web.i18n import SUPPORTED_LOCALES
from soulmap.web.prompt_pack import scenarios_for

PUBLIC_RAW_BASE_URL = "https://tuanductran.github.io/soulmap-ai"
_CATALOG_FIELDS = ("group", "title", "summary", "use_when", "best_for", "boundary")


def _load_catalog_data() -> dict[str, object]:
    payload = json.loads(
        files("soulmap.web").joinpath("catalog_data.json").read_text(encoding="utf-8")
    )
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("Invalid catalog data version")
    return payload


_DATA = _load_catalog_data()
_RAW_COPY_VALUE = _DATA.get("raw_copy")
if not isinstance(_RAW_COPY_VALUE, dict):
    raise ValueError("Catalog raw_copy must be an object")
_RAW_COPY = cast(dict[str, dict[str, str]], _RAW_COPY_VALUE)


def _content_locale(locale: str) -> str:
    return locale if locale in SUPPORTED_LOCALES else "en"


def _response_locale(locale: str) -> str:
    return locale if locale in SUPPORTED_LOCALES else "en"


@dataclass(frozen=True)
class SkillEntry:
    """Public-facing metadata for one importable SoulMap capability group."""

    slug: str
    directory: str
    featured_file: str
    locales: dict[str, dict[str, str]]

    def public_dict(self) -> dict[str, object]:
        """Return metadata safe for the public catalog API."""
        fields = locale_fields(self, "en")
        return {
            "slug": self.slug,
            **fields,
            "raw_path": f"/api/raw/{self.slug}.md",
            "raw_url": f"{PUBLIC_RAW_BASE_URL}/api/raw/{self.slug}.md",
            "featured_file": self.featured_file,
            "prompt_scenarios": [
                scenario.localized("en") for scenario in scenarios_for(self.slug)
            ],
        }

    def _field(self, field: str, locale: str) -> str:
        return locale_fields(self, locale)[field]

    @property
    def group(self) -> str:
        return self._field("group", "en")

    @property
    def group_vi(self) -> str:
        return self._field("group", "vi")

    @property
    def title_en(self) -> str:
        return self._field("title", "en")

    @property
    def title_vi(self) -> str:
        return self._field("title", "vi")

    @property
    def summary_en(self) -> str:
        return self._field("summary", "en")

    @property
    def summary_vi(self) -> str:
        return self._field("summary", "vi")

    @property
    def use_when_en(self) -> str:
        return self._field("use_when", "en")

    @property
    def use_when_vi(self) -> str:
        return self._field("use_when", "vi")

    @property
    def best_for_en(self) -> str:
        return self._field("best_for", "en")

    @property
    def best_for_vi(self) -> str:
        return self._field("best_for", "vi")

    @property
    def boundary_en(self) -> str:
        return self._field("boundary", "en")

    @property
    def boundary_vi(self) -> str:
        return self._field("boundary", "vi")


def _build_catalog() -> tuple[SkillEntry, ...]:
    raw_entries = _DATA.get("entries")
    if not isinstance(raw_entries, list):
        raise ValueError("Catalog entries must be a list")
    entries: list[SkillEntry] = []
    for raw_entry in raw_entries:
        if not isinstance(raw_entry, dict):
            raise ValueError("Catalog entry must be an object")
        locales = raw_entry.get("locales")
        if not isinstance(locales, dict) or set(locales) != set(SUPPORTED_LOCALES):
            raise ValueError(f"Catalog locale parity failed: {raw_entry.get('slug')}")
        normalized: dict[str, dict[str, str]] = {}
        for locale in SUPPORTED_LOCALES:
            fields = locales[locale]
            if not isinstance(fields, dict) or set(fields) != set(_CATALOG_FIELDS):
                raise ValueError(
                    f"Catalog field parity failed: {raw_entry.get('slug')}/{locale}"
                )
            if not all(isinstance(value, str) for value in fields.values()):
                raise ValueError(
                    f"Catalog values must be strings: {raw_entry.get('slug')}/{locale}"
                )
            normalized[locale] = dict(fields)
        entries.append(
            SkillEntry(
                slug=str(raw_entry["slug"]),
                directory=str(raw_entry["directory"]),
                featured_file=str(raw_entry["featured_file"]),
                locales=normalized,
            )
        )
    return tuple(entries)


CATALOG: tuple[SkillEntry, ...] = _build_catalog()
_BY_SLUG = {entry.slug: entry for entry in CATALOG}
_SEARCH_FIELDS = _CATALOG_FIELDS


def _normalise_search_text(value: str) -> str:
    """Fold accents and punctuation so public search behaves consistently."""
    decomposed = unicodedata.normalize("NFKD", value.casefold().replace("đ", "d"))
    without_marks = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", " ", without_marks).strip()


def _search_tokens(value: str) -> tuple[str, ...]:
    return tuple(
        token for token in _normalise_search_text(value).split() if len(token) > 1
    )


def _public_entry_dict(
    entry: SkillEntry, locale: str = "en", raw_base_url: str = PUBLIC_RAW_BASE_URL
) -> dict[str, object]:
    language = _content_locale(locale)
    fields = locale_fields(entry, language)
    return {
        "slug": entry.slug,
        **fields,
        "raw_path": f"/api/raw/{entry.slug}.md",
        "raw_url": f"{raw_base_url.rstrip('/')}/api/raw/{entry.slug}.md"
        if raw_base_url
        else "",
        "featured_file": entry.featured_file,
        "prompt_scenarios": [
            scenario.localized(language) for scenario in scenarios_for(entry.slug)
        ],
    }


def search_catalog(
    locale: str = "en", query: str = "", group: str = "", limit: int = 50
) -> list[dict[str, object]]:
    """Search localized Skill metadata with deterministic relevance ranking."""
    language = _content_locale(locale)
    query_normalised = _normalise_search_text(query)
    query_tokens = _search_tokens(query)
    group_normalised = _normalise_search_text(group)
    bounded_limit = max(1, min(limit, 100))
    ranked: list[tuple[int, int, dict[str, object]]] = []

    for position, entry in enumerate(CATALOG):
        fields = locale_fields(entry, language)
        normalized_fields = {
            field: _normalise_search_text(fields[field]) for field in _SEARCH_FIELDS
        }
        normalized_slug = _normalise_search_text(entry.slug)
        if group_normalised and group_normalised not in normalized_fields["group"]:
            continue

        matched_fields: list[str] = []
        score = 0
        if query_normalised:
            if query_normalised == normalized_slug:
                score += 1000
                matched_fields.append("slug")
            if query_normalised == normalized_fields["title"]:
                score += 900
                matched_fields.append("title")
            for field, value in normalized_fields.items():
                if query_normalised in value:
                    score += {"group": 360, "title": 420}.get(field, 180)
                    if field not in matched_fields:
                        matched_fields.append(field)
            for token in query_tokens:
                for field, value in (
                    ("slug", normalized_slug),
                    *normalized_fields.items(),
                ):
                    if token in value:
                        score += 40 if token == value else 15
                        if field not in matched_fields:
                            matched_fields.append(field)
            if score == 0:
                continue

        result = _public_entry_dict(entry, language)
        result["score"] = score
        result["matched_fields"] = matched_fields
        ranked.append((score, -position, result))

    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [result for _, _, result in ranked[:bounded_limit]]


def catalog_search_json(
    locale: str = "en", query: str = "", group: str = "", limit: int = 50
) -> str:
    """Serialize the public, localized advanced-search response."""
    language = _content_locale(locale)
    bounded_limit = max(1, min(limit, 100))
    all_results = search_catalog(language, query, group, 100)
    results = all_results[:bounded_limit]
    return json.dumps(
        {
            "version": 1,
            "locale": _response_locale(locale),
            "query": query,
            "group": group,
            "limit": bounded_limit,
            "total": len(all_results),
            "results": results,
        },
        ensure_ascii=False,
        indent=2,
    )


def get_skill(slug: str) -> SkillEntry | None:
    """Return a catalog entry by public slug."""
    return _BY_SLUG.get(slug)


def _repo_root() -> Path:
    candidates = (
        Path(__file__).resolve().parents[3],
        Path.cwd(),
    )
    for candidate in candidates:
        if (candidate / "skills").is_dir():
            return candidate
    return candidates[0]


def _sanitize_public_markdown(
    markdown: str,
    behavioral_contract: str = "SoulMap behavioral contract",
    internal_references: str = "repository internals",
) -> str:
    """Remove repository-only references while preserving public Skill guidance."""
    sanitized = re.sub(r"\[([^\]]+)\]\((?:\.\./)+AGENTS\.md\)", r"\1", markdown)
    sanitized = re.sub(r"\[AGENTS\.md\]\([^)]*\)", behavioral_contract, sanitized)
    sanitized = sanitized.replace("AGENTS.md", behavioral_contract)
    sanitized = re.sub(
        r"(?<!\w)(?:\.claude/|\.github/|src/|tests/|pyproject\.toml|uv\.lock)(?:[A-Za-z0-9_./-]*)",
        internal_references,
        sanitized,
    )
    return sanitized


def _raw_copy(locale: str) -> dict[str, str]:
    language = _content_locale(locale)
    selected = _RAW_COPY.get(language)
    english = _RAW_COPY.get("en")
    if not isinstance(selected, dict) or not isinstance(english, dict):
        raise ValueError("Invalid raw copy locale data")
    selected_copy = {str(key): str(value) for key, value in selected.items()}
    english_copy = {str(key): str(value) for key, value in english.items()}
    return {key: selected_copy.get(key, value) for key, value in english_copy.items()}


def raw_markdown(entry: SkillEntry, locale: str = "en") -> str:
    """Build one complete public Markdown bundle for a catalog group."""
    language = _content_locale(locale)
    labels = _raw_copy(language)
    fields = locale_fields(entry, language)
    directory = _repo_root() / "skills" / entry.directory
    files = sorted(directory.glob("*.md")) if directory.is_dir() else []
    sections = [
        f"# {labels['bundle_title']}: {fields['title']}\n\n",
        f"> {labels['canonical_bundle']} `{entry.slug}`.\n\n",
    ]
    if not files:
        sections.append(f"{labels['unavailable']}\n")
        return "".join(sections)
    for path in files:
        sections.append(f"\n---\n\n## {path.name}\n\n")
        sections.append(
            _sanitize_public_markdown(
                path.read_text(encoding="utf-8"),
                labels["behavioral_contract"],
                labels["repository_internals"],
            )
        )
        sections.append("\n")
    scenarios = scenarios_for(entry.slug)
    raw_url = f"{PUBLIC_RAW_BASE_URL}/api/raw/{entry.slug}.md"
    if scenarios:
        sections.append(f"\n---\n\n## {labels['suggested_prompts']}\n\n")
        sections.append(f"{labels['use_one']}\n\n")
        for scenario in scenarios:
            localized = scenario.localized(language)
            sections.append(f"### {localized['title']}\n\n")
            sections.append(f"**{labels['when']}:** {localized['when']}\n\n")
            sections.append(f"**{labels['prompt']}:** {localized['prompt']}\n\n")
            sections.append(f"**{labels['source_bundle']}:** {raw_url}\n\n")
            sections.append(
                f"**{labels['starter_question']}:** {localized['question']}\n\n"
            )
    return "".join(sections)


def catalog_json(locale: str = "en", raw_base_url: str = PUBLIC_RAW_BASE_URL) -> str:
    """Serialize localized public catalog metadata without private paths."""
    language = _content_locale(locale)
    entries = [_public_entry_dict(entry, language, raw_base_url) for entry in CATALOG]
    return json.dumps(
        {"version": 1, "locale": _response_locale(locale), "skills": entries},
        ensure_ascii=False,
        indent=2,
    )


def locale_fields(entry: SkillEntry, locale: str) -> dict[str, str]:
    """Return localized catalog copy with English fallback."""
    language = _content_locale(locale)
    english = entry.locales["en"]
    selected = entry.locales.get(language, {})
    return {field: selected.get(field, english[field]) for field in _CATALOG_FIELDS}
