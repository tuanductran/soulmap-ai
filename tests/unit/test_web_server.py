import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast
from urllib.parse import unquote
from wsgiref.types import StartResponse
from wsgiref.util import setup_testing_defaults

import pytest
from werkzeug.test import Client
from werkzeug.wrappers import Response

from soulmap.cli import _command_table
from soulmap.web import server as web_server
from soulmap.web.catalog import CATALOG
from soulmap.web.server import application, export_static


def _request(path: str, query: str = "") -> tuple[dict[str, Any], bytes]:
    environ: dict[str, Any] = {}
    setup_testing_defaults(environ)
    environ["PATH_INFO"] = path
    environ["QUERY_STRING"] = query
    captured: dict[str, Any] = {}

    def capture(
        status: str,
        headers: list[tuple[str, str]],
        *_args: object,
    ) -> Callable[[bytes], object]:
        captured["status"] = status
        captured["headers"] = headers
        return lambda _body: None

    body = b"".join(application(environ, cast(StartResponse, capture)))
    return captured, body


def test_local_font_assets_are_allow_listed_and_cached() -> None:
    headers, body = _request("/static/fonts/InterVariable.woff2")
    assert headers["status"] == "200 OK"
    assert len(body) > 1000
    response_headers = dict(cast(list[tuple[str, str]], headers["headers"]))
    assert response_headers["Content-Type"] == "font/woff2; charset=utf-8"
    assert response_headers["Cache-Control"] == "public, max-age=31536000, immutable"

    missing_headers, _ = _request("/static/fonts/unknown.woff2")
    assert missing_headers["status"] == "404 Not Found"


def test_werkzeug_client_exercises_json_route() -> None:
    response = Client(application, Response).get(
        "/api/skills/search.json?q=bu%C3%B2n&limit=6"
    )

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    payload = response.get_json()
    assert isinstance(payload, dict)
    assert payload["locale"] == "en"
    assert isinstance(payload["results"], list)


@pytest.mark.parametrize(
    ("path", "status"),
    [
        ("/", "200 OK"),
        ("/en", "301 Moved Permanently"),
        ("/vi", "200 OK"),
        ("/ko", "200 OK"),
        ("/how-it-works", "200 OK"),
        ("/boundaries", "200 OK"),
        ("/download", "200 OK"),
        ("/notes", "200 OK"),
        ("/about", "200 OK"),
        ("/faq", "200 OK"),
        ("/privacy", "200 OK"),
        ("/vi/faq", "200 OK"),
        ("/vi/privacy", "200 OK"),
        ("/ko/faq", "200 OK"),
        ("/ko/privacy", "200 OK"),
        ("/private", "301 Moved Permanently"),
        ("/skills", "200 OK"),
        ("/skills/meta", "200 OK"),
        ("/static/site.css", "200 OK"),
        ("/static/site.js", "200 OK"),
        ("/static/search.js", "200 OK"),
        ("/favicon.ico", "200 OK"),
        ("/sitemap.xml", "200 OK"),
        ("/api/skills.json", "200 OK"),
        ("/api/skills/search.json", "200 OK"),
        ("/vi/api/skills/search.json", "200 OK"),
        ("/ko/api/skills/search.json", "200 OK"),
        ("/api/skills/meta/prompts.json", "200 OK"),
        ("/api/skills/meta/prompts.vi.json", "200 OK"),
        ("/api/skills/meta/prompts.ko.json", "200 OK"),
        ("/api/raw/meta.md", "200 OK"),
        ("/partials/skill/not-real.en.html", "404 Not Found"),
        ("/partials/skill/not-real.vi.html", "404 Not Found"),
        ("/partials/skill/not-real.ko.html", "404 Not Found"),
        ("/missing", "404 Not Found"),
    ],
)
def test_public_website_routes(path: str, status: str) -> None:
    captured, body = _request(path)

    assert captured["status"] == status
    assert body
    headers = dict(cast(list[tuple[str, str]], captured["headers"]))
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert (
        "script-src 'self' https://cdn.jsdelivr.net"
        in headers["Content-Security-Policy"]
    )
    assert headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"


def test_english_prefixed_routes_redirect_to_canonical_root() -> None:
    captured, body = _request("/en/how-it-works", "q=mirror")
    assert captured["status"] == "301 Moved Permanently"
    headers = dict(cast(list[tuple[str, str]], captured["headers"]))
    assert headers["Location"] == "/how-it-works?q=mirror"
    assert body.decode("utf-8") == "Canonical English route: /how-it-works?q=mirror\n"


def test_seo_metadata_is_absolute_localized_and_server_rendered() -> None:
    _, english_body = _request("/how-it-works")
    english = english_body.decode("utf-8")
    assert (
        '<link rel="canonical" href="https://tuanductran.github.io/soulmap-ai/how-it-works/">'
        in english
    )
    assert (
        'hreflang="en" href="https://tuanductran.github.io/soulmap-ai/how-it-works/"'
        in english
    )
    assert (
        'hreflang="vi" href="https://tuanductran.github.io/soulmap-ai/vi/how-it-works/"'
        in english
    )
    assert (
        'hreflang="x-default" href="https://tuanductran.github.io/soulmap-ai/how-it-works/"'
        in english
    )
    assert 'property="og:type" content="website"' in english
    assert 'name="twitter:card" content="summary"' in english
    assert '<script type="application/ld+json">' in english
    assert '"@type":"Organization"' in english
    assert '"@type":"WebPage"' in english

    _, vietnamese_body = _request("/vi/how-it-works")
    vietnamese = vietnamese_body.decode("utf-8")
    assert '<html lang="vi">' in vietnamese
    assert (
        '<link rel="canonical" href="https://tuanductran.github.io/soulmap-ai/vi/how-it-works/">'
        in vietnamese
    )
    assert (
        'hreflang="en" href="https://tuanductran.github.io/soulmap-ai/how-it-works/"'
        in vietnamese
    )
    assert (
        'hreflang="vi" href="https://tuanductran.github.io/soulmap-ai/vi/how-it-works/"'
        in vietnamese
    )
    assert '"inLanguage":"vi"' in vietnamese

    _, korean_body = _request("/ko/how-it-works")
    korean = korean_body.decode("utf-8")
    assert '<html lang="ko">' in korean
    assert (
        '<link rel="canonical" href="https://tuanductran.github.io/soulmap-ai/ko/how-it-works/">'
        in korean
    )
    assert (
        'hreflang="ko" href="https://tuanductran.github.io/soulmap-ai/ko/how-it-works/"'
        in korean
    )
    assert '"inLanguage":"ko"' in korean


def test_language_dropdown_exposes_all_locales_and_current_state() -> None:
    _, body = _request("/ko/faq")
    html = body.decode("utf-8")
    assert 'x-data="languageMenu"' in html
    assert 'x-on:click="toggle($event)"' in html
    assert 'x-on:keydown="onKeydown($event)"' in html
    assert 'x-transition:enter="dropdown-enter"' in html
    assert 'x-transition:leave="dropdown-leave"' in html
    assert 'aria-haspopup="menu"' in html
    assert 'aria-controls="language-menu"' in html
    assert 'id="language-menu"' in html
    assert 'role="menu"' in html
    assert 'role="menuitem" href="/faq" lang="en"' in html
    assert 'role="menuitem" href="/vi/faq" lang="vi"' in html
    assert 'role="menuitem" href="/ko/faq" lang="ko" aria-current="page"' in html
    assert '<svg class="icon icon-mark" viewBox="0 0 24 24"' in html
    assert '<svg class="icon locale-chevron" viewBox="0 0 16 16"' in html
    assert 'class="faq-toggle" aria-hidden="true"' in html
    assert html.index('<div class="locale-switcher"') < html.index(
        '<nav class="nav-links"'
    )
    assert html.index('class="nav-links-shell"') < html.index('<nav class="nav-links"')
    assert html.index('<nav class="nav-links"') < html.index("</nav>")
    assert 'x-data="navScroll"' in html
    assert 'x-bind:data-scroll-left="canScrollLeft"' in html
    assert 'x-bind:data-scroll-right="canScrollRight"' in html
    assert "한국어" in html


def test_sitemap_and_robots_reference_only_public_canonical_urls() -> None:
    sitemap_captured, sitemap_body = _request("/sitemap.xml")
    sitemap = sitemap_body.decode("utf-8")
    assert sitemap_captured["status"] == "200 OK"
    assert 'xmlns:xhtml="http://www.w3.org/1999/xhtml"' in sitemap
    assert "https://tuanductran.github.io/soulmap-ai/faq/" in sitemap
    assert "https://tuanductran.github.io/soulmap-ai/vi/privacy/" in sitemap
    assert "https://tuanductran.github.io/soulmap-ai/ko/privacy/" in sitemap
    assert "https://tuanductran.github.io/soulmap-ai/en/" not in sitemap
    assert "https://tuanductran.github.io/soulmap-ai/api/" not in sitemap
    assert sitemap.count('hreflang="x-default"') >= 2

    robots_captured, robots_body = _request("/robots.txt")
    robots = robots_body.decode("utf-8")
    assert robots_captured["status"] == "200 OK"
    assert "User-agent: *" in robots
    assert "Allow: /" in robots
    assert "Sitemap: https://tuanductran.github.io/soulmap-ai/sitemap.xml" in robots


def test_faq_and_privacy_pages_use_public_i18n_content() -> None:
    _, faq_body = _request("/faq")
    faq = faq_body.decode("utf-8")
    assert faq.count('<details class="faq-item">') == 6
    assert faq.count("<summary>") == 6
    visible_faq = faq.split('<main id="main-content">', 1)[1].split("</main>", 1)[0]
    assert "faq_q_1" not in visible_faq
    assert "src/soulmap" not in visible_faq
    assert '<script id="soulmap-locale-data" type="application/json">' in faq

    _, privacy_body = _request("/vi/privacy")
    privacy = privacy_body.decode("utf-8")
    assert '<html lang="vi">' in privacy
    assert "Thông báo này áp dụng cho những gì" in privacy
    assert "Trang web hiện không có tạo tài khoản" in privacy
    assert privacy.count('<h2 class="card-title">') == 6


def test_private_alias_redirects_to_canonical_privacy_route() -> None:
    captured, body = _request("/private", "from=legacy")
    assert captured["status"] == "301 Moved Permanently"
    headers = dict(cast(list[tuple[str, str]], captured["headers"]))
    assert headers["Location"] == "/privacy?from=legacy"
    assert body.decode("utf-8") == "Canonical privacy route: /privacy?from=legacy\n"


def test_favicon_route_returns_original_ico_bytes() -> None:
    captured, body = _request("/favicon.ico")
    assert captured["status"] == "200 OK"
    headers = dict(cast(list[tuple[str, str]], captured["headers"]))
    assert headers["Content-Type"] == "image/x-icon; charset=utf-8"
    assert body[:4] == b"\x00\x00\x01\x00"
    assert len(body) > 1000


def test_localized_shared_accessible_labels_are_not_hardcoded() -> None:
    _, body = _request("/vi")
    html = body.decode("utf-8")
    _, en_body = _request("/")
    en_html = en_body.decode("utf-8")

    assert 'aria-label="SoulMap AI home"' in en_html
    assert 'aria-label="Primary navigation"' in en_html
    assert "<cite>SoulMap principle</cite>" in en_html
    assert 'aria-label="Trang chủ SoulMap AI"' in html
    assert 'aria-label="Điều hướng chính"' in html
    assert (
        '<div class="mirror-card" role="note" aria-label="Nguyên tắc SoulMap">' in html
    )
    assert "<cite>Nguyên tắc SoulMap</cite>" in html
    assert "SoulMap principle" not in html
    assert "Primary navigation" not in html


def test_website_is_responsive_accessible_and_progressive() -> None:
    captured, body = _request("/static/site.css")

    assert captured["status"] == "200 OK"
    css = body.decode("utf-8")
    assert "@media (max-width: 640px)" in css
    assert "--gold: #8a681f" in css
    assert "--muted: #5d6b70" in css
    assert "--radius-hero: 32px" in css
    assert "--radius-hero-inner" not in css
    assert "border-radius: 24px 34px 24px 34px" in css
    assert "border-radius: 40% 40% 34% 34% / 34% 34% 42% 42%" not in css
    assert "#c99b50" not in css
    assert "prefers-reduced-motion" in css
    assert "select:focus-visible" in css
    assert "textarea:focus-visible" in css
    assert re.search(
        r"button,\s*input,\s*select,\s*textarea\s*\{\s*font:\s*inherit;\s*\}",
        css,
    )
    assert "font-korean" not in css
    assert '--font-sans: "Inter", ui-sans-serif, system-ui' in css
    assert 'font-family: "Manrope"' in css
    assert "a { color: inherit; text-decoration: none; }" not in css
    assert re.search(r"a\s*\{\s*color:\s*inherit;\s*text-decoration:\s*none;\s*\}", css)
    assert ".nav-topline" in css
    assert ".nav-links-shell::before" in css
    assert '.nav-links-shell[data-scroll-left="true"]::before' in css
    assert '.nav-links-shell[data-scroll-right="true"]::after' in css
    assert "prefers-color-scheme: dark" in css
    assert "prefers-reduced-transparency" in css
    assert "safe-area-inset" in css
    assert ":focus-visible" in css
    assert "min-height: 44px" in css
    assert re.search(r"body\.modal-open\s*\{\s*overflow:\s*hidden;\s*\}", css)
    assert ".modal-dialog" in css
    assert ".skill-grid" in css
    assert ".mode-switch" in css
    assert ".mode-option input:checked + span" in css
    assert ".mode-panel" in css
    assert ".question-card__scenario" in css
    assert ".faq-item" in css
    assert ".privacy-grid" in css


def test_layout_uses_local_fonts_and_pinned_script_assets() -> None:
    _, body = _request("/skills")
    html = body.decode("utf-8")

    assert "rsms.me/inter" not in html
    assert '<link rel="preconnect" href="https://cdn.jsdelivr.net/">' in html
    assert '<link rel="dns-prefetch" href="https://cdn.jsdelivr.net/">' in html
    assert 'rel="preload"' not in html
    assert html.count('rel="preconnect"') == 1
    assert html.count('rel="dns-prefetch"') == 1
    assert 'rel="icon" href="/favicon.ico" sizes="any"' in html
    assert 'aria-label="SoulMap AI home"' in html
    assert 'aria-label="Primary navigation"' in html
    assert "<title>Choose the layer that fits the moment. · SoulMap AI</title>" in html
    assert "SoulMap AI · SoulMap AI" not in html
    assert 'name="htmx-config"' in html
    assert "includeIndicatorStyles" in html
    assert 'src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"' in html
    assert (
        'src="https://cdn.jsdelivr.net/npm/@alpinejs/csp@3.16.2/dist/cdn.min.js"'
        in html
    )
    assert html.count('integrity="sha384-') == 2
    assert 'src="/static/search.js"' in html
    assert 'src="/static/site.js"' in html
    assert 'id="page-shell"' in html
    assert "hx-boost" not in html
    assert "hx-history-elt" not in html
    assert 'hx-swap="innerHTML transition:true show:top"' not in html
    search_form_attributes = html.split('<form class="field search-form"', 1)[1].split(
        ">", 1
    )[0]
    assert "hx-boost" not in search_form_attributes
    assert "page-progress" not in html
    site_css = _request("/static/site.css")[1].decode("utf-8")
    assert 'url("/static/fonts/InterVariable.woff2")' in site_css
    assert ".page-progress" not in site_css
    assert ".htmx-swapping #main-content" not in site_css
    _, search_body = _request("/static/search.js")
    search_js = search_body.decode("utf-8")
    assert "SoulMapSearch" in search_js
    _, js_body = _request("/static/site.js")
    js = js_body.decode("utf-8")
    assert 'body.classList.add("modal-open")' in js
    assert 'body.classList.remove("modal-open")' in js
    assert "preventScroll: true" in js
    assert 'window.htmx.ajax("GET", detailUrl' in js
    assert "copyFailed: false" in js
    assert "this.copyFailed = !success" in js
    assert 'data-detail-url="/partials/skill/meta.en.html?lang=en"' in html
    assert "x-on:click.prevent=\"open('meta'," in html
    assert 'hx-get="/partials/skill/meta.en.html?lang=en"' not in html
    assert 'hx-get="/partials/skills-grid.html?lang=en"' not in html
    assert 'method="get"' in html
    assert 'x-on:submit="preventSubmit($event)"' in html
    assert 'data-skill-root="/skills"' in html
    assert 'class="section tinted catalog-section"' in html
    assert 'class="modal-close"' in html
    _, modal_body = _request("/partials/skill/meta.en.html", query="lang=en")
    modal_html = modal_body.decode("utf-8")
    assert 'class="icon provider-icon"' in modal_html
    assert 'data-search-api="/api/skills/search.json"' in html
    assert 'data-search-error="Search is temporarily unavailable.' in html
    assert 'aria-controls="search-panel ask-panel"' in html
    assert 'data-search-locale="en"' in html
    assert 'data-search-query-label="Search the Skill catalog"' in html
    assert 'data-ask-query-label="Describe what you want to ask"' in html
    assert 'value="search"' in html and 'value="ask"' in html
    assert 'id="search-panel"' in html
    assert 'id="ask-panel"' in html
    assert 'aria-labelledby="search-panel-title"' in html
    assert 'aria-labelledby="ask-panel-title"' in html
    assert 'x-model="mode"' in html
    assert 'id="question-results"' in html
    assert 'enterkeyhint="search"' in html
    assert "Search only changes the Skill list below" in html
    assert (
        "Find the layer that matches your words, then open its details or raw bundle."
        not in html
    )
    assert "Choose an existing Skill scenario as a grounded starting point." not in html
    assert 'aria-haspopup="dialog"' in html
    assert 'aria-controls="skill-modal"' in html
    assert 'id="skill-modal"' in html
    assert 'id="skill-loading"' in html
    assert 'id="provider-chooser"' in html
    assert 'id="provider-chooser-dialog"' in html
    assert 'role="status"' in html
    assert "x-cloak" in html
    assert 'x-transition:enter="modal-shell-enter"' in html
    assert 'x-transition:leave="modal-shell-leave"' in html
    assert 'x-if="openSlug"' in html
    assert 'x-if="providerOpen"' in html
    assert 'x-transition:enter="modal-dialog-enter"' not in html
    assert 'x-transition:leave="modal-dialog-leave"' not in html
    assert 'rel="canonical"' in html
    assert 'hreflang="x-default"' in html
    assert "application/ld+json" in html

    _, fragment_body = _request("/partials/skill/meta.en.html")
    fragment = fragment_body.decode("utf-8")
    assert 'aria-live="polite"' in fragment
    assert 'x-show="!copied && !copyFailed"' in fragment
    assert 'x-show="copied"' in fragment
    assert 'x-show="copyFailed"' in fragment
    assert "copy_failed" not in fragment
    assert "x-transition.opacity.duration.150ms" in fragment


def test_htmx_skill_filter_returns_fragment_and_full_page_fallback() -> None:
    captured, fragment_body = _request(
        "/partials/skills-grid.html", "lang=en&q=spiritual"
    )
    fragment = fragment_body.decode("utf-8")
    assert captured["status"] == "200 OK"
    assert '<div class="skill-grid" id="skill-grid"' in fragment
    assert "Grounded symbolic layer" in fragment
    assert "Core orchestration" not in fragment
    assert "Reflective frameworks" not in fragment

    full_captured, full_body = _request("/skills", "q=spiritual")
    full_page = full_body.decode("utf-8")
    assert full_captured["status"] == "200 OK"
    assert 'name="q"' in full_page
    assert 'value="spiritual"' in full_page
    assert "Grounded symbolic layer" in full_page
    assert "Core orchestration" not in full_page


def test_api_error_and_fallback_routes_are_deterministic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invalid_limit_headers, invalid_limit_body = _request(
        "/api/skills/search.json", "q=spiritual&limit=not-a-number"
    )
    invalid_limit = json.loads(invalid_limit_body)
    assert invalid_limit_headers["status"] == "200 OK"
    assert invalid_limit["limit"] == 50

    monkeypatch.setattr("soulmap.web.routes.read_text_asset", lambda _name: None)
    missing_asset_headers, _ = _request("/static/site.js")
    assert missing_asset_headers["status"] == "404 Not Found"

    for path in (
        "/api/skills/not-real.json",
        "/api/skills/not-real/prompts.json",
        "/api/skills/meta/prompts.fr.json",
        "/api/skills/meta/prompts-broken.json",
    ):
        headers, body = _request(path)
        assert headers["status"] == "404 Not Found"
        assert json.loads(body)["error"] == "skill_not_found"

    raw_headers, raw_body = _request("/api/raw/not-real.md")
    assert raw_headers["status"] == "404 Not Found"
    assert "not found" in raw_body.decode("utf-8").lower()

    partial_headers, partial_body = _request("/partials/skill/meta.fr.html")
    assert partial_headers["status"] == "200 OK"
    assert "Core orchestration" in partial_body.decode("utf-8")

    fallback_partial_headers, fallback_partial_body = _request(
        "/partials/skill/meta.html"
    )
    assert fallback_partial_headers["status"] == "200 OK"
    assert "Core orchestration" in fallback_partial_body.decode("utf-8")

    skill_headers, skill_body = _request("/skills/not-real")
    assert skill_headers["status"] == "404 Not Found"
    assert "not found" in skill_body.decode("utf-8").lower()

    skill_json_headers, skill_json_body = _request("/api/skills/meta.json")
    skill_json = json.loads(skill_json_body)
    assert skill_json_headers["status"] == "200 OK"
    assert skill_json["slug"] == "meta"
    assert skill_json["raw_url"].endswith("/api/raw/meta.md")


def test_advanced_skill_search_api_localizes_ranks_filters_and_limits() -> None:
    captured, body = _request("/api/skills/search.json", "q=spiritual&limit=1")
    payload = json.loads(body)
    assert captured["status"] == "200 OK"
    assert payload["version"] == 1
    assert payload["locale"] == "en"
    assert payload["query"] == "spiritual"
    assert payload["total"] == 1
    assert payload["results"][0]["slug"] == "spiritual"
    assert payload["results"][0]["score"] > 0
    assert "summary" in payload["results"][0]

    vi_captured, vi_body = _request(
        "/vi/api/skills/search.json", "q=khung&group=Phản chiếu"
    )
    vi_payload = json.loads(vi_body)
    assert vi_captured["status"] == "200 OK"
    assert vi_payload["locale"] == "vi"
    assert vi_payload["results"][0]["slug"] == "frameworks"
    assert vi_payload["results"][0]["group"] == "Phản chiếu"

    ko_payload = json.loads(_request("/ko/api/skills/search.json")[1])
    assert ko_payload["locale"] == "ko"
    assert ko_payload["results"]

    ko_prompt = json.loads(_request("/api/skills/meta/prompts.ko.json")[1])
    assert ko_prompt["locale"] == "ko"
    assert ko_prompt["scenarios"]

    group_body = _request("/api/skills/search.json", "group=Safety")[1]
    group_payload = json.loads(group_body)
    assert [result["slug"] for result in group_payload["results"]] == ["safety"]


def test_server_main_export_and_serve_modes_forward_arguments(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    exported: dict[str, object] = {}

    def fake_export(
        output: Path,
        base_path: str = "",
        *,
        incremental: bool = False,
        cache_dir: Path | None = None,
    ) -> list[Path]:
        exported.update(
            output=output,
            base_path=base_path,
            incremental=incremental,
            cache_dir=cache_dir,
        )
        return [output / "index.html"]

    monkeypatch.setattr(web_server, "export_static", fake_export)
    assert (
        web_server.main(
            [
                "--export-static",
                "--output",
                str(tmp_path / "site"),
                "--base-path",
                "/soulmap-ai",
                "--incremental",
                "--cache-dir",
                str(tmp_path / "cache"),
            ]
        )
        == 0
    )
    assert exported == {
        "output": tmp_path / "site",
        "base_path": "/soulmap-ai",
        "incremental": True,
        "cache_dir": tmp_path / "cache",
    }

    served: dict[str, object] = {}
    monkeypatch.setattr(
        web_server,
        "serve",
        lambda host, port: served.update(host=host, port=port),
    )
    assert web_server.main(["--host", "127.0.0.1", "--port", "4321"]) == 0
    assert served == {"host": "127.0.0.1", "port": 4321}


def test_server_serve_mode_handles_shutdown_and_quiet_logging(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    class FakeServer:
        def __enter__(self) -> "FakeServer":
            return self

        def __exit__(self, *_args: object) -> None:
            captured["closed"] = True

        def serve_forever(self) -> None:
            raise KeyboardInterrupt

    def fake_make_server(*args: object, **kwargs: object) -> FakeServer:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return FakeServer()

    monkeypatch.setattr(web_server, "make_server", fake_make_server)
    web_server.serve("127.0.0.1", 4321)

    assert captured["args"][:2] == ("127.0.0.1", 4321)
    assert captured["closed"] is True
    handler_class = captured["kwargs"]["handler_class"]
    handler_class.log_message(object(), "%s", "request")


def test_ask_mode_uses_json_scenarios_and_safe_dom_rendering() -> None:
    _, html_body = _request("/vi/skills")
    html = html_body.decode("utf-8")
    assert '<p class="ask-intro">Chế độ Hỏi giúp bạn chọn một Skill công khai' in html
    assert 'data-ask-result-label="Câu hỏi mở đầu"' in html
    assert 'data-ask-use-label="Dùng câu hỏi này"' in html
    assert (
        'data-provider-source-instruction="Hãy đọc gói Skill SoulMap công khai trước khi phản hồi:'
        in html
    )
    assert 'id="question-results"' in html
    assert 'id="provider-chooser"' in html
    assert 'id="provider-chooser-dialog"' in html
    assert 'x-text="providerQuestion"' in html

    _, search_body = _request("/static/search.js")
    search_js = search_body.decode("utf-8")
    assert "prompt_scenarios" in search_js
    assert "document" not in search_js
    assert "innerHTML" not in search_js

    _, site_body = _request("/static/site.js")
    site_js = site_body.decode("utf-8")
    assert "renderAskResults" in site_js
    assert "renderSearchError" in site_js
    assert "providerUrl" in site_js
    assert "closeProviderChooser" in site_js
    assert "input.value = question" not in site_js
    assert 'role", "alert"' in site_js
    assert "document.createElement" in site_js
    assert "innerHTML" not in site_js

    payload = json.loads(_request("/vi/api/skills/search.json")[1])
    assert any(result["prompt_scenarios"] for result in payload["results"])
    assert all(
        "answer" not in scenario
        for result in payload["results"]
        for scenario in result["prompt_scenarios"]
    )


def test_skill_catalog_blocks_enter_navigation_and_exposes_static_search_api() -> None:
    _, body = _request("/vi/skills")
    html = body.decode("utf-8")
    assert 'action="/vi/skills"' in html
    assert 'data-search-api="/vi/api/skills/search.json"' in html
    assert 'data-search-error="Tìm kiếm tạm thời không khả dụng.' in html
    assert "Chi tiết Skill SoulMap" in html
    assert 'data-search-locale="vi"' in html
    assert 'data-search-query-label="Tìm trong danh mục Skills"' in html
    assert 'data-ask-query-label="Mô tả điều bạn muốn hỏi"' in html
    assert 'value="ask"' in html
    assert 'id="search-panel"' in html
    assert 'id="ask-panel"' in html
    assert (
        'data-ask-query-hint="Hỏi chỉ khớp với các kịch bản công khai; không tự tạo câu trả lời."'
        in html
    )
    assert 'data-skill-root="/vi/skills"' in html
    assert 'id="question-results"' in html

    _, search_body = _request("/static/search.js")
    search_js = search_body.decode("utf-8")
    assert "SoulMapSearch" in search_js
    assert "MAX_QUESTION_RESULTS = 6" in search_js

    _, js_body = _request("/static/site.js")
    js = js_body.decode("utf-8")
    assert "preventSubmit(event)" in js
    assert "event.preventDefault();" in js
    assert "window.SoulMapSearch" in js
    assert "question-card__scenario" in js
    assert 'Alpine.data("languageMenu"' in js
    assert "result.scenario.when" not in js
    assert 'credentials: "same-origin"' in js


def test_skill_fragment_exposes_provider_handoffs_in_both_locales() -> None:
    _, english_body = _request("/partials/skill/meta.en.html")
    english = english_body.decode("utf-8")
    _, vietnamese_body = _request("/partials/skill/meta.vi.html")
    vietnamese = vietnamese_body.decode("utf-8")

    for (
        html,
        labels,
        heading,
        prompt_label,
        source_label,
        question_label,
        expected_raw_url,
    ) in (
        (
            english,
            ("Open in ChatGPT", "Open in Claude", "Open in Claude Code"),
            "Choose a context-specific prompt",
            "Prompt",
            "Source Skill bundle",
            "Starter question",
            "https://tuanductran.github.io/soulmap-ai/api/raw/meta.md",
        ),
        (
            vietnamese,
            ("Mở trong ChatGPT", "Mở trong Claude", "Mở trong Claude Code"),
            "Chọn prompt theo bối cảnh",
            "Prompt",
            "Gói Skill nguồn",
            "Câu hỏi bắt đầu",
            "https://tuanductran.github.io/soulmap-ai/vi/api/raw/meta.md",
        ),
    ):
        assert heading in html
        assert html.count(prompt_label) >= 3
        assert html.count(source_label) >= 3
        assert html.count(question_label) >= 3
        assert html.count(expected_raw_url) >= 3
        assert "https://chatgpt.com/?q=" in html
        assert "https://claude.ai/new?q=" in html
        assert "claude-cli://open?q=" in html
        assert "Provider links may require sign-in" not in html
        assert "Use this public SoulMap Markdown bundle" not in html
        for label in labels:
            assert label in html

    decoded_english = unquote(english)
    decoded_vietnamese = unquote(vietnamese)
    assert "Read the public SoulMap Skill bundle before responding:" in decoded_english
    assert "Starter question:" in decoded_english
    assert (
        "Hãy đọc gói Skill SoulMap công khai trước khi phản hồi:" in decoded_vietnamese
    )
    assert "Câu hỏi bắt đầu:" in decoded_vietnamese
    assert (
        "Read the public SoulMap Skill bundle before responding:"
        not in decoded_vietnamese
    )
    assert "Starter question:" not in decoded_vietnamese

    _, voice_body = _request("/partials/skill/voice.vi.html")
    voice = voice_body.decode("utf-8")
    assert "không dùng biểu tượng cảm xúc" in voice
    assert "không dùng emoji" not in voice


def test_unknown_skill_partials_return_localized_not_found_errors() -> None:
    captured_en, body_en = _request("/partials/skill/not-real.en.html")
    captured_vi, body_vi = _request("/partials/skill/not-real.vi.html")

    assert captured_en["status"] == "404 Not Found"
    assert captured_vi["status"] == "404 Not Found"
    assert "Skill not found." in body_en.decode("utf-8")
    assert "Không tìm thấy Skill." in body_vi.decode("utf-8")
    assert (
        dict(cast(list[tuple[str, str]], captured_en["headers"]))["Cache-Control"]
        == "no-store"
    )


@pytest.mark.parametrize("slug", [entry.slug for entry in CATALOG])
def test_every_skill_fragment_has_context_prompt_source_and_provider_links(
    slug: str,
) -> None:
    _, body = _request(f"/partials/skill/{slug}.en.html")
    html = body.decode("utf-8")

    assert html.count('class="prompt-scenario"') == 3
    assert html.count('class="prompt-scenario__prompt"') == 3
    assert html.count('class="prompt-scenario__source"') == 3
    assert html.count('class="prompt-scenario__question"') == 3
    assert html.count("https://tuanductran.github.io/soulmap-ai/api/raw/") >= 3
    assert html.count("https://chatgpt.com/?q=") == 3
    assert html.count("https://claude.ai/new?q=") == 3
    assert html.count("claude-cli://open?q=") == 3
    assert "Provider links may require sign-in" not in html


def test_catalog_api_and_raw_bundle_are_public_and_complete() -> None:
    _, catalog_body = _request("/api/skills.json")
    catalog = catalog_body.decode("utf-8")
    assert '"slug": "meta"' in catalog
    assert '"slug": "frameworks"' in catalog
    assert '"raw_path": "/api/raw/meta.md"' in catalog
    assert (
        '"raw_url": "https://tuanductran.github.io/soulmap-ai/api/raw/meta.md"'
        in catalog
    )
    assert '"prompt_scenarios": [' in catalog

    _, prompts_body = _request("/api/skills/meta/prompts.json")
    prompts = json.loads(prompts_body.decode("utf-8"))
    assert prompts["locale"] == "en"
    assert prompts["raw_url"].endswith("/api/raw/meta.md")
    assert len(prompts["scenarios"]) == 3
    assert all(item["prompt"] and item["question"] for item in prompts["scenarios"])

    _, vi_prompts_body = _request("/api/skills/meta/prompts.vi.json")
    vi_prompts = json.loads(vi_prompts_body.decode("utf-8"))
    assert vi_prompts["locale"] == "vi"
    assert vi_prompts["raw_url"].endswith("/vi/api/raw/meta.md")
    assert "Bắt đầu một phiên phản chiếu" in vi_prompts["scenarios"][0]["title"]

    _, vi_catalog_body = _request("/api/skills.json", "lang=vi")
    vi_catalog = vi_catalog_body.decode("utf-8")
    assert '"locale": "vi"' in vi_catalog
    assert "Điều phối cốt lõi" in vi_catalog
    assert '"raw_path": "/vi/api/raw/meta.md"' in vi_catalog

    _, raw_body = _request("/api/raw/meta.md")
    raw = raw_body.decode("utf-8")
    assert "# SoulMap Skill bundle: Core orchestration" in raw
    assert "execution-pipeline.md" in raw
    assert "## Suggested prompts by context" in raw
    assert "**Prompt:**" in raw
    assert (
        "**Source Skill bundle:** https://tuanductran.github.io/soulmap-ai/api/raw/meta.md"
        in raw
    )
    assert "**Starter question:**" in raw
    assert "AGENTS.md" not in raw

    _, vi_raw_body = _request("/api/raw/meta.md", "lang=vi")
    vi_raw = vi_raw_body.decode("utf-8")
    assert "# Gói Skill SoulMap: Điều phối cốt lõi" in vi_raw
    assert (
        "**Gói Skill nguồn:** https://tuanductran.github.io/soulmap-ai/vi/api/raw/meta.md"
        in vi_raw
    )
    assert (
        "**Gói Skill nguồn:** https://tuanductran.github.io/soulmap-ai/api/raw/meta.md"
        not in vi_raw
    )
    assert "SoulMap behavioral contract" in raw
    for forbidden in (".claude/", "src/", "tests/", "pyproject.toml", "uv.lock"):
        assert forbidden not in raw


def test_localized_catalog_uses_requested_language() -> None:
    _, body = _request("/skills", "lang=vi")
    html = body.decode("utf-8")
    assert '<html lang="vi">' in html
    assert "Chọn lớp phù hợp với khoảnh khắc này." in html
    locale_payload = html.split(
        '<script id="soulmap-locale-data" type="application/json">', 1
    )[1].split("</script>", 1)[0]
    locale_messages = json.loads(locale_payload)
    assert locale_messages["home_skills"] == "Khám phá các Skills"
    assert locale_messages["privacy_page"] == "Quyền riêng tư"
    assert "raw_heading" not in locale_messages
    assert (
        locale_messages["raw_note"]
        == "URL này trả về một gói Markdown hoàn chỉnh cho nhóm Skill này."
    )
    visible_main = html.split('<main id="main-content">', 1)[1].split("</main>", 1)[0]
    assert "Khám phá các Skills" not in visible_main
    assert "inner work" not in visible_main
    assert "authority" not in visible_main
    assert "privacy" not in visible_main.lower()
    assert "Phản chiếu" in visible_main
    assert "Reflection" not in visible_main
    assert "6 nhóm · có bundle Markdown gốc" not in visible_main
    assert "groups · raw bundles available" not in visible_main
    assert (
        "Tìm lớp phù hợp với điều bạn viết, rồi mở chi tiết hoặc bundle gốc."
        not in visible_main
    )
    assert (
        "Chọn một kịch bản Skill có sẵn làm điểm bắt đầu có nền tảng."
        not in visible_main
    )
    search_heading = visible_main.split('<div class="mode-panel__heading">', 1)[
        1
    ].split("</div>", 1)[0]
    assert search_heading.count("<p") == 0
    assert '<p class="muted">' not in search_heading
    assert "Tìm trong danh mục Skills" in visible_main
    assert "Mô tả điều bạn muốn hỏi" in visible_main
    assert "Chọn một câu hỏi để bắt đầu" in visible_main
    assert "Choose a question to begin" not in visible_main

    _, notes_body = _request("/vi/notes")
    notes = notes_body.decode("utf-8")
    assert "Tự nhận ra" in notes
    assert "Thành thật trong quan hệ" in notes
    assert "Thực hành nội tâm có nền tảng" in notes
    assert "Grounded inner work" not in notes

    _, body = _request("/vi/skills")
    assert '<html lang="vi">' in body.decode("utf-8")


def test_download_page_uses_public_artifact_language() -> None:
    _, body = _request("/download")
    html = body.decode("utf-8")
    main = html.split('<main id="main-content">', 1)[1].split("</main>", 1)[0]

    for internal_path in ("src/", "tests/", ".claude/", "dist/"):
        assert internal_path not in main
    assert ".skill" in main
    assert ".zip" in main


def test_secondary_page_card_headings_are_sequential() -> None:
    for path in ("/how-it-works", "/boundaries", "/download", "/notes", "/skills"):
        _, body = _request(path)
        html = body.decode("utf-8")
        assert len(re.findall(r"<h1(?:\s[^>]*)?>", html)) == 1
        assert "<h3>" not in html
        assert "<h2" in html


def test_web_command_is_public_cli_surface() -> None:
    assert "web" in _command_table()


def test_static_export_writes_localized_pages_and_api(tmp_path: Path) -> None:
    output = tmp_path / "site"
    written = export_static(output, "/soulmap-ai")

    assert len(written) > 50
    expected = (
        "index.html",
        "vi/index.html",
        "ko/index.html",
        "faq/index.html",
        "privacy/index.html",
        "vi/faq/index.html",
        "vi/privacy/index.html",
        "ko/faq/index.html",
        "ko/privacy/index.html",
        "skills/index.html",
        "privacy/index.html",
        "vi/faq/index.html",
        "vi/privacy/index.html",
        "skills/index.html",
        "vi/skills/index.html",
        "ko/skills/index.html",
        "skills/meta/index.html",
        "vi/skills/meta/index.html",
        "ko/skills/meta/index.html",
        "partials/skill/meta.en.html",
        "partials/skill/meta.vi.html",
        "partials/skill/meta.ko.html",
        "partials/skills-grid.html",
        "vi/partials/skills-grid.html",
        "ko/partials/skills-grid.html",
        "api/skills.json",
        "api/skills/search.json",
        "vi/api/skills.json",
        "vi/api/skills/search.json",
        "ko/api/skills.json",
        "ko/api/skills/search.json",
        "api/raw/meta.md",
        "vi/api/raw/meta.md",
        "ko/api/raw/meta.md",
        "api/skills/meta.json",
        "vi/api/skills/meta.json",
        "ko/api/skills/meta.json",
        "api/skills/meta/prompts.json",
        "api/skills/meta/prompts.vi.json",
        "api/skills/meta/prompts.ko.json",
        "vi/api/skills/meta/prompts.json",
        "ko/api/skills/meta/prompts.json",
        "static/site.css",
        "static/site.js",
        "static/search.js",
        "static/fonts/InterVariable.woff2",
        "static/fonts/ManropeVariable.woff2",
        "robots.txt",
        "sitemap.xml",
        "favicon.ico",
    )
    for relative in expected:
        assert (output / relative).exists(), relative
    exported_css = (output / "static/site.css").read_text(encoding="utf-8")
    assert 'url("/soulmap-ai/static/fonts/InterVariable.woff2")' in exported_css
    assert 'url("/soulmap-ai/static/fonts/ManropeVariable.woff2")' in exported_css

    html = (output / "index.html").read_text(encoding="utf-8")
    assert 'href="/soulmap-ai/' in html
    assert 'src="/soulmap-ai/static/site.js"' in html
    assert 'src="/soulmap-ai/static/search.js"' in html
    skills_html = (output / "skills/index.html").read_text(encoding="utf-8")
    assert (
        'data-detail-url="/soulmap-ai/partials/skill/meta.en.html?lang=en"'
        in skills_html
    )
    assert 'hx-get="/soulmap-ai/partials/skill/meta.en.html?lang=en"' not in skills_html
    assert 'action="/soulmap-ai/skills"' in skills_html
    assert 'data-skill-root="/soulmap-ai/skills"' in skills_html
    assert 'data-search-api="/soulmap-ai/api/skills/search.json"' in skills_html
    assert 'data-search-query-label="Search the Skill catalog"' in skills_html
    assert 'data-ask-query-label="Describe what you want to ask"' in skills_html
    assert 'id="search-panel"' in skills_html
    assert 'id="ask-panel"' in skills_html
    assert 'hx-get="/soulmap-ai/partials/skills-grid.html?lang=en"' not in skills_html
    grid_html = (output / "partials/skills-grid.html").read_text(encoding="utf-8")
    assert (
        'data-detail-url="/soulmap-ai/partials/skill/meta.en.html?lang=en"' in grid_html
    )
    assert 'hx-get="/soulmap-ai/partials/skill/meta.en.html?lang=en"' not in grid_html
    detail_html = (output / "partials/skill/meta.en.html").read_text(encoding="utf-8")
    assert 'href="/soulmap-ai/api/raw/meta.md"' in detail_html
    vi_detail_html = (output / "partials/skill/meta.vi.html").read_text(
        encoding="utf-8"
    )
    assert 'href="/soulmap-ai/vi/api/raw/meta.md"' in vi_detail_html
    ko_detail_html = (output / "partials/skill/meta.ko.html").read_text(
        encoding="utf-8"
    )
    assert 'href="/soulmap-ai/ko/api/raw/meta.md"' in ko_detail_html
    assert (
        (output / "api/skills/search.json").read_text(encoding="utf-8").startswith("{")
    )
    assert (
        (output / "vi/api/skills/search.json")
        .read_text(encoding="utf-8")
        .startswith("{")
    )
    assert 'href="/"' not in html
    assert "viewport-fit=cover" in html
    assert 'media="(prefers-color-scheme: dark)"' in html
    ko_skills_html = (output / "ko/skills/index.html").read_text(encoding="utf-8")
    assert '<html lang="ko">' in ko_skills_html
    assert 'action="/soulmap-ai/ko/skills"' in ko_skills_html
    assert 'data-search-api="/soulmap-ai/ko/api/skills/search.json"' in ko_skills_html
    assert 'x-data="languageMenu"' in ko_skills_html
    assert "한국어" in ko_skills_html
    assert "<script" in html
    assert 'integrity="sha384-' in html


def test_static_export_has_no_source_code_paths_in_html(tmp_path: Path) -> None:
    output = tmp_path / "soulmap-test-static-site"
    export_static(output, "/soulmap-ai")
    for html_path in output.rglob("*.html"):
        if html_path.relative_to(output).as_posix().startswith("partials/"):
            continue
        html = html_path.read_text(encoding="utf-8")
        assert "127.0.0.1" not in html
        assert "localhost" not in html
