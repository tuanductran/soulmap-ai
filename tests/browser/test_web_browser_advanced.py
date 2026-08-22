from __future__ import annotations

import re
from urllib.parse import parse_qs, unquote, urlparse

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.browser

LOCALES = ("en", "vi", "ko")
ROUTES = ("/faq", "/skills", "/download")


def _path(locale: str, route: str) -> str:
    if locale == "en":
        return route
    return f"/{locale}" if route == "/" else f"/{locale}{route}"


def _open(page: Page, origin: str, locale: str, route: str) -> None:
    expected_path = _path(locale, route)
    page.goto(f"{origin}{expected_path}", wait_until="domcontentloaded")
    page.wait_for_function(
        f"() => window.location.pathname === {expected_path!r} "
        f"&& document.documentElement.lang === {locale!r} "
        "&& typeof window.Alpine === 'object' "
        "&& typeof window.SoulMapSearch === 'object'"
    )
    page.wait_for_function(
        "() => [...document.styleSheets].some(sheet => "
        "sheet.href && sheet.href.endsWith('/static/site.css'))"
    )
    page.locator(".locale-trigger").wait_for(state="visible")
    page.wait_for_timeout(100)


def _expected_locale_path(locale: str, route: str) -> str:
    return _path(locale, route).rstrip("/") or "/"


@pytest.mark.parametrize("start_locale", LOCALES)
@pytest.mark.parametrize("route", ROUTES)
def test_locale_switch_roundtrip_preserves_route_and_context(
    page: Page, browser_origin: str, start_locale: str, route: str
) -> None:
    _open(page, browser_origin, start_locale, route)
    trigger = page.locator(".locale-trigger")
    if trigger.get_attribute("aria-expanded") == "true":
        trigger.click()
    expect(trigger).to_have_attribute("aria-expanded", "false")
    trigger.click()
    menu = page.locator("#language-menu")
    expect(trigger).to_have_attribute("aria-expanded", "true")
    expect(menu).to_be_visible()
    for target in LOCALES:
        link = page.locator(f'#language-menu a[lang="{target}"]')
        expect(link).to_be_visible()
        expected_path = _expected_locale_path(target, route)
        expect(link).to_have_attribute("href", expected_path)
    trigger.click()
    expect(menu).to_be_hidden()

    for target in LOCALES:
        target_path = _path(target, route)
        page.goto(f"{browser_origin}{target_path}", wait_until="domcontentloaded")
        page.wait_for_function(
            f"() => window.location.pathname === {target_path!r} "
            f"&& document.documentElement.lang === {target!r} "
            "&& typeof window.Alpine === 'object' "
            "&& typeof window.SoulMapSearch === 'object'"
        )
        assert re.search(
            re.compile(re.escape(_expected_locale_path(target, route)) + r"/?$"),
            page.url,
        )
        expect(page.locator("main#main-content")).to_be_visible()

    trigger = page.locator(".locale-trigger")
    trigger.click()
    expect(page.locator("#language-menu")).to_be_visible()
    page.locator(".page-hero").click(position={"x": 8, "y": 8})
    expect(page.locator("#language-menu")).to_be_hidden()


@pytest.mark.parametrize("locale", LOCALES)
def test_locale_menu_repeated_toggle_preserves_page_scroll(
    page: Page, browser_origin: str, locale: str
) -> None:
    page.set_viewport_size({"width": 1280, "height": 720})
    _open(page, browser_origin, locale, "/faq")
    target_scroll = page.evaluate(
        "Math.max(1, Math.min(Math.round(document.documentElement.scrollHeight / 2), document.documentElement.scrollHeight - window.innerHeight))"
    )
    page.evaluate(
        "target => { document.documentElement.style.scrollBehavior = 'auto'; window.scrollTo(0, target); }",
        target_scroll,
    )
    page.wait_for_function(
        "target => Math.abs(window.scrollY - target) <= 1", arg=target_scroll
    )
    scroll_before = page.evaluate("window.scrollY")
    assert scroll_before > 0
    trigger = page.locator(".locale-trigger")
    menu = page.locator("#language-menu")

    for _ in range(3):
        trigger.dispatch_event("click")
        expect(menu).to_be_visible()
        trigger.dispatch_event("click")
        expect(menu).to_be_hidden()

    scroll_after = page.evaluate("window.scrollY")
    assert abs(scroll_after - scroll_before) <= 1


def test_locale_menu_keyboard_open_and_focus_return(
    page: Page, browser_origin: str
) -> None:
    _open(page, browser_origin, "ko", "/faq")
    trigger = page.locator(".locale-trigger")
    trigger.focus()
    page.keyboard.press("Enter")
    expect(page.locator("#language-menu")).to_be_visible()
    expect(trigger).to_have_attribute("aria-expanded", "true")
    page.keyboard.press("Escape")
    expect(page.locator("#language-menu")).to_be_hidden()
    expect(trigger).to_be_focused()


@pytest.mark.parametrize("locale", LOCALES)
def test_primary_nav_exposes_horizontal_scroll_edges(
    page: Page, browser_origin: str, locale: str
) -> None:
    page.set_viewport_size({"width": 320, "height": 720})
    _open(page, browser_origin, locale, "/faq")
    shell = page.locator(".nav-links-shell")
    nav = page.locator(".nav-links")
    assert nav.evaluate("element => element.scrollWidth") > nav.evaluate(
        "element => element.clientWidth"
    )
    expect(shell).not_to_have_attribute("data-scroll-left")
    expect(shell).to_have_attribute("data-scroll-right", "true")

    nav.evaluate(
        "element => { element.scrollLeft = (element.scrollWidth - element.clientWidth) / 2; }"
    )
    expect(shell).to_have_attribute("data-scroll-left", "true")
    expect(shell).to_have_attribute("data-scroll-right", "true")

    nav.evaluate("element => { element.scrollLeft = element.scrollWidth; }")
    expect(shell).to_have_attribute("data-scroll-left", "true")
    expect(shell).not_to_have_attribute("data-scroll-right")

    nav.evaluate("element => { element.scrollLeft = 0; }")
    expect(shell).not_to_have_attribute("data-scroll-left")
    expect(shell).to_have_attribute("data-scroll-right", "true")
    assert (
        float(
            page.locator(".nav-links-shell").evaluate(
                "element => getComputedStyle(element, '::after').opacity"
            )
        )
        > 0
    )

    nav.evaluate(
        "element => { element.scrollLeft = (element.scrollWidth - element.clientWidth) / 2; }"
    )
    expect(shell).to_have_attribute("data-scroll-left", "true")
    expect(shell).to_have_attribute("data-scroll-right", "true")
    assert (
        float(
            page.locator(".nav-links-shell").evaluate(
                "element => getComputedStyle(element, '::before').opacity"
            )
        )
        > 0
    )


@pytest.mark.parametrize("locale", LOCALES)
def test_locales_share_the_default_font_stack(
    page: Page, browser_origin: str, locale: str
) -> None:
    _open(page, browser_origin, locale, "/")
    page.wait_for_function(
        "() => document.fonts && document.fonts.status === 'loaded' "
        "&& document.fonts.check('1em Inter')"
    )
    page.wait_for_timeout(100)
    font_family = page.locator("body").evaluate(
        "element => getComputedStyle(element).fontFamily"
    )
    assert font_family.startswith("Inter")
    assert (
        page.locator("html").evaluate("element => getComputedStyle(element).fontFamily")
        == font_family
    )


@pytest.mark.parametrize("locale", LOCALES)
def test_faq_keyboard_disclosures_keep_independent_state(
    page: Page, browser_origin: str, locale: str
) -> None:
    _open(page, browser_origin, locale, "/faq")
    items = page.locator("details.faq-item")
    first_summary = items.nth(0).locator("summary")
    second_summary = items.nth(1).locator("summary")
    first_summary.focus()
    page.keyboard.press("Enter")
    expect(items.nth(0)).to_have_attribute("open", "")
    second_summary.focus()
    page.keyboard.press("Space")
    expect(items.nth(1)).to_have_attribute("open", "")
    expect(items.nth(0).locator(".faq-answer")).to_be_visible()
    expect(items.nth(1).locator(".faq-answer")).to_be_visible()
    first_summary.focus()
    page.keyboard.press("Enter")
    expect(items.nth(0)).not_to_have_attribute("open", "")
    expect(items.nth(1)).to_have_attribute("open", "")


@pytest.mark.parametrize(
    ("locale", "search_query", "ask_query"),
    [
        ("en", "grief", "sad"),
        ("vi", "khủng hoảng", "buồn bã"),
        ("ko", "슬픔", "불안"),
    ],
)
def test_search_ask_toggle_and_use_question_flow(
    page: Page,
    browser_origin: str,
    locale: str,
    search_query: str,
    ask_query: str,
) -> None:
    _open(page, browser_origin, locale, "/skills")
    form = page.locator("form[data-search-api]")
    query = page.locator("#skill-search")
    grid = page.locator("#skill-grid")
    questions = page.locator("#question-results")
    query.fill(search_query)
    expect(grid).to_have_attribute("aria-busy", "false")
    expect(grid.locator(".skill-card:not([hidden])")).not_to_have_count(0)
    page.locator('label.mode-option:has(input[value="ask"])').click()
    expect(page.locator("#ask-panel")).to_be_visible()
    expect(page.locator("#search-panel")).to_be_hidden()
    query.fill(ask_query)
    expect(questions).to_have_attribute("aria-busy", "false")
    expect(questions.locator("article")).not_to_have_count(0)
    first_question = questions.locator("article").first
    use_button = first_question.locator("button").first
    original_query = query.input_value()
    use_button.click()
    chooser = page.locator("#provider-chooser")
    dialog = page.locator("#provider-chooser-dialog")
    expect(questions).to_have_attribute("aria-busy", "false")
    expect(chooser).to_be_visible()
    expect(dialog).to_be_focused()
    expect(query).to_have_value(original_query)
    expect(dialog.locator(".provider-chooser__question")).not_to_be_empty()
    provider_links = dialog.locator(".provider-chooser__actions a")
    expect(provider_links).to_have_count(2)
    expect(provider_links.nth(0)).to_have_attribute(
        "href", re.compile(r"^https://chatgpt\.com/\?q=")
    )
    expect(provider_links.nth(1)).to_have_attribute(
        "href", re.compile(r"^https://claude\.ai/new\?q=")
    )
    chatgpt_href = provider_links.nth(0).get_attribute("href")
    assert chatgpt_href is not None
    decoded_prompt = unquote(parse_qs(urlparse(chatgpt_href).query)["q"][0])
    assert re.search(
        r"https://tuanductran\.github\.io/soulmap-ai/(?:[a-z]{2}/)?api/raw/",
        decoded_prompt,
    )
    expect(dialog.locator(".provider-chooser__raw a")).to_have_attribute(
        "href",
        re.compile(
            r"^https://tuanductran\.github\.io/soulmap-ai/(?:[a-z]{2}/)?api/raw/"
        ),
    )
    page.keyboard.press("Escape")
    expect(chooser).to_be_hidden()
    expect(use_button).to_be_focused()
    use_button.click()
    expect(chooser).to_be_visible()
    chooser.locator(".modal-backdrop").click(position={"x": 2, "y": 2})
    expect(chooser).to_be_hidden()
    expect(chooser).to_have_count(0)
    expect(use_button).to_be_focused()
    expect(questions.locator("article")).not_to_have_count(0)
    page.locator('label.mode-option:has(input[value="search"])').click()
    expect(page.locator("#search-panel")).to_be_visible()
    expect(page.locator("#ask-panel")).to_be_hidden()
    expect(form).to_have_attribute(
        "data-search-api", re.compile(r"/api/skills/search\.json")
    )


@pytest.mark.parametrize("locale", LOCALES)
def test_search_query_is_bounded_and_enter_stays_on_route(
    page: Page, browser_origin: str, locale: str
) -> None:
    _open(page, browser_origin, locale, "/skills")
    query = page.locator("#skill-search")
    current_url = page.url
    query.fill("x" * 5000)
    query.press("Enter")
    expect(page).to_have_url(current_url)
    expect(page.locator("#skill-grid")).to_be_visible()
    expect(page.locator("#skill-grid")).to_have_attribute("aria-busy", "false")
    expect(page.locator("body")).not_to_contain_text(
        "Search is temporarily unavailable"
    )


@pytest.mark.parametrize("locale", LOCALES)
def test_modal_focus_trap_backdrop_close_resize_and_localized_raw_links(
    page: Page, browser_origin: str, locale: str
) -> None:
    page.set_viewport_size({"width": 320, "height": 720})
    _open(page, browser_origin, locale, "/skills")
    trigger = page.locator('#skill-grid .skill-card a[aria-haspopup="dialog"]').first
    trigger.click()
    dialog = page.locator('#skill-modal [role="dialog"]')
    expect(dialog).to_be_visible()
    expect(page.locator("body")).to_have_class(re.compile(r"\bmodal-open\b"))
    source_links = dialog.locator(".prompt-scenario__source a")
    expect(source_links).to_have_count(3)
    expected_raw = (
        "/api/raw/meta.md" if locale == "en" else f"/{locale}/api/raw/meta.md"
    )
    for link in source_links.all():
        expect(link).to_have_attribute("href", expected_raw)
    focusable = dialog.locator(
        "a[href], button:not([disabled]), [tabindex]:not([tabindex='-1'])"
    )
    expect(focusable).not_to_have_count(0)
    focusable.last.focus()
    page.keyboard.press("Tab")
    expect(focusable.first).to_be_focused()
    page.keyboard.press("Shift+Tab")
    expect(focusable.last).to_be_focused()
    page.set_viewport_size({"width": 1280, "height": 900})
    expect(dialog).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth") <= page.evaluate(
        "document.documentElement.clientWidth"
    )
    page.locator("#skill-modal > .modal-backdrop").click(position={"x": 2, "y": 2})
    expect(dialog).to_be_hidden()
    expect(page.locator("#skill-modal")).to_have_count(0)
    expect(trigger).to_be_focused()
    expect(page.locator("body")).not_to_have_class(re.compile(r"\bmodal-open\b"))
