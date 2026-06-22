"""Navigation + reading helpers for the categories-and-services migration (VCITA2-13993).

The Services index settings page is the Angular frontage app rendered in the outer
``iframe[title="angularjs"]``. Categories are Angular-Material cards
(``md-card[data-qa="services-category-container"]``) that each list their service
rows in order; the page uses endless scroll, so reads scroll the list to load every
card before collecting. Selectors mirror the current legacy page object
``pages/desktop/Frontage/Scheduling/servicesSettings.js``.
"""

from __future__ import annotations

from playwright.sync_api import Page

UI_TIMEOUT = 5_000
SETTLE_MS = 300
SERVICES_PATH = "/app/settings/services"

CATEGORY_CARD = 'md-card[data-qa="services-category-container"]'
CATEGORY_TITLE = ".header-titles .title"
SERVICE_ROW = "div.list-item:not(.main-actions)"
SERVICE_TITLE = ".titles .title"


def app_base(page: Page) -> str:
    if "/app/" not in page.url:
        raise ValueError(f"Cannot infer app base URL from: {page.url}")
    return page.url.split("/app/")[0]


def frame(page: Page):
    """Return the Angular frontage frame locator that hosts the services settings page."""
    return page.frame_locator('iframe[title="angularjs"]')


def goto_services(page: Page):
    """Navigate to (or refresh) the Services settings page and wait until it renders.

    The legacy page object re-enters the page before every action; we mirror that so
    each mutation reads a freshly rendered list. Returns the Angular frame locator.
    """
    page.goto(f"{app_base(page)}{SERVICES_PATH}", wait_until="domcontentloaded", timeout=UI_TIMEOUT)
    page.wait_for_url(f"**{SERVICES_PATH}**", timeout=UI_TIMEOUT, wait_until="domcontentloaded")
    page.wait_for_selector('iframe[title="angularjs"]', state="visible", timeout=UI_TIMEOUT)
    ng = frame(page)
    ng.get_by_role("heading", name="Settings / Services").wait_for(state="visible", timeout=UI_TIMEOUT)
    ng.locator(CATEGORY_CARD).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    return ng


def _scroll_all_categories(page: Page, ng) -> None:
    """Scroll the list until the rendered category-card count stops growing (endless scroll)."""
    previous = -1
    for _ in range(10):
        cards = ng.locator(CATEGORY_CARD)
        count = cards.count()
        if count == previous:
            return
        previous = count
        cards.nth(count - 1).scroll_into_view_if_needed()
        page.wait_for_timeout(SETTLE_MS)


def collect_categories(page: Page) -> list[dict]:
    """Return ``[{name, services: [...]}]`` in displayed order (categories and their rows).

    Re-enters the services page first (mirrors the legacy `search categories` which
    re-runs ServicesSettings().goto()) so the read always sees a freshly rendered list,
    regardless of where the previous action left the browser (e.g. a service editor).
    Each category card exposes its title and the ordered service titles rendered inside it.
    """
    ng = goto_services(page)
    _scroll_all_categories(page, ng)
    cards = ng.locator(CATEGORY_CARD)
    result: list[dict] = []
    for i in range(cards.count()):
        card = cards.nth(i)
        name = (card.locator(CATEGORY_TITLE).first.inner_text() or "").strip()
        titles = card.locator(SERVICE_TITLE)
        services = [(titles.nth(j).inner_text() or "").strip() for j in range(titles.count())]
        result.append({"name": name, "services": [s for s in services if s]})
    return result


def assert_categories(page: Page, expected: list[dict]) -> None:
    """Assert the category->services mapping and order match ``expected`` exactly.

    ``expected`` is ``[{"name": str, "services": [str, ...]}]`` in displayed order,
    mirroring the legacy "search categories" table (order-sensitive).
    """
    actual = collect_categories(page)
    actual_view = [{"name": c["name"], "services": c["services"]} for c in actual]
    assert actual_view == expected, (
        "category->services mapping mismatch.\n"
        f"  expected: {expected}\n"
        f"  actual:   {actual_view}"
    )


def service_row(page: Page, service_name: str):
    """Locate a service row by its visible title across all category cards."""
    ng = frame(page)
    return ng.locator(SERVICE_ROW).filter(has=ng.locator(SERVICE_TITLE, has_text=service_name)).first


def assert_service_details(page: Page, service_name: str, *, contains: list[str], excludes: list[str] | None = None) -> None:
    """Assert a service row shows the expected payment/price/attendees tokens.

    Reads the rendered row text (duration, payment line, attendees) and checks the
    expected tokens are present (e.g. "$100", "10 attendees") and any forbidden tokens
    absent (e.g. no "$" for a don't-display-fee service). This preserves the legacy
    "search services" assertion intent without depending on its brittle field parser.
    Re-enters the services page first so the read is independent of the prior action.
    """
    goto_services(page)
    _scroll_all_categories(page, frame(page))
    row = service_row(page, service_name)
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    text = (row.inner_text() or "")
    for token in contains:
        assert token in text, f"service {service_name!r} row missing {token!r}; row text: {text!r}"
    for token in excludes or []:
        assert token not in text, f"service {service_name!r} row should not contain {token!r}; row text: {text!r}"
