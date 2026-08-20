from __future__ import annotations

from urllib.parse import unquote

import pytest

from soulmap.web.catalog import CATALOG
from soulmap.web.config import PUBLIC_SITE_URL
from soulmap.web.http import _nav_path
from soulmap.web.i18n import SUPPORTED_LOCALES
from soulmap.web.prompt_pack import scenarios_for
from soulmap.web.skill_views import (
    _provider_url,
    _skill_catalog,
    _skill_detail_fragment,
    _skill_page,
)


@pytest.mark.parametrize("entry", CATALOG, ids=lambda entry: entry.slug)
@pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
def test_skill_detail_keeps_localized_prompt_source_contract(
    entry: object, locale: str
) -> None:
    slug = entry.slug  # type: ignore[attr-defined]
    html = _skill_detail_fragment(slug, locale)

    assert html.count('class="prompt-scenario"') == 3
    assert html.count('class="prompt-scenario__source"') == 3
    assert html.count(f"{PUBLIC_SITE_URL}/api/raw/{slug}.md") >= 3
    assert "Provider links may require sign-in" not in html
    assert "Use this public SoulMap Markdown bundle" not in html


@pytest.mark.parametrize("entry", CATALOG, ids=lambda entry: entry.slug)
def test_provider_urls_include_prompt_question_and_raw_source(entry: object) -> None:
    slug = entry.slug  # type: ignore[attr-defined]
    raw_url = f"{PUBLIC_SITE_URL}/api/raw/{slug}.md"
    scenario = scenarios_for(slug)[0]
    for provider, prefix in (
        ("chatgpt", "https://chatgpt.com/?q="),
        ("claude", "https://claude.ai/new?q="),
        ("claude-code", "claude-cli://open?q="),
    ):
        url = _provider_url(provider, raw_url, scenario, "en")
        assert url.startswith(prefix)
        decoded = unquote(url.split("?q=", 1)[1])
        assert raw_url in decoded
        assert scenario.localized("en")["prompt"] in decoded
        assert scenario.localized("en")["question"] in decoded


@pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
def test_skill_catalog_preserves_locale_aware_search_contract(locale: str) -> None:
    html = _skill_catalog(locale, query="mirror")

    assert f'data-search-locale="{locale}"' in html
    assert 'data-search-api="' in html
    assert _nav_path("/api/skills/search.json", locale) in html
    assert 'id="skill-modal"' in html
    assert "mirror" in html.lower()


@pytest.mark.parametrize(
    ("locale", "skill_id_label"),
    [("en", "Skill ID"), ("vi", "Mã Skill"), ("ko", "Skill 식별자")],
)
def test_skill_cards_expose_localized_skill_id_accessible_labels(
    locale: str, skill_id_label: str
) -> None:
    html = _skill_catalog(locale)

    assert f'aria-label="{skill_id_label}: meta"' in html
    assert 'data-skill-slug="meta"' in html


@pytest.mark.parametrize("entry", CATALOG, ids=lambda entry: entry.slug)
def test_skill_page_has_canonical_catalog_link(entry: object) -> None:
    slug = entry.slug  # type: ignore[attr-defined]
    html = _skill_page(slug, "en")

    assert html
    assert 'class="page-hero"' in html
    assert 'class="section tinted"' in html
    assert 'class="container card"' in html
    assert 'href="/skills"' in html
    assert slug in html
