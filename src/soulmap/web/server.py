"""A small, dependency-free responsive website for SoulMap AI.

The website is separate from the shipped knowledge artifacts at runtime, while the
public catalog exposes curated Skill bundles through explicit raw endpoints.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server
from wsgiref.types import StartResponse

from soulmap.web import config as _config
from soulmap.web import http as _http
from soulmap.web import pages as _page_views
from soulmap.web import routes as _routes
from soulmap.web import skill_views as _skill_views
from soulmap.web.exporter import export_static as _export_static

# Compatibility facade: existing imports remain stable while implementation boundaries
# move into focused modules.
HOST = _config.HOST
PORT = _config.PORT
SITE_NAME = _config.SITE_NAME
RELEASE_URL = _config.RELEASE_URL
REPOSITORY_URL = _config.REPOSITORY_URL
PUBLIC_SITE_URL = _config.PUBLIC_SITE_URL
HTMX_URL = _config.HTMX_URL
ALPINE_URL = _config.ALPINE_URL
INTER_CSS_URL = _config.INTER_CSS_URL
HTMX_SRI = _config.HTMX_SRI
ALPINE_SRI = _config.ALPINE_SRI

_origin = _http._origin
_resource_hints = _http._resource_hints
tr = _http.tr
_nav_path = _http._nav_path
_text = _http._text
_response = _http._response
_normalise_request_path = _http._normalise_request_path

_seo_copy = _page_views._seo_copy
_nav = _page_views._nav
_layout = _page_views._layout
_home = _page_views._home
_how_it_works = _page_views._how_it_works
_boundaries = _page_views._boundaries
_download = _page_views._download
_notes = _page_views._notes
_about = _page_views._about
_faq = _page_views._faq
_privacy = _page_views._privacy
_not_found = _page_views._not_found

_provider_url = _skill_views._provider_url
_render_prompt_scenario = _skill_views._render_prompt_scenario
_skill_detail_fragment = _skill_views._skill_detail_fragment
_skill_cards = _skill_views._skill_cards
_skill_grid_fragment = _skill_views._skill_grid_fragment
_skill_catalog = _skill_views._skill_catalog
_skill_page = _skill_views._skill_page

_read_static_css = _routes._read_static_css
_sitemap_routes = _routes._sitemap_routes
_pages = _routes._pages
_dispatch = _routes.dispatch


def application(
    environ: dict[str, object], start_response: StartResponse
) -> list[bytes]:
    """Serve the public SoulMap website using the WSGI protocol."""
    return _dispatch(environ, start_response)


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
