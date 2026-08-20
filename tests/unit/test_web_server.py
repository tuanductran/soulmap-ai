import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast
from urllib.parse import unquote
from wsgiref.types import StartResponse
from wsgiref.util import setup_testing_defaults

import pytest

from soulmap.cli import _command_table
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


@pytest.mark.parametrize(
    ("path", "status"),
    [
        ("/", "200 OK"),
        ("/en", "301 Moved Permanently"),
        ("/vi", "200 OK"),
        ("/how-it-works", "200 OK"),
        ("/boundaries", "200 OK"),
        ("/download", "200 OK"),
        ("/notes", "200 OK"),
        ("/about", "200 OK"),
        ("/faq", "200 OK"),
        ("/privacy", "200 OK"),
        ("/vi/faq", "200 OK"),
        ("/vi/privacy", "200 OK"),
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
        ("/api/skills/meta/prompts.json", "200 OK"),
        ("/api/skills/meta/prompts.vi.json", "200 OK"),
        ("/api/raw/meta.md", "200 OK"),
        ("/partials/skill/not-real.en.html", "404 Not Found"),
        ("/partials/skill/not-real.vi.html", "404 Not Found"),
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


def test_sitemap_and_robots_reference_only_public_canonical_urls() -> None:
    sitemap_captured, sitemap_body = _request("/sitemap.xml")
    sitemap = sitemap_body.decode("utf-8")
    assert sitemap_captured["status"] == "200 OK"
    assert 'xmlns:xhtml="http://www.w3.org/1999/xhtml"' in sitemap
    assert "https://tuanductran.github.io/soulmap-ai/faq/" in sitemap
    assert "https://tuanductran.github.io/soulmap-ai/vi/privacy/" in sitemap
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
    assert "Thông báo này bao phủ điều gì" in privacy
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
    assert "border-radius: var(--radius-hero) 36px 28px 32px" in css
    assert "border-radius: 40% 40% 34% 34% / 34% 34% 42% 42%" not in css
    assert "#c99b50" not in css
    assert "prefers-reduced-motion" in css
    assert "select:focus-visible" in css
    assert "textarea:focus-visible" in css
    assert "button, input, select, textarea { font: inherit; }" in css
    assert "prefers-color-scheme: dark" in css
    assert "prefers-reduced-transparency" in css
    assert "safe-area-inset" in css
    assert ":focus-visible" in css
    assert "min-height: 44px" in css
    assert "body.modal-open { overflow: hidden; }" in css
    assert ".modal-dialog" in css
    assert ".skill-grid" in css
    assert ".faq-item" in css
    assert ".privacy-grid" in css


def test_layout_loads_pinned_cdn_assets_with_sri() -> None:
    _, body = _request("/skills")
    html = body.decode("utf-8")

    assert 'href="https://rsms.me/inter/inter.css"' in html
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
    _, search_body = _request("/static/search.js")
    search_js = search_body.decode("utf-8")
    assert "SoulMapSearch" in search_js
    _, js_body = _request("/static/site.js")
    js = js_body.decode("utf-8")
    assert 'document.body.classList.add("modal-open")' in js
    assert 'document.body.classList.remove("modal-open")' in js
    assert "copyFailed: false" in js
    assert "this.copyFailed = !success" in js
    assert 'hx-get="/partials/skill/meta.en.html?lang=en"' in html
    assert 'hx-get="/partials/skills-grid.html?lang=en"' not in html
    assert 'method="get"' in html
    assert 'x-on:submit="preventSubmit($event)"' in html
    assert 'data-skill-root="/skills"' in html
    assert 'data-search-api="/api/skills/search.json"' in html
    assert 'data-search-error="Search is temporarily unavailable.' in html
    assert 'aria-controls="skill-grid question-results"' in html
    assert 'data-search-locale="en"' in html
    assert '<option value="search">Search Skills</option>' in html
    assert '<option value="ask">Ask with a Skill</option>' in html
    assert "SoulMap Skill details" in html
    assert 'x-model="mode"' in html
    assert 'id="question-results"' in html
    assert 'enterkeyhint="search"' in html
    assert "Choose Search or Ask" in html
    assert 'aria-haspopup="dialog"' in html
    assert 'aria-controls="skill-modal"' in html
    assert 'id="skill-modal"' in html
    assert 'id="skill-loading"' in html
    assert 'role="status"' in html
    assert "x-cloak" in html
    assert "x-transition.opacity.duration.200ms" in html
    assert "x-transition.opacity.scale.origin.top.duration.200ms" in html
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

    group_body = _request("/api/skills/search.json", "group=Safety")[1]
    group_payload = json.loads(group_body)
    assert [result["slug"] for result in group_payload["results"]] == ["safety"]


def test_ask_mode_uses_json_scenarios_and_safe_dom_rendering() -> None:
    _, html_body = _request("/vi/skills")
    html = html_body.decode("utf-8")
    assert 'data-ask-intro="Chế độ Hỏi giúp bạn chọn một Skill công khai' in html
    assert 'data-ask-result-label="Câu hỏi mở đầu"' in html
    assert 'data-ask-use-label="Dùng câu hỏi này"' in html
    assert 'id="question-results"' in html

    _, search_body = _request("/static/search.js")
    search_js = search_body.decode("utf-8")
    assert "prompt_scenarios" in search_js
    assert "document" not in search_js
    assert "innerHTML" not in search_js

    _, site_body = _request("/static/site.js")
    site_js = site_body.decode("utf-8")
    assert "renderAskResults" in site_js
    assert "renderSearchError" in site_js
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
    assert "Chọn Tìm kiếm hoặc Hỏi" in html
    assert '<option value="ask">Hỏi cùng một Skill</option>' in html
    assert 'data-skill-root="/vi/skills"' in html
    assert 'id="question-results"' in html

    _, search_body = _request("/static/search.js")
    search_js = search_body.decode("utf-8")
    assert "SoulMapSearch" in search_js

    _, js_body = _request("/static/site.js")
    js = js_body.decode("utf-8")
    assert "preventSubmit(event)" in js
    assert "event.preventDefault();" in js
    assert "window.SoulMapSearch" in js
    assert 'credentials: "same-origin"' in js


def test_skill_fragment_exposes_provider_handoffs_in_both_locales() -> None:
    _, english_body = _request("/partials/skill/meta.en.html")
    english = english_body.decode("utf-8")
    _, vietnamese_body = _request("/partials/skill/meta.vi.html")
    vietnamese = vietnamese_body.decode("utf-8")

    for html, labels, heading, prompt_label, source_label, question_label in (
        (
            english,
            ("Open in ChatGPT", "Open in Claude", "Open in Claude Code"),
            "Choose a context-specific prompt",
            "Prompt",
            "Source Skill bundle",
            "Starter question",
        ),
        (
            vietnamese,
            ("Mở trong ChatGPT", "Mở trong Claude", "Mở trong Claude Code"),
            "Chọn prompt theo bối cảnh",
            "Prompt",
            "Gói Skill nguồn",
            "Câu hỏi bắt đầu",
        ),
    ):
        assert heading in html
        assert html.count(prompt_label) >= 3
        assert html.count(source_label) >= 3
        assert html.count(question_label) >= 3
        assert (
            html.count("https://tuanductran.github.io/soulmap-ai/api/raw/meta.md") >= 3
        )
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
    assert "Bắt đầu một phiên phản chiếu" in vi_prompts["scenarios"][0]["title"]

    _, vi_catalog_body = _request("/api/skills.json", "lang=vi")
    vi_catalog = vi_catalog_body.decode("utf-8")
    assert '"locale": "vi"' in vi_catalog
    assert "Điều phối cốt lõi" in vi_catalog

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
    visible_main = html.split('<main id="main-content">', 1)[1].split("</main>", 1)[0]
    assert "Khám phá các Skills" not in visible_main
    assert "inner work" not in visible_main
    assert "authority" not in visible_main
    assert "privacy" not in visible_main.lower()
    assert "Phản chiếu" in visible_main
    assert "Reflection" not in visible_main
    assert "6 nhóm · có bundle Markdown gốc" in visible_main
    assert "groups · raw bundles available" not in visible_main

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
        assert html.count("<h1>") == 1
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
        "faq/index.html",
        "privacy/index.html",
        "vi/faq/index.html",
        "vi/privacy/index.html",
        "skills/index.html",
        "privacy/index.html",
        "vi/faq/index.html",
        "vi/privacy/index.html",
        "skills/index.html",
        "vi/skills/index.html",
        "skills/meta/index.html",
        "vi/skills/meta/index.html",
        "partials/skill/meta.en.html",
        "partials/skill/meta.vi.html",
        "partials/skills-grid.html",
        "vi/partials/skills-grid.html",
        "api/skills.json",
        "api/skills/search.json",
        "vi/api/skills.json",
        "vi/api/skills/search.json",
        "api/raw/meta.md",
        "api/skills/meta/prompts.json",
        "api/skills/meta/prompts.vi.json",
        "static/site.css",
        "static/site.js",
        "static/search.js",
        "robots.txt",
        "sitemap.xml",
        "favicon.ico",
    )
    for relative in expected:
        assert (output / relative).exists(), relative

    html = (output / "index.html").read_text(encoding="utf-8")
    assert 'href="/soulmap-ai/' in html
    assert 'src="/soulmap-ai/static/site.js"' in html
    assert 'src="/soulmap-ai/static/search.js"' in html
    skills_html = (output / "skills/index.html").read_text(encoding="utf-8")
    assert 'hx-get="/soulmap-ai/partials/skill/meta.en.html?lang=en"' in skills_html
    assert 'action="/soulmap-ai/skills"' in skills_html
    assert 'data-skill-root="/soulmap-ai/skills"' in skills_html
    assert 'data-search-api="/soulmap-ai/api/skills/search.json"' in skills_html
    assert '<option value="ask">Ask with a Skill</option>' in skills_html
    assert 'hx-get="/soulmap-ai/partials/skills-grid.html?lang=en"' not in skills_html
    grid_html = (output / "partials/skills-grid.html").read_text(encoding="utf-8")
    assert 'hx-get="/soulmap-ai/partials/skill/meta.en.html?lang=en"' in grid_html
    detail_html = (output / "partials/skill/meta.en.html").read_text(encoding="utf-8")
    assert 'href="/soulmap-ai/api/raw/meta.md"' in detail_html
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
    assert "<script" in html
    assert 'integrity="sha384-' in html


def test_static_export_has_no_source_code_paths_in_html() -> None:
    output = Path("/tmp") / "soulmap-test-static-site"
    export_static(output, "/soulmap-ai")
    for html_path in output.rglob("*.html"):
        if html_path.relative_to(output).as_posix().startswith("partials/"):
            continue
        html = html_path.read_text(encoding="utf-8")
        assert "127.0.0.1" not in html
        assert "localhost" not in html
