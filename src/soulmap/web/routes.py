"""Ordered route handlers and WSGI dispatcher for the SoulMap website."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.types import StartResponse

from soulmap.web.catalog import (
    CATALOG,
    catalog_json,
    catalog_search_json,
    get_skill,
    locale_fields,
    raw_markdown,
    raw_url,
)
from soulmap.web.catalog import (
    raw_path as localized_raw_path,
)
from soulmap.web.config import PUBLIC_SITE_URL
from soulmap.web.http import _normalise_request_path, _response, _text
from soulmap.web.i18n import SUPPORTED_LOCALES
from soulmap.web.pages import (
    _about,
    _boundaries,
    _download,
    _faq,
    _home,
    _how_it_works,
    _layout,
    _not_found,
    _notes,
    _privacy,
)
from soulmap.web.prompt_pack import scenarios_for
from soulmap.web.seo import robots_txt, sitemap_xml
from soulmap.web.skill_views import (
    _skill_catalog,
    _skill_detail_fragment,
    _skill_grid_fragment,
    _skill_page,
)


def _read_static_css() -> str:
    return (Path(__file__).with_name("static") / "site.css").read_text(encoding="utf-8")


def _sitemap_routes() -> list[str]:
    routes = list(_pages())
    routes.extend(f"/skills/{entry.slug}" for entry in CATALOG)
    return routes


def _pages() -> dict[str, tuple[str, str, Callable[[str], str]]]:
    return {
        "/": ("page_title_home", "page_description_home", _home),
        "/how-it-works": ("page_title_how", "page_description_how", _how_it_works),
        "/boundaries": (
            "page_title_boundaries",
            "page_description_boundaries",
            _boundaries,
        ),
        "/download": (
            "page_title_download",
            "page_description_download",
            _download,
        ),
        "/notes": ("page_title_notes", "page_description_notes", _notes),
        "/about": ("page_title_about", "page_description_about", _about),
        "/faq": ("page_title_faq", "page_description_faq", _faq),
        "/privacy": ("page_title_privacy", "page_description_privacy", _privacy),
        "/skills": ("page_title_skills", "page_description_skills", _skill_catalog),
    }


def dispatch(environ: dict[str, object], start_response: StartResponse) -> list[bytes]:
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
            _text("en", "canonical_english_route").format(location=location),
            [("Location", location), ("Cache-Control", "public, max-age=300")],
        )
    if raw_path == "/private" or raw_path.startswith("/private/"):
        suffix = raw_path.removeprefix("/private") or ""
        location = "/privacy" + suffix + (f"?{raw_query}" if raw_query else "")
        return _response(
            start_response,
            "301 Moved Permanently",
            "text/plain",
            _text("en", "canonical_privacy_route").format(location=location),
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
                    "raw_url": raw_url(entry.slug, prompt_locale),
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
            "raw_path": localized_raw_path(entry.slug, locale),
            "raw_url": raw_url(entry.slug, locale),
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
                start_response,
                "404 Not Found",
                "text/plain",
                _text(locale, "error_skill_not_found_plain"),
            )
        return _response(
            start_response,
            "200 OK",
            "text/markdown",
            raw_markdown(entry, locale),
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
                    _text(locale, "not_found_title"),
                    _text(locale, "not_found_description"),
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
                _text(locale, "page_title_skills"),
                _text(locale, "page_description_skills"),
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
            _layout(
                _text(locale, "not_found_title"),
                _text(locale, "not_found_description"),
                path,
                _not_found(locale),
                locale,
            ),
        )
    title_key, description_key, renderer = pages[path]
    return _response(
        start_response,
        "200 OK",
        "text/html",
        _layout(
            _text(locale, title_key),
            _text(locale, description_key),
            path,
            renderer(locale),
            locale,
        ),
    )
