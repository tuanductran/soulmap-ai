from __future__ import annotations

import re
from collections.abc import Mapping

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.browser

PAGE_ROUTES = (
    "/",
    "/how-it-works",
    "/boundaries",
    "/download",
    "/notes",
    "/about",
    "/faq",
    "/privacy",
    "/skills",
)
LOCALES = ("en", "vi", "ko")
VIEWPORTS = ((320, 720), (768, 900), (1280, 900))


def _path(locale: str, route: str) -> str:
    if locale == "en":
        return route
    if route == "/":
        return f"/{locale}"
    return f"/{locale}{route}"


def _open(page: Page, url: str) -> None:
    page.goto(url, wait_until="commit")
    page.wait_for_function(
        "() => typeof window.Alpine === 'object' && typeof window.SoulMapSearch === 'object'"
    )
    page.wait_for_function(
        "() => [...document.styleSheets].some(sheet => "
        "sheet.href && sheet.href.endsWith('/static/site.css'))"
    )


def _diagnostics_are_empty(diagnostics: Mapping[str, list[str]]) -> None:
    assert diagnostics["console_errors"] == []
    assert diagnostics["page_errors"] == []
    assert diagnostics["failed_requests"] == []


@pytest.mark.parametrize("locale", LOCALES)
def test_localized_pages_have_landmarks_and_no_horizontal_overflow(
    page: Page,
    browser_origin: str,
    locale: str,
) -> None:
    page.set_viewport_size({"width": 320, "height": 720})
    for route in PAGE_ROUTES:
        _open(page, f"{browser_origin}{_path(locale, route)}")
        expect(page.locator("html")).to_have_attribute("lang", locale)
        expect(page.locator("main#main-content")).to_be_visible()
        expect(page.locator("h1")).to_have_count(1)
        viewport_width = page.evaluate("document.documentElement.clientWidth")
        document_width = page.evaluate("document.documentElement.scrollWidth")
        assert document_width <= viewport_width, (
            locale,
            route,
            document_width,
            viewport_width,
        )


def test_language_menu_opens_switches_locale_and_closes_with_escape(
    page: Page,
    browser_origin: str,
) -> None:
    _open(page, f"{browser_origin}/vi/faq")
    trigger = page.locator(".locale-trigger")
    menu = page.locator("#language-menu")
    expect(trigger).to_have_attribute("aria-expanded", "false")
    expect(menu).to_be_hidden()

    trigger.click()
    expect(trigger).to_have_attribute("aria-expanded", "true")
    expect(menu).to_be_visible()
    expect(menu.get_by_role("menuitem")).to_have_count(3)

    menu.get_by_role("menuitem", name=re.compile("English")).evaluate(
        "element => element.click()"
    )
    for _ in range(100):
        if page.url.rstrip("/") == f"{browser_origin}/faq":
            break
        page.wait_for_timeout(100)
    else:
        raise AssertionError(
            f"locale navigation did not reach /faq; current URL: {page.url}"
        )
    page.wait_for_function(
        "() => window.location.pathname === '/faq' "
        "&& document.documentElement.lang === 'en'"
    )
    assert re.search(r"/faq/?$", page.url)
    expect(page.locator("html")).to_have_attribute("lang", "en")

    _open(page, f"{browser_origin}/ko/faq")
    page.locator(".locale-trigger").click()
    page.keyboard.press("Escape")
    expect(page.locator("#language-menu")).to_be_hidden()


def test_language_menu_supports_arrow_navigation_and_focus_restore(
    page: Page,
    browser_origin: str,
) -> None:
    _open(page, f"{browser_origin}/faq")
    trigger = page.locator(".locale-trigger")
    menu = page.locator("#language-menu")

    trigger.focus()
    page.keyboard.press("ArrowDown")
    expect(menu).to_be_visible()
    expect(menu.get_by_role("menuitem").first).to_be_focused()

    page.keyboard.press("ArrowDown")
    expect(menu.get_by_role("menuitem").nth(1)).to_be_focused()

    page.keyboard.press("Escape")
    expect(menu).to_be_hidden()
    expect(trigger).to_be_focused()


def test_skills_search_ask_mode_and_enter_do_not_navigate(
    page: Page,
    browser_origin: str,
) -> None:
    _open(page, f"{browser_origin}/vi/skills")
    query = page.locator("#skill-search")
    expect(page.locator("#skill-grid")).to_be_visible()
    expect(page.locator("#skill-grid .skill-card")).to_have_count(6)

    query.fill("khủng hoảng")
    expect(page.locator("#skill-grid .skill-card:not([hidden])")).not_to_have_count(0)
    search_url = page.url
    query.press("Enter")
    expect(page).to_have_url(search_url)

    page.locator('label.mode-option:has(input[name="mode"][value="ask"])').click()
    expect(page.locator("#ask-panel")).to_be_visible()
    expect(page.locator("#search-panel")).to_be_hidden()
    query.fill("buồn")
    expect(page.locator("#question-results article")).not_to_have_count(0)
    expect(page.locator("#question-results .provider-grid")).to_have_count(0)


@pytest.mark.parametrize(
    ("locale", "skill_id_label", "ask_hint"),
    [
        ("en", "Skill ID", "Ask matches existing public scenarios"),
        ("vi", "Mã Skill", "Hỏi chỉ khớp với các kịch bản công khai"),
        (
            "ko",
            "Skill 식별자",
            "질문 모드는 기존 공개 시나리오와 일치하는 항목을 찾으며",
        ),
    ],
)
def test_localized_skills_controls_do_not_leak_ui_english(
    page: Page,
    browser_origin: str,
    locale: str,
    skill_id_label: str,
    ask_hint: str,
) -> None:
    _open(page, f"{browser_origin}{_path(locale, '/skills')}")
    form = page.locator("form[data-search-api]")
    expect(form).to_have_attribute("data-ask-query-hint", re.compile(ask_hint))
    if locale == "ko":
        expect(form).not_to_have_attribute(
            "data-ask-query-hint", re.compile(r"\bAsk\b")
        )
    slug = page.locator("#skill-grid .skill-card__slug").first
    expect(slug).to_have_attribute("aria-label", f"{skill_id_label}: meta")
    expect(slug).to_have_class(re.compile(r"\bsr-only\b"))
    expect(page.locator("#skill-grid .code-pill")).to_have_count(0)
    raw_href = page.locator(
        '#skill-grid .skill-card a.link-button[href*="/api/raw/"]'
    ).first
    expected_raw_path = (
        "/api/raw/meta.md" if locale == "en" else f"/{locale}/api/raw/meta.md"
    )
    expect(raw_href).to_have_attribute("href", expected_raw_path)


def test_skill_detail_htmx_modal_focus_and_provider_links(
    page: Page,
    browser_origin: str,
) -> None:
    _open(page, f"{browser_origin}/skills")
    trigger = page.locator('#skill-grid .skill-card a[aria-haspopup="dialog"]').first
    trigger.click()

    dialog = page.locator('[role="dialog"]')
    expect(dialog).to_be_visible()
    expect(dialog.locator(".modal-dialog__header h2")).to_be_visible()
    expect(dialog.locator(".prompt-scenario")).not_to_have_count(0)
    provider_grids = dialog.locator(".prompt-scenario .provider-grid")
    expect(provider_grids).not_to_have_count(0)
    for provider_grid in provider_grids.all():
        expect(provider_grid.locator("a")).to_have_count(3)
        for link in provider_grid.locator("a").all():
            expect(link).to_have_attribute(
                "href", re.compile(r"^(?:https?://|/api/raw/|claude-cli://)")
            )

    expect(dialog).to_be_focused()
    dialog.press("Escape")
    expect(dialog).to_be_hidden()
    expect(trigger).to_be_focused()


@pytest.mark.parametrize("locale", LOCALES)
@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_skills_action_buttons_are_balanced(
    page: Page,
    browser_origin: str,
    locale: str,
    viewport: tuple[int, int],
) -> None:
    page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
    _open(page, f"{browser_origin}{_path(locale, '/skills')}")
    search_queries = {
        "en": ("grief", "sad"),
        "vi": ("khủng hoảng", "buồn"),
        "ko": ("슬픔", "불안"),
    }

    for mode, query_text in zip(("search", "ask"), search_queries[locale], strict=True):
        page.locator(f'label.mode-option:has(input[value="{mode}"])').click()
        query = page.locator("#skill-search")
        query.fill(query_text)
        rows = page.locator(
            "#skill-grid .skill-card__actions"
            if mode == "search"
            else "#question-results .skill-card__actions"
        )
        expect(rows).not_to_have_count(0)
        for row in rows.all():
            buttons = row.locator(":scope > *")
            expect(buttons).to_have_count(2)
            widths = [
                box["width"]
                for button in buttons.all()
                if (box := button.bounding_box()) is not None
            ]
            assert len(widths) == 2
            assert abs(widths[0] - widths[1]) <= 1, (locale, viewport, mode, widths)


def test_skills_mobile_layout_has_touch_targets_and_no_modal_overflow(
    page: Page,
    browser_origin: str,
) -> None:
    page.set_viewport_size({"width": 320, "height": 720})
    _open(page, f"{browser_origin}/skills")
    for selector in (".locale-trigger", ".mode-option", ".skill-card__actions a"):
        for element in page.locator(selector).all():
            box = element.bounding_box()
            assert box is not None
            assert box["width"] >= 44
            assert box["height"] >= 44

    page.locator('#skill-grid .skill-card a[aria-haspopup="dialog"]').first.click()
    dialog = page.locator('[role="dialog"]')
    expect(dialog).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth") <= page.evaluate(
        "document.documentElement.clientWidth"
    )


def test_browser_diagnostics_fixture_is_available(
    browser_diagnostics: Mapping[str, list[str]],
) -> None:
    _diagnostics_are_empty(browser_diagnostics)
