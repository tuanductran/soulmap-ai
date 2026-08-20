"""A small, dependency-free responsive website for SoulMap AI.

The website is separate from the shipped knowledge artifacts at runtime, while the
public catalog exposes curated Skill bundles through explicit raw endpoints.
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections.abc import Callable
from html import escape
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server
from wsgiref.types import StartResponse

from soulmap.web.catalog import (
    CATALOG,
    catalog_json,
    catalog_search_json,
    get_skill,
    locale_fields,
    raw_markdown,
)
from soulmap.web.i18n import LOCALES as TEXT
from soulmap.web.i18n import SUPPORTED_LOCALES, messages_json
from soulmap.web.prompt_pack import PromptScenario, scenarios_for
from soulmap.web.seo import metadata, robots_txt, sitemap_xml
from soulmap.web.templates import render_template

HOST = "127.0.0.1"
PORT = 8765
SITE_NAME = "SoulMap AI"
RELEASE_URL = "https://github.com/tuanductran/soulmap-ai/releases/latest"
REPOSITORY_URL = "https://github.com/tuanductran/soulmap-ai"
PUBLIC_SITE_URL = "https://tuanductran.github.io/soulmap-ai"
HTMX_URL = "https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"
ALPINE_URL = "https://cdn.jsdelivr.net/npm/@alpinejs/csp@3.16.2/dist/cdn.min.js"
INTER_CSS_URL = "https://rsms.me/inter/inter.css"
HTMX_SRI = "sha384-H5SrcfygHmAuTDZphMHqBJLc3FhssKjG7w/CeCpFReSfwBWDTKpkzPP8c+cLsK+V"
ALPINE_SRI = "sha384-V/6+qWbzTJSzEweFWozPRF8In+k5cIL398rKMOn3YTJwFQAubV91vSnII3clycgX"


def _read_static_css() -> str:
    return (Path(__file__).with_name("static") / "site.css").read_text(encoding="utf-8")


def _origin(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}/"


def _resource_hints() -> str:
    """Generate conservative, deduplicated resource hints from critical URLs."""
    external_urls = (INTER_CSS_URL, HTMX_URL, ALPINE_URL)
    origins = tuple(
        dict.fromkeys(origin for url in external_urls if (origin := _origin(url)))
    )
    critical_origin = _origin(INTER_CSS_URL)
    hints: list[str] = []
    if critical_origin:
        hints.append(
            f'<link rel="preconnect" href="{escape(critical_origin, quote=True)}">'
        )
    hints.extend(
        f'<link rel="dns-prefetch" href="{escape(origin, quote=True)}">'
        for origin in origins
    )
    hints.append(
        f'<link rel="preload" href="{escape(INTER_CSS_URL, quote=True)}" '
        'as="style" type="text/css">'
    )
    return "\n".join(hints)


def tr(locale: str, key: str) -> str:
    return TEXT.get(locale, TEXT["en"]).get(key, TEXT["en"].get(key, key))


def _nav_path(route: str, locale: str) -> str:
    if locale == "en":
        return route or "/"
    return f"/{locale}{route if route != '/' else ''}"


def _text(locale: str, key: str) -> str:
    return escape(tr(locale, key))


_SEO_COPY_KEYS: dict[str, tuple[str, str]] = {
    "/": ("home_h1", "home_lede"),
    "/how-it-works": ("how_h1", "how_lede"),
    "/boundaries": ("boundaries_h1", "boundaries_lede"),
    "/download": ("download_h1", "download_lede"),
    "/notes": ("notes_h1", "notes_lede"),
    "/about": ("about_h1", "about_lede"),
    "/faq": ("faq_h1", "faq_lede"),
    "/privacy": ("privacy_page_h1", "privacy_page_lede"),
    "/skills": ("catalog_h1", "catalog_lede"),
}


def _seo_copy(
    path: str, locale: str, fallback_title: str, fallback_description: str
) -> tuple[str, str]:
    keys = _SEO_COPY_KEYS.get(path)
    if keys is None:
        return fallback_title, fallback_description
    title_key, description_key = keys
    return tr(locale, title_key), tr(locale, description_key)


def _nav(path: str, locale: str) -> str:
    links = (
        ("/", "home"),
        ("/how-it-works", "how"),
        ("/boundaries", "boundaries"),
        ("/notes", "notes"),
        ("/about", "about"),
        ("/faq", "faq"),
        ("/skills", "skills"),
    )
    rendered = "".join(
        '<a href="{}"{}>{}</a>'.format(
            escape(_nav_path(href, locale), quote=True),
            ' aria-current="page"' if path == href else "",
            _text(locale, label_key),
        )
        for href, label_key in links
    )
    locale_options = "".join(
        '<a class="locale-option" role="menuitem" href="{}" lang="{}"{}>'
        '<span>{}</span><span class="locale-code">{}</span></a>'.format(
            escape(_nav_path(path, target_locale), quote=True),
            target_locale,
            ' aria-current="page"' if target_locale == locale else "",
            _text(locale, f"language_name_{target_locale}"),
            target_locale.upper(),
        )
        for target_locale in SUPPORTED_LOCALES
    )
    return render_template(
        "partials/nav.html",
        brand_home=escape(_nav_path("/", locale), quote=True),
        brand_home_label=_text(locale, "brand_home_label"),
        nav_links=rendered,
        primary_nav_label=_text(locale, "primary_nav_label"),
        language_label=_text(locale, "language"),
        locale_options=locale_options,
        current_locale_upper=locale.upper(),
    )


def _layout(title: str, description: str, path: str, content: str, locale: str) -> str:
    language = locale if locale in SUPPORTED_LOCALES else "en"
    seo_title, seo_description = _seo_copy(path, locale, title, description)
    seo = metadata(
        site_url=PUBLIC_SITE_URL,
        repository_url=REPOSITORY_URL,
        route=path,
        locale=locale,
        title=seo_title,
        description=seo_description,
    )
    footer = render_template(
        "partials/footer.html",
        footer_label=_text(locale, "footer"),
        faq_href=escape(_nav_path("/faq", locale), quote=True),
        faq_label=_text(locale, "faq"),
        privacy_href=escape(_nav_path("/privacy", locale), quote=True),
        privacy_label=_text(locale, "privacy_page"),
        download_href=escape(_nav_path("/download", locale), quote=True),
        download_label=_text(locale, "download"),
        repository_url=escape(REPOSITORY_URL, quote=True),
        repository_label=_text(locale, "repository"),
    )
    return render_template(
        "layout.html",
        language=language,
        description=escape(seo_description, quote=True),
        locale_json=messages_json(locale),
        title=escape(seo_title),
        site_name=escape(SITE_NAME),
        skip_label=_text(locale, "skip"),
        nav=_nav(path, locale),
        content=content,
        footer=footer,
        canonical_url=seo["canonical_url"],
        alternate_links=seo["alternate_links"],
        og_title=seo["og_title"],
        og_description=seo["og_description"],
        og_url=seo["og_url"],
        og_locale=seo["og_locale"],
        og_locale_alternate=seo["og_locale_alternate"],
        json_ld=seo["json_ld"],
        resource_hints=_resource_hints(),
        inter_css_url=escape(INTER_CSS_URL, quote=True),
        htmx_url=escape(HTMX_URL, quote=True),
        htmx_sri=escape(HTMX_SRI, quote=True),
        alpine_url=escape(ALPINE_URL, quote=True),
        alpine_sri=escape(ALPINE_SRI, quote=True),
    )


def _home(locale: str) -> str:
    principles = "".join(
        f'<article class="card"><span class="number">0{index}</span><h3>{_text(locale, title_key)}</h3><p>{_text(locale, body_key)}</p></article>'
        for index, (title_key, body_key) in enumerate(
            (
                ("mirror_first", "mirror_first_body"),
                ("bounded", "bounded_body"),
                ("independence", "independence_body"),
            ),
            1,
        )
    )
    path_cards = "".join(
        f'<article class="card"><h3 class="card-title">{_text(locale, title_key)}</h3><p>{_text(locale, body_key)}</p><a class="link-button" href="{escape(_nav_path(href, locale), quote=True)}">{_text(locale, link_key)}</a></article>'
        for title_key, body_key, link_key, href in (
            ("home_path_1", "home_path_1_body", "home_path_1_link", "/how-it-works"),
            ("home_path_2", "home_path_2_body", "home_path_2_link", "/skills"),
            ("home_path_3", "home_path_3_body", "home_path_3_link", "/faq"),
        )
    )
    return render_template(
        "pages/home.html",
        home_eyebrow=_text(locale, "home_eyebrow"),
        home_h1=_text(locale, "home_h1"),
        home_lede=_text(locale, "home_lede"),
        how_href=escape(_nav_path("/how-it-works", locale), quote=True),
        home_how=_text(locale, "home_how"),
        skills_href=escape(_nav_path("/skills", locale), quote=True),
        home_skills=_text(locale, "home_skills"),
        home_principle=_text(locale, "home_principle"),
        principle_label=_text(locale, "principle_label"),
        home_section_eyebrow=_text(locale, "home_section_eyebrow"),
        home_section_h2=_text(locale, "home_section_h2"),
        home_section_lede=_text(locale, "home_section_lede"),
        principles=principles,
        path_cards=path_cards,
        home_path_eyebrow=_text(locale, "home_path_eyebrow"),
        home_path_h2=_text(locale, "home_path_h2"),
        home_path_lede=_text(locale, "home_path_lede"),
        quiet_eyebrow=_text(locale, "quiet_eyebrow"),
        quiet_h2=_text(locale, "quiet_h2"),
        quiet_p1=_text(locale, "quiet_p1"),
        quiet_p2=_text(locale, "quiet_p2"),
        boundaries_href=escape(_nav_path("/boundaries", locale), quote=True),
        read_boundaries=_text(locale, "read_boundaries"),
    )


def _how_it_works(locale: str) -> str:
    steps = "".join(
        f'<article class="step"><div><h2 class="step-title">{_text(locale, title_key)}</h2><p>{_text(locale, body_key)}</p></div></article>'
        for title_key, body_key in (
            ("step_1", "step_1_body"),
            ("step_2", "step_2_body"),
            ("step_3", "step_3_body"),
        )
    )
    return render_template(
        "pages/how-it-works.html",
        how_eyebrow=_text(locale, "how_eyebrow"),
        how_h1=_text(locale, "how_h1"),
        how_lede=_text(locale, "how_lede"),
        steps=steps,
        changes=_text(locale, "changes"),
        changes_h2=_text(locale, "changes_h2"),
        changes_body=_text(locale, "changes_body"),
    )


def _boundaries(locale: str) -> str:
    cards = "".join(
        f'<article class="card"><h2 class="card-title">{_text(locale, title_key)}</h2><p>{_text(locale, body_key)}</p></article>'
        for title_key, body_key in (
            ("no_diagnose", "no_diagnose_body"),
            ("no_predict", "no_predict_body"),
            ("no_replace", "no_replace_body"),
        )
    )
    privacy_items = "".join(
        f"<li>{_text(locale, key)}</li>"
        for key in ("privacy_1", "privacy_2", "privacy_3", "privacy_4")
    )
    return render_template(
        "pages/boundaries.html",
        boundaries_eyebrow=_text(locale, "boundaries_eyebrow"),
        boundaries_h1=_text(locale, "boundaries_h1"),
        boundaries_lede=_text(locale, "boundaries_lede"),
        boundary_cards=cards,
        privacy=_text(locale, "privacy"),
        privacy_h2=_text(locale, "privacy_h2"),
        privacy_items=privacy_items,
    )


def _download(locale: str) -> str:
    return render_template(
        "pages/download.html",
        download_eyebrow=_text(locale, "download_eyebrow"),
        download_h1=_text(locale, "download_h1"),
        download_lede=_text(locale, "download_lede"),
        skill_package=_text(locale, "skill_package"),
        skill_package_body=_text(locale, "skill_package_body"),
        knowledge_archive=_text(locale, "knowledge_archive"),
        knowledge_archive_body=_text(locale, "knowledge_archive_body"),
        release_url=escape(RELEASE_URL, quote=True),
        open_releases=_text(locale, "open_releases"),
        view_release=_text(locale, "view_release"),
        before_import=_text(locale, "before_import"),
        start_artifact=_text(locale, "start_artifact"),
        artifact_body=_text(locale, "artifact_body"),
    )


def _notes(locale: str) -> str:
    cards = "".join(
        f'<article class="card"><span class="note-label">{_text(locale, label_key)}</span><h2 class="card-title">{_text(locale, title_key)}</h2><p>{_text(locale, body_key)}</p></article>'
        for label_key, title_key, body_key in zip(
            ("notes_label_1", "notes_label_2", "notes_label_3"),
            ("note_1", "note_2", "note_3"),
            ("note_1_body", "note_2_body", "note_3_body"),
            strict=True,
        )
    )
    return render_template(
        "pages/notes.html",
        notes_eyebrow=_text(locale, "notes_eyebrow"),
        notes_h1=_text(locale, "notes_h1"),
        notes_lede=_text(locale, "notes_lede"),
        note_cards=cards,
        notes_callout=_text(locale, "notes_callout"),
    )


def _about(locale: str) -> str:
    return render_template(
        "pages/about.html",
        about_eyebrow=_text(locale, "about_eyebrow"),
        about_h1=_text(locale, "about_h1"),
        about_lede=_text(locale, "about_lede"),
        posture=_text(locale, "posture"),
        posture_h2=_text(locale, "posture_h2"),
        posture_p1=_text(locale, "posture_p1"),
        posture_p2=_text(locale, "posture_p2"),
        about_callout=_text(locale, "about_callout"),
    )


def _faq(locale: str) -> str:
    faq_items = "".join(
        f'<details class="faq-item"><summary>{_text(locale, question_key)}</summary><div class="faq-answer"><p>{_text(locale, answer_key)}</p></div></details>'
        for question_key, answer_key in (
            ("faq_q_1", "faq_a_1"),
            ("faq_q_2", "faq_a_2"),
            ("faq_q_3", "faq_a_3"),
            ("faq_q_4", "faq_a_4"),
            ("faq_q_5", "faq_a_5"),
            ("faq_q_6", "faq_a_6"),
        )
    )
    return render_template(
        "pages/faq.html",
        faq_eyebrow=_text(locale, "faq_eyebrow"),
        faq_h1=_text(locale, "faq_h1"),
        faq_lede=_text(locale, "faq_lede"),
        faq_items=faq_items,
    )


def _privacy(locale: str) -> str:
    return render_template(
        "pages/privacy.html",
        privacy_page_eyebrow=_text(locale, "privacy_page_eyebrow"),
        privacy_page_h1=_text(locale, "privacy_page_h1"),
        privacy_page_lede=_text(locale, "privacy_page_lede"),
        privacy_scope_h2=_text(locale, "privacy_scope_h2"),
        privacy_scope_body=_text(locale, "privacy_scope_body"),
        privacy_collect_h2=_text(locale, "privacy_collect_h2"),
        privacy_collect_body=_text(locale, "privacy_collect_body"),
        privacy_use_h2=_text(locale, "privacy_use_h2"),
        privacy_use_body=_text(locale, "privacy_use_body"),
        privacy_storage_h2=_text(locale, "privacy_storage_h2"),
        privacy_storage_body=_text(locale, "privacy_storage_body"),
        privacy_links_h2=_text(locale, "privacy_links_h2"),
        privacy_links_body=_text(locale, "privacy_links_body"),
        privacy_contact_h2=_text(locale, "privacy_contact_h2"),
        privacy_contact_body=_text(locale, "privacy_contact_body"),
        privacy_updated=_text(locale, "privacy_updated"),
    )


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
        raw_href=escape(f"/api/raw/{entry_slug}.md", quote=True),
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
        return "<p>Skill not found.</p>"
    fields = locale_fields(entry, locale)
    raw_url = f"{PUBLIC_SITE_URL}/api/raw/{entry.slug}.md"
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
        raw_href=escape(f"/api/raw/{entry.slug}.md", quote=True),
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
        cards.append(
            f'<article class="skill-card" data-search="{escape(search_text)}">'
            f'<div class="skill-card__meta"><span>{escape(fields["group"])}</span><span class="code-pill">{escape(entry.slug)}</span></div>'
            f'<div class="skill-card__body"><h2>{escape(fields["title"])}</h2><p>{escape(fields["summary"])}</p></div>'
            f'<div class="skill-card__actions"><a class="button small" href="{escape(detail_href, quote=True)}" aria-haspopup="dialog" aria-controls="skill-modal" hx-get="{escape(partial_href, quote=True)}" hx-target="#skill-modal-content" hx-swap="innerHTML" hx-indicator="#skill-loading" x-on:click="open(\'{escape(entry.slug)}\', $event.currentTarget)">{_text(locale, "details")}</a><a class="link-button small secondary" href="/api/raw/{escape(entry.slug)}.md" target="_blank" rel="noopener">{_text(locale, "raw")}</a></div>'
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
        ask_no_results=_text(locale, "ask_no_results"),
        search_error=_text(locale, "search_error"),
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


def _not_found(locale: str) -> str:
    return render_template(
        "pages/not-found.html",
        not_found=_text(locale, "not_found"),
        not_found_body=_text(locale, "not_found_body"),
        home_href=escape(_nav_path("/", locale), quote=True),
        return_home=_text(locale, "return_home"),
    )


def _sitemap_routes() -> list[str]:
    routes = list(_pages())
    routes.extend(f"/skills/{entry.slug}" for entry in CATALOG)
    return routes


def _pages() -> dict[str, tuple[str, str, Callable[[str], str]]]:
    return {
        "/": (
            "Hear yourself more clearly",
            "A reflective companion built around self-trust.",
            _home,
        ),
        "/how-it-works": (
            "How it works",
            "How SoulMap uses reflection without taking authority away.",
            _how_it_works,
        ),
        "/boundaries": (
            "Boundaries",
            "The safety and scope boundaries behind SoulMap.",
            _boundaries,
        ),
        "/download": (
            "Download SoulMap Skills",
            "Import the SoulMap Skill or knowledge archive into an AI tool.",
            _download,
        ),
        "/notes": ("Notes", "Grounded public writing from SoulMap AI.", _notes),
        "/about": (
            "About SoulMap AI",
            "The brand posture and purpose behind SoulMap AI.",
            _about,
        ),
        "/faq": (
            "FAQ",
            "Practical answers about SoulMap Skills, boundaries and privacy.",
            _faq,
        ),
        "/privacy": (
            "Privacy",
            "The current public-site privacy boundary for SoulMap AI.",
            _privacy,
        ),
        "/skills": (
            "SoulMap Skills",
            "Choose the SoulMap layer that fits the moment.",
            _skill_catalog,
        ),
    }


def _response(
    start_response: StartResponse,
    status: str,
    content_type: str,
    body: str | bytes,
    extra_headers: list[tuple[str, str]] | None = None,
) -> list[bytes]:
    payload = body if isinstance(body, bytes) else body.encode("utf-8")
    headers = [
        ("Content-Type", f"{content_type}; charset=utf-8"),
        ("Content-Length", str(len(payload))),
        ("X-Content-Type-Options", "nosniff"),
        (
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' https://rsms.me; font-src 'self' https://rsms.me; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; object-src 'none'",
        ),
        ("Permissions-Policy", "camera=(), microphone=(), geolocation=()"),
        ("Referrer-Policy", "strict-origin-when-cross-origin"),
    ]
    if extra_headers:
        headers.extend(extra_headers)
    start_response(status, headers)
    return [payload]


def _normalise_request_path(path: str) -> tuple[str, str]:
    normal = "/" + path.strip("/") if path.strip("/") else "/"
    parts = normal.strip("/").split("/") if normal != "/" else []
    if parts and parts[0] in SUPPORTED_LOCALES:
        locale = parts.pop(0)
        route = "/" + "/".join(parts) if parts else "/"
        return route, locale
    return normal, "en"


def application(
    environ: dict[str, object], start_response: StartResponse
) -> list[bytes]:
    """Serve the public SoulMap website using the WSGI protocol."""
    raw_path = str(environ.get("PATH_INFO") or "/")
    raw_query = str(environ.get("QUERY_STRING") or "")
    if raw_path == "/en" or raw_path.startswith("/en/"):
        canonical_path = raw_path[3:] or "/"
        location = canonical_path + (f"?{raw_query}" if raw_query else "")
        return _response(
            start_response,
            "301 Moved Permanently",
            "text/plain",
            f"Canonical English route: {location}\n",
            [("Location", location), ("Cache-Control", "public, max-age=300")],
        )
    if raw_path == "/private" or raw_path.startswith("/private/"):
        suffix = raw_path.removeprefix("/private") or ""
        location = "/privacy" + suffix + (f"?{raw_query}" if raw_query else "")
        return _response(
            start_response,
            "301 Moved Permanently",
            "text/plain",
            f"Canonical privacy route: {location}\n",
            [("Location", location), ("Cache-Control", "public, max-age=300")],
        )
    path, locale = _normalise_request_path(raw_path)
    query = parse_qs(raw_query)
    locale = (
        query.get("lang", [locale])[0]
        if query.get("lang", [locale])[0] in SUPPORTED_LOCALES
        else locale
    )
    if path == "/favicon.ico":
        favicon_path = Path(__file__).with_name("static") / "favicon.ico"
        return _response(
            start_response,
            "200 OK",
            "image/x-icon",
            favicon_path.read_bytes(),
            [("Cache-Control", "public, max-age=86400")],
        )
    if path == "/static/site.css":
        return _response(
            start_response,
            "200 OK",
            "text/css",
            _read_static_css(),
            [("Cache-Control", "public, max-age=300")],
        )
    if path in {"/static/site.js", "/static/search.js"}:
        js_path = Path(__file__).with_name("static") / path.rsplit("/", 1)[-1]
        return _response(
            start_response,
            "200 OK",
            "text/javascript",
            js_path.read_text(encoding="utf-8"),
            [("Cache-Control", "public, max-age=300")],
        )
    if path == "/robots.txt":
        return _response(
            start_response,
            "200 OK",
            "text/plain",
            robots_txt(PUBLIC_SITE_URL),
            [("Cache-Control", "public, max-age=300")],
        )
    if path == "/sitemap.xml":
        return _response(
            start_response,
            "200 OK",
            "application/xml",
            sitemap_xml(PUBLIC_SITE_URL, _sitemap_routes()),
            [("Cache-Control", "public, max-age=300")],
        )
    if path == "/api/skills.json":
        return _response(
            start_response,
            "200 OK",
            "application/json",
            catalog_json(locale),
            [
                ("Access-Control-Allow-Origin", "*"),
                ("Cache-Control", "public, max-age=300"),
            ],
        )
    if path == "/api/skills/search.json":
        query_value = query.get("q", [""])[0]
        group_value = query.get("group", [""])[0]
        try:
            limit_value = int(query.get("limit", ["50"])[0])
        except ValueError:
            limit_value = 50
        return _response(
            start_response,
            "200 OK",
            "application/json",
            catalog_search_json(locale, query_value, group_value, limit_value),
            [
                ("Access-Control-Allow-Origin", "*"),
                ("Cache-Control", "public, max-age=300"),
            ],
        )
    if (
        path.startswith("/api/skills/")
        and path.rsplit("/", 1)[-1].startswith("prompts")
        and path.endswith(".json")
    ):
        prompt_path = path.removeprefix("/api/skills/")
        prompt_slug, separator, prompt_filename = prompt_path.rpartition("/")
        prompt_locale = locale
        if separator and prompt_filename == "prompts.json":
            suffix = "/prompts.json"
        elif separator and prompt_filename.startswith("prompts."):
            requested_locale = prompt_filename.removeprefix("prompts.").removesuffix(
                ".json"
            )
            if requested_locale not in SUPPORTED_LOCALES:
                prompt_slug = ""
            prompt_locale = requested_locale
            suffix = f"/prompts.{requested_locale}.json"
        else:
            prompt_slug = ""
            suffix = ""
        slug = prompt_slug if suffix else ""
        entry = get_skill(slug)
        if entry is None:
            return _response(
                start_response,
                "404 Not Found",
                "application/json",
                json.dumps({"error": "skill_not_found"}),
            )
        return _response(
            start_response,
            "200 OK",
            "application/json",
            json.dumps(
                {
                    "version": 1,
                    "locale": prompt_locale,
                    "slug": entry.slug,
                    "raw_url": f"{PUBLIC_SITE_URL}/api/raw/{entry.slug}.md",
                    "scenarios": [
                        scenario.localized(prompt_locale)
                        for scenario in scenarios_for(entry.slug)
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            [
                ("Access-Control-Allow-Origin", "*"),
                ("Cache-Control", "public, max-age=300"),
            ],
        )
    if path.startswith("/api/skills/") and path.endswith(".json"):
        entry = get_skill(path.removeprefix("/api/skills/").removesuffix(".json"))
        if entry is None:
            return _response(
                start_response,
                "404 Not Found",
                "application/json",
                json.dumps({"error": "skill_not_found"}),
            )
        data = locale_fields(entry, locale) | {
            "slug": entry.slug,
            "raw_path": f"/api/raw/{entry.slug}.md",
            "raw_url": f"{PUBLIC_SITE_URL}/api/raw/{entry.slug}.md",
            "prompt_scenarios": [
                scenario.localized(locale) for scenario in scenarios_for(entry.slug)
            ],
        }
        return _response(
            start_response,
            "200 OK",
            "application/json",
            json.dumps(data, ensure_ascii=False),
            [
                ("Access-Control-Allow-Origin", "*"),
                ("Cache-Control", "public, max-age=300"),
            ],
        )
    if path.startswith("/api/raw/") and path.endswith(".md"):
        entry = get_skill(path.removeprefix("/api/raw/").removesuffix(".md"))
        if entry is None:
            return _response(
                start_response, "404 Not Found", "text/plain", "Skill not found.\n"
            )
        return _response(
            start_response,
            "200 OK",
            "text/markdown",
            raw_markdown(entry),
            [
                ("Access-Control-Allow-Origin", "*"),
                ("Content-Disposition", "inline"),
                ("Cache-Control", "public, max-age=300"),
            ],
        )
    if path == "/partials/skills-grid.html":
        query_value = query.get("q", [""])[0]
        return _response(
            start_response,
            "200 OK",
            "text/html",
            _skill_grid_fragment(locale, query_value),
            [("Vary", "HX-Request"), ("Cache-Control", "no-store")],
        )
    if path.startswith("/partials/skill/") and path.endswith(".html"):
        filename = path.removeprefix("/partials/skill/").removesuffix(".html")
        slug, _, partial_locale = filename.rpartition(".")
        if not slug:
            slug, partial_locale = filename, locale
        partial_locale = (
            partial_locale if partial_locale in SUPPORTED_LOCALES else locale
        )
        if get_skill(slug) is None:
            return _response(
                start_response,
                "404 Not Found",
                "text/html",
                f'<p class="empty-state" role="status">{_text(partial_locale, "skill_not_found")}</p>',
                [("Cache-Control", "no-store")],
            )
        return _response(
            start_response,
            "200 OK",
            "text/html",
            _skill_detail_fragment(slug, partial_locale),
        )
    if path.startswith("/skills/") and path.count("/") == 2:
        slug = path.removeprefix("/skills/")
        entry = get_skill(slug)
        if entry is None:
            return _response(
                start_response,
                "404 Not Found",
                "text/html",
                _layout(
                    "Not found",
                    "Page not found.",
                    "/skills",
                    _not_found(locale),
                    locale,
                ),
            )
        content = _skill_page(slug, locale)
        return _response(
            start_response,
            "200 OK",
            "text/html",
            _layout(
                locale_fields(entry, locale)["title"],
                locale_fields(entry, locale)["summary"],
                "/skills/" + slug,
                content,
                locale,
            ),
        )
    if path == "/skills":
        query_value = query.get("q", [""])[0]
        return _response(
            start_response,
            "200 OK",
            "text/html",
            _layout(
                "SoulMap Skills",
                "Choose the SoulMap layer that fits the moment.",
                path,
                _skill_catalog(locale, query_value),
                locale,
            ),
        )
    pages = _pages()
    if path not in pages:
        return _response(
            start_response,
            "404 Not Found",
            "text/html",
            _layout("Not found", "Page not found.", path, _not_found(locale), locale),
        )
    title, description, renderer = pages[path]
    return _response(
        start_response,
        "200 OK",
        "text/html",
        _layout(title, description, path, renderer(locale), locale),
    )


def _normalise_base_path(base_path: str) -> str:
    cleaned = base_path.strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def _apply_base_path(content: str, base_path: str) -> str:
    if not base_path:
        return content
    for attribute in (
        "href",
        "src",
        "hx-get",
        "action",
        "data-search-api",
        "data-skill-root",
    ):
        content = content.replace(f'{attribute}="/', f'{attribute}="{base_path}/')
    return content


def _write_page(
    output: Path, route: str, page: str, written: list[Path], base_path: str
) -> None:
    destination = output / ("index.html" if route == "/" else route.strip("/"))
    destination = destination if destination.suffix else destination / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(_apply_base_path(page, base_path), encoding="utf-8")
    written.append(destination)


def export_static(output: Path, base_path: str = "") -> list[Path]:
    """Export public pages, locale variants, API JSON, raw bundles and partials."""
    output = output.resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    normalised_base = _normalise_base_path(base_path)
    written: list[Path] = []
    pages = _pages()
    for locale in SUPPORTED_LOCALES:
        locale_prefix = "" if locale == "en" else f"/{locale}"
        for route, (title, description, renderer) in pages.items():
            page_route = f"{locale_prefix}{route if route != '/' else ''}" or "/"
            _write_page(
                output,
                page_route,
                _layout(title, description, route, renderer(locale), locale),
                written,
                normalised_base,
            )
    for entry in CATALOG:
        for locale in SUPPORTED_LOCALES:
            prefix = "" if locale == "en" else f"/{locale}"
            _write_page(
                output,
                f"{prefix}/skills/{entry.slug}",
                _layout(
                    locale_fields(entry, locale)["title"],
                    locale_fields(entry, locale)["summary"],
                    f"/skills/{entry.slug}",
                    _skill_page(entry.slug, locale),
                    locale,
                ),
                written,
                normalised_base,
            )
            partial = output / f"partials/skill/{entry.slug}.{locale}.html"
            partial.parent.mkdir(parents=True, exist_ok=True)
            partial.write_text(
                _apply_base_path(
                    _skill_detail_fragment(entry.slug, locale), normalised_base
                ),
                encoding="utf-8",
            )
            written.append(partial)
    for locale in SUPPORTED_LOCALES:
        grid_partial = output / (
            "partials/skills-grid.html"
            if locale == "en"
            else f"{locale}/partials/skills-grid.html"
        )
        grid_partial.parent.mkdir(parents=True, exist_ok=True)
        grid_partial.write_text(
            _apply_base_path(_skill_grid_fragment(locale), normalised_base),
            encoding="utf-8",
        )
        written.append(grid_partial)
    api_dir = output / "api"
    (api_dir / "raw").mkdir(parents=True, exist_ok=True)
    (api_dir / "skills").mkdir(parents=True, exist_ok=True)
    (api_dir / "skills.json").write_text(catalog_json(), encoding="utf-8")
    (api_dir / "skills" / "search.json").write_text(
        catalog_search_json(), encoding="utf-8"
    )
    written.extend([api_dir / "skills.json", api_dir / "skills" / "search.json"])
    for locale in SUPPORTED_LOCALES:
        if locale == "en":
            continue
        locale_api_dir = output / locale / "api" / "skills"
        locale_api_dir.mkdir(parents=True, exist_ok=True)
        locale_api_json = output / locale / "api" / "skills.json"
        locale_api_json.write_text(catalog_json(locale), encoding="utf-8")
        locale_search_json = locale_api_dir / "search.json"
        locale_search_json.write_text(catalog_search_json(locale), encoding="utf-8")
        written.extend([locale_api_json, locale_search_json])
    for entry in CATALOG:
        raw_path = api_dir / "raw" / f"{entry.slug}.md"
        raw_path.write_text(raw_markdown(entry), encoding="utf-8")
        written.append(raw_path)
        data_path = api_dir / "skills" / f"{entry.slug}.json"
        data_path.write_text(
            json.dumps(entry.public_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        written.append(data_path)
        prompt_dir = api_dir / "skills" / entry.slug
        prompt_dir.mkdir(parents=True, exist_ok=True)
        for prompt_locale in SUPPORTED_LOCALES:
            prompt_path = prompt_dir / (
                "prompts.json"
                if prompt_locale == "en"
                else f"prompts.{prompt_locale}.json"
            )
            prompt_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "locale": prompt_locale,
                        "slug": entry.slug,
                        "raw_url": f"{PUBLIC_SITE_URL}/api/raw/{entry.slug}.md",
                        "scenarios": [
                            scenario.localized(prompt_locale)
                            for scenario in scenarios_for(entry.slug)
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            written.append(prompt_path)
    (output / "static").mkdir()
    (output / "static" / "site.css").write_text(_read_static_css(), encoding="utf-8")
    static_dir = Path(__file__).with_name("static")
    for asset_name in ("site.js", "search.js"):
        (output / "static" / asset_name).write_text(
            (static_dir / asset_name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    favicon_source = Path(__file__).with_name("static") / "favicon.ico"
    shutil.copyfile(favicon_source, output / "favicon.ico")
    (output / "robots.txt").write_text(robots_txt(PUBLIC_SITE_URL), encoding="utf-8")
    (output / "sitemap.xml").write_text(
        sitemap_xml(PUBLIC_SITE_URL, _sitemap_routes()), encoding="utf-8"
    )
    written.extend(
        [
            output / "static" / "site.css",
            output / "static" / "site.js",
            output / "static" / "search.js",
            output / "favicon.ico",
            output / "robots.txt",
            output / "sitemap.xml",
        ]
    )
    return written


def serve(host: str = HOST, port: int = PORT) -> None:
    """Run the local website server until interrupted."""

    class QuietRequestHandler(WSGIRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            print(format % args)

    with make_server(
        host,
        port,
        application,
        server_class=WSGIServer,
        handler_class=QuietRequestHandler,
    ) as httpd:
        print(f"SoulMap website running at http://{host}:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSoulMap website stopped.")


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="soulmap web", description="Run or export the SoulMap public website."
    )
    parser.add_argument("--host", default=HOST, help=f"Bind host (default: {HOST})")
    parser.add_argument(
        "--port", type=int, default=PORT, help=f"Bind port (default: {PORT})"
    )
    parser.add_argument(
        "--export-static",
        action="store_true",
        help="Write static files instead of serving.",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("site"), help="Static output directory."
    )
    parser.add_argument(
        "--base-path",
        default="",
        help="URL path prefix for a GitHub Pages project site.",
    )
    parsed = parser.parse_args(args)
    if parsed.export_static:
        written = export_static(parsed.output, parsed.base_path)
        print(f"Exported {len(written)} static website files to {parsed.output}")
        return 0
    serve(parsed.host, parsed.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
