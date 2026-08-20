"""A small, dependency-free responsive website for SoulMap AI.

The website is separate from the shipped knowledge artifacts at runtime, while the
public catalog exposes curated Skill bundles through explicit raw endpoints.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path
from urllib.parse import parse_qs
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
    _normalise_request_path,
    _response,
    _text,
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
