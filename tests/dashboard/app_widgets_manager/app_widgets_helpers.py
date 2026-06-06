"""Helpers for the app_widgets_manager migration (VCITA2-13864).

New-dashboard widgets render on the top-level POV page (verified live: 6
`[data-qa="EmbeddedAppDelegator"]`, 1 `.sales-widget`, all at frame `''`).
"""

import time

from playwright.sync_api import Page

UI_TIMEOUT = 5_000
WIDGET = '[data-qa="EmbeddedAppDelegator"]'


def open_dashboard(page: Page) -> None:
    app_base = page.url.split("/app/")[0]
    page.goto(f"{app_base}/app/dashboard", wait_until="domcontentloaded", timeout=15_000)
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
    """Whether the `<name>-widget` is rendered (mirrors legacy isWidgetFound)."""
    widget = page.locator(f".{name}-widget").first
    try:
        widget.wait_for(state="visible", timeout=UI_TIMEOUT)
        return True
    except Exception:
        return False
