"""Helpers for the app_widgets_manager migration (VCITA2-13864).

New-dashboard widgets render on the top-level POV page (verified live: 6
`[data-qa="EmbeddedAppDelegator"]`, 1 `.sales-widget`, all at frame `''`).
"""

import time

from playwright.sync_api import Page

UI_TIMEOUT = 5_000
# page.goto budget for the top-level POV dashboard; domcontentloaded fires fast and
# readiness is gated by the dashboard main section + widget delegator waits below.
PAGE_TIMEOUT = 5_000
WIDGET = '[data-qa="EmbeddedAppDelegator"]'
# Dashboard main container — legacy `isWidgetFound` waits for `.main` before probing a
# widget so a not-yet-rendered grid never reads as an absent widget.
DASHBOARD_MAIN = ".main"


def open_dashboard(page: Page) -> None:
    app_base = page.url.split("/app/")[0]
    page.goto(f"{app_base}/app/dashboard", wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    # Gate on the dashboard main section before the widget grid so widget presence/absence
    # is read against a mounted dashboard (mirrors legacy main_section readiness).
    page.locator(DASHBOARD_MAIN).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    page.locator(WIDGET).first.wait_for(state="visible", timeout=UI_TIMEOUT)


def assert_widget_count(page: Page, expected: int) -> None:
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    count = -1
    while time.monotonic() < deadline:
        count = page.locator(WIDGET).count()
        if count == expected:
            return
        time.sleep(0.2)
    raise AssertionError(f"Expected {expected} dashboard widgets, got {count}")


def is_widget_shown(page: Page, name: str) -> bool:
    """Whether the `<name>-widget` is rendered (mirrors legacy isWidgetFound).

    Legacy waits for the dashboard main section first, then polls the widget, so a
    still-mounting grid is never mistaken for an absent widget. Gate on `.main` here too.
    """
    page.locator(DASHBOARD_MAIN).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    widget = page.locator(f".{name}-widget").first
    try:
        widget.wait_for(state="visible", timeout=UI_TIMEOUT)
        return True
    except Exception:
        return False
