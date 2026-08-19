import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast
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
        ("/en", "200 OK"),
        ("/vi", "200 OK"),
        ("/how-it-works", "200 OK"),
        ("/boundaries", "200 OK"),
        ("/download", "200 OK"),
        ("/notes", "200 OK"),
        ("/about", "200 OK"),
        ("/skills", "200 OK"),
        ("/skills/meta", "200 OK"),
        ("/static/site.css", "200 OK"),
        ("/static/site.js", "200 OK"),
        ("/api/skills.json", "200 OK"),
        ("/api/skills/meta/prompts.json", "200 OK"),
        ("/api/skills/meta/prompts.vi.json", "200 OK"),
        ("/api/raw/meta.md", "200 OK"),
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
    assert "prefers-color-scheme: dark" in css
    assert "prefers-reduced-transparency" in css
    assert "safe-area-inset" in css
    assert ":focus-visible" in css
    assert "min-height: 44px" in css
    assert ".modal-dialog" in css
    assert ".skill-grid" in css


def test_layout_loads_pinned_cdn_assets_with_sri() -> None:
    _, body = _request("/skills")
    html = body.decode("utf-8")

    assert 'href="https://rsms.me/inter/inter.css"' in html
    assert "<title>SoulMap Skills · SoulMap AI</title>" in html
    assert "SoulMap AI · SoulMap AI" not in html
    assert 'name="htmx-config"' in html
    assert "includeIndicatorStyles" in html
    assert 'src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"' in html
    assert (
        'src="https://cdn.jsdelivr.net/npm/@alpinejs/csp@3.16.2/dist/cdn.min.js"'
        in html
    )
    assert html.count('integrity="sha384-') == 2
    assert 'src="/static/site.js"' in html
    assert 'hx-get="/partials/skill/meta.en.html?lang=en"' in html
    assert 'aria-haspopup="dialog"' in html
    assert 'aria-controls="skill-modal"' in html
    assert 'id="skill-modal"' in html


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
            "Skill bundle nguồn",
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
    assert "Chọn layer phù hợp với khoảnh khắc này." in html
    assert "Khám phá Skills" not in html

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
        "en/index.html",
        "vi/index.html",
        "skills/index.html",
        "vi/skills/index.html",
        "skills/meta/index.html",
        "vi/skills/meta/index.html",
        "partials/skill/meta.en.html",
        "partials/skill/meta.vi.html",
        "api/skills.json",
        "api/raw/meta.md",
        "api/skills/meta/prompts.json",
        "api/skills/meta/prompts.vi.json",
        "static/site.css",
        "static/site.js",
        "robots.txt",
    )
    for relative in expected:
        assert (output / relative).exists(), relative

    html = (output / "index.html").read_text(encoding="utf-8")
    assert 'href="/soulmap-ai/' in html
    assert 'src="/soulmap-ai/static/site.js"' in html
    skills_html = (output / "skills/index.html").read_text(encoding="utf-8")
    assert 'hx-get="/soulmap-ai/partials/skill/meta.en.html?lang=en"' in skills_html
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
