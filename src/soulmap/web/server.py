"""A small, dependency-free responsive website for SoulMap AI.

The website is separate from the shipped knowledge artifacts at runtime, while the
public catalog exposes curated Skill bundles through explicit raw endpoints.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from html import escape
from pathlib import Path
from urllib.parse import parse_qs, quote
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
from soulmap.web.config import (
    HOST,
    PORT,
    PUBLIC_SITE_URL,
)
from soulmap.web.exporter import export_static as _export_static
from soulmap.web.http import (
    _nav_path,
    _normalise_request_path,
    _response,
    _text,
    tr,
)
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
from soulmap.web.prompt_pack import PromptScenario, scenarios_for
from soulmap.web.seo import robots_txt, sitemap_xml
from soulmap.web.templates import render_template


def _read_static_css() -> str:
    return (Path(__file__).with_name("static") / "site.css").read_text(encoding="utf-8")


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


def export_static(
    output: Path,
    base_path: str = "",
    *,
    incremental: bool = False,
    cache_dir: Path | None = None,
) -> list[Path]:
    """Export public pages through the isolated exporter module."""
    return _export_static(
        output,
        base_path,
        pages_factory=_pages,
        page_layout=_layout,
        skill_page_renderer=_skill_page,
        skill_detail_renderer=_skill_detail_fragment,
        skill_grid_renderer=_skill_grid_fragment,
        static_css_reader=_read_static_css,
        sitemap_routes=_sitemap_routes,
        incremental=incremental,
        cache_dir=cache_dir,
    )


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
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Reuse a verified local export when its source fingerprint is unchanged.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Directory for the incremental manifest (defaults beside --output).",
    )
    parsed = parser.parse_args(args)
    if parsed.export_static:
        written = export_static(
            parsed.output,
            parsed.base_path,
            incremental=parsed.incremental,
            cache_dir=parsed.cache_dir,
        )
        print(f"Exported {len(written)} static website files to {parsed.output}")
        return 0
    serve(parsed.host, parsed.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
