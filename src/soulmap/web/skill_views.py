"""Skill catalog and detail renderers for the SoulMap website."""

from __future__ import annotations

from html import escape
from urllib.parse import quote

from soulmap.web.catalog import (
    CATALOG,
    get_skill,
    locale_fields,
    raw_path,
)
from soulmap.web.catalog import (
    raw_url as raw_bundle_url,
)
from soulmap.web.http import _nav_path, _text, tr
from soulmap.web.pages import _not_found
from soulmap.web.prompt_pack import PromptScenario, scenarios_for
from soulmap.web.templates import render_template


def _provider_url(
    provider: str, raw_url: str, scenario: PromptScenario, locale: str
) -> str:
    localized = scenario.localized(locale)
    prompt = (
        localized["prompt"]
        + "\n\n"
        + tr(locale, "provider_source_instruction")
        + "\n"
        + raw_url
        + "\n\n"
        + tr(locale, "provider_starter_prefix")
        + " "
        + localized["question"]
    )
    encoded = quote(prompt, safe="")
    if provider == "chatgpt":
        return f"https://chatgpt.com/?q={encoded}"
    if provider == "claude":
        return f"https://claude.ai/new?q={encoded}"
    return f"claude-cli://open?q={encoded}"


def _render_prompt_scenario(
    entry_slug: str, raw_url: str, scenario: PromptScenario, locale: str
) -> str:
    localized = scenario.localized(locale)
    return render_template(
        "partials/prompt-scenario.html",
        scenario_title=escape(localized["title"]),
        when_label=_text(locale, "use_when"),
        scenario_when=escape(localized["when"]),
        prompt_label=_text(locale, "prompt_label"),
        scenario_prompt=escape(localized["prompt"]),
        source_label=_text(locale, "source_bundle"),
        raw_href=escape(raw_path(entry_slug, locale), quote=True),
        raw_url=escape(raw_url, quote=True),
        question_label=_text(locale, "starter_question"),
        scenario_question=escape(localized["question"]),
        chatgpt_url=escape(
            _provider_url("chatgpt", raw_url, scenario, locale), quote=True
        ),
        claude_url=escape(
            _provider_url("claude", raw_url, scenario, locale), quote=True
        ),
        claude_code_url=escape(
            _provider_url("claude-code", raw_url, scenario, locale), quote=True
        ),
        chatgpt_label=_text(locale, "open_chatgpt"),
        claude_label=_text(locale, "open_claude"),
        claude_code_label=_text(locale, "open_claude_code"),
    )


def _skill_detail_fragment(entry_slug: str, locale: str) -> str:
    entry = get_skill(entry_slug)
    if entry is None:
        return f"<p>{escape(_text(locale, 'skill_not_found_inline'))}</p>"
    fields = locale_fields(entry, locale)
    raw_url = raw_bundle_url(entry.slug, locale)
    return render_template(
        "partials/skill-detail.html",
        group=escape(fields["group"]),
        slug=escape(entry.slug),
        title=escape(fields["title"]),
        summary=escape(fields["summary"]),
        use_when_label=_text(locale, "use_when"),
        use_when=escape(fields["use_when"]),
        best_for_label=_text(locale, "best_for"),
        best_for=escape(fields["best_for"]),
        boundary_label=_text(locale, "boundary"),
        boundary=escape(fields["boundary"]),
        raw_note=_text(locale, "raw_note"),
        raw_href=escape(raw_path(entry.slug, locale), quote=True),
        raw_label=_text(locale, "raw"),
        raw_url=escape(raw_url, quote=True),
        copied_label=_text(locale, "copied"),
        copy_raw_label=_text(locale, "copy_raw"),
        copy_failed_label=_text(locale, "copy_failed"),
        prompt_heading=_text(locale, "prompt_heading"),
        prompt_intro=_text(locale, "prompt_intro"),
        prompt_scenarios="".join(
            _render_prompt_scenario(entry.slug, raw_url, scenario, locale)
            for scenario in scenarios_for(entry.slug)
        ),
    )


def _skill_cards(locale: str, query: str = "") -> str:
    cards = []
    normalised_query = query.strip().lower()
    for entry in CATALOG:
        fields = locale_fields(entry, locale)
        search_text = " ".join(fields.values()).lower()
        if normalised_query and normalised_query not in search_text:
            continue
        detail_href = _nav_path("/skills/" + entry.slug, locale)
        partial_href = f"/partials/skill/{entry.slug}.{locale}.html?lang={locale}"
        skill_slug = escape(entry.slug, quote=True)
        skill_id_label = escape(_text(locale, "skill_id_label"), quote=True)
        cards.append(
            f'<article class="skill-card" data-search="{escape(search_text)}" data-skill-slug="{skill_slug}">'
            f'<div class="skill-card__meta"><span>{escape(fields["group"])}</span><span class="skill-card__slug sr-only" data-skill-slug="{skill_slug}" aria-label="{skill_id_label}: {skill_slug}">{skill_slug}</span></div>'
            f'<div class="skill-card__body"><h2>{escape(fields["title"])}</h2><p>{escape(fields["summary"])}</p></div>'
            f'<div class="skill-card__actions"><a class="button small" href="{escape(detail_href, quote=True)}" hx-boost="false" aria-haspopup="dialog" aria-controls="skill-modal" hx-get="{escape(partial_href, quote=True)}" hx-target="#skill-modal-content" hx-swap="innerHTML" hx-indicator="#skill-loading" x-on:click="open(\'{escape(entry.slug)}\', $event.currentTarget)">{_text(locale, "details")}</a><a class="link-button small secondary" href="{escape(raw_path(entry.slug, locale), quote=True)}" target="_blank" rel="noopener">{_text(locale, "raw")}</a></div>'
            "</article>"
        )
    return (
        "".join(cards)
        or f'<p class="empty-state" role="status">{_text(locale, "no_results")}</p>'
    )


def _skill_grid_fragment(locale: str, query: str = "") -> str:
    return render_template(
        "partials/skill-grid.html",
        no_results_label=_text(locale, "no_results"),
        skill_cards=_skill_cards(locale, query),
    )


def _skill_catalog(locale: str, query: str = "") -> str:
    return render_template(
        "pages/skill-catalog.html",
        catalog_eyebrow=_text(locale, "catalog_eyebrow"),
        catalog_h1=_text(locale, "catalog_h1"),
        catalog_lede=_text(locale, "catalog_lede"),
        search_query_label=_text(locale, "search_query_label"),
        search_query_placeholder=_text(locale, "search_query_placeholder"),
        search_query_hint=_text(locale, "search_query_hint"),
        ask_query_label=_text(locale, "ask_query_label"),
        ask_query_placeholder=_text(locale, "ask_query_placeholder"),
        ask_query_hint=_text(locale, "ask_query_hint"),
        search_panel_title=_text(locale, "search_panel_title"),
        ask_panel_title=_text(locale, "ask_panel_title"),
        ask_results_heading=_text(locale, "ask_results_heading"),
        ask_browse_label=_text(locale, "ask_browse_label"),
        ask_details_label=_text(locale, "ask_details_label"),
        search_mode_label=_text(locale, "search_mode_label"),
        search_mode_search=_text(locale, "search_mode_search"),
        search_mode_ask=_text(locale, "search_mode_ask"),
        search_mode_search_hint=_text(locale, "search_mode_search_hint"),
        search_mode_ask_hint=_text(locale, "search_mode_ask_hint"),
        ask_intro=_text(locale, "ask_intro"),
        ask_result_label=_text(locale, "ask_result_label"),
        ask_use_label=_text(locale, "ask_use_label"),
        ask_provider_title=_text(locale, "ask_provider_title"),
        ask_provider_intro=_text(locale, "ask_provider_intro"),
        ask_provider_question=_text(locale, "ask_provider_question"),
        ask_provider_raw=_text(locale, "ask_provider_raw"),
        ask_no_results=_text(locale, "ask_no_results"),
        search_error=_text(locale, "search_error"),
        provider_source_instruction=_text(locale, "provider_source_instruction"),
        provider_starter_prefix=_text(locale, "provider_starter_prefix"),
        open_chatgpt=_text(locale, "open_chatgpt"),
        open_claude=_text(locale, "open_claude"),
        loading_label=_text(locale, "loading"),
        catalog_action=escape(_nav_path("/skills", locale), quote=True),
        search_api_endpoint=escape(
            _nav_path("/api/skills/search.json", locale), quote=True
        ),
        search_locale=locale,
        search_query=escape(query, quote=True),
        skill_grid=_skill_grid_fragment(locale, query),
        close_label=_text(locale, "close"),
        details_label=_text(locale, "details"),
        modal_title=_text(locale, "modal_title"),
    )


def _skill_page(entry_slug: str, locale: str) -> str:
    entry = get_skill(entry_slug)
    if entry is None:
        return _not_found(locale)
    fields = locale_fields(entry, locale)
    return render_template(
        "pages/skill-page.html",
        group=escape(fields["group"]),
        title=escape(fields["title"]),
        summary=escape(fields["summary"]),
        skills_href=escape(_nav_path("/skills", locale), quote=True),
        skills_label=_text(locale, "skills"),
        detail=_skill_detail_fragment(entry_slug, locale),
    )
