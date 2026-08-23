"""Localized public page renderers for the SoulMap website."""

from __future__ import annotations

from html import escape

from web.config import (
    ALPINE_SRI,
    ALPINE_URL,
    HTMX_SRI,
    HTMX_URL,
    PUBLIC_SITE_URL,
    RELEASE_URL,
    REPOSITORY_URL,
    SITE_NAME,
)
from web.http import _nav_path, _resource_hints, _text, tr
from web.i18n import SUPPORTED_LOCALES, messages_json
from web.seo import metadata
from web.templates import render_template

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
        f'<details class="faq-item"><summary>{_text(locale, question_key)}<span class="faq-toggle" aria-hidden="true"><svg class="icon" viewBox="0 0 20 20" focusable="false"><path d="M10 3v14M3 10h14"/></svg></span></summary><div class="faq-answer"><p>{_text(locale, answer_key)}</p></div></details>'
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


def _not_found(locale: str) -> str:
    return render_template(
        "pages/not-found.html",
        not_found=_text(locale, "not_found"),
        not_found_body=_text(locale, "not_found_body"),
        home_href=escape(_nav_path("/", locale), quote=True),
        return_home=_text(locale, "return_home"),
    )
