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
        page.goto(f"{browser_origin}{_path(locale, route)}", wait_until="networkidle")
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
    page.goto(f"{browser_origin}/vi/faq", wait_until="networkidle")
    trigger = page.locator(".locale-trigger")
    menu = page.locator("#language-menu")
    expect(trigger).to_have_attribute("aria-expanded", "false")
    expect(menu).to_be_hidden()

    trigger.click()
    expect(trigger).to_have_attribute("aria-expanded", "true")
    expect(menu).to_be_visible()
    expect(menu.get_by_role("menuitem")).to_have_count(3)

    menu.get_by_role("menuitem", name=re.compile("English")).click()
    expect(page).to_have_url(re.compile(r"/faq/?$"))
    expect(page.locator("html")).to_have_attribute("lang", "en")

    page.goto(f"{browser_origin}/ko/faq", wait_until="networkidle")
    page.locator(".locale-trigger").click()
    page.keyboard.press("Escape")
    expect(page.locator("#language-menu")).to_be_hidden()


def test_skills_search_ask_mode_and_enter_do_not_navigate(
    page: Page,
    browser_origin: str,
) -> None:
    page.goto(f"{browser_origin}/vi/skills", wait_until="networkidle")
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


def test_skill_detail_htmx_modal_focus_and_provider_links(
    page: Page,
    browser_origin: str,
) -> None:
    page.goto(f"{browser_origin}/skills", wait_until="networkidle")
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

    page.keyboard.press("Escape")
    expect(dialog).to_be_hidden()
    expect(trigger).to_be_focused()


def test_skills_mobile_layout_has_touch_targets_and_no_modal_overflow(
    page: Page,
    browser_origin: str,
) -> None:
    page.set_viewport_size({"width": 320, "height": 720})
    page.goto(f"{browser_origin}/skills", wait_until="networkidle")
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
