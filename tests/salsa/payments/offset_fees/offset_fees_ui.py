"""Shared UI primitives for the offset_fees subcategories.

The offset-fee controls and card-on-file dialog live across the frontage
document nesting (POV at top, Angular and Vue in iframes), and the client
portal checkout lives inside the vitrage `cp_iframe`. These helpers resolve a
visible control across the page and all of its frames, and open the POV
"Online Payments" settings tab that hosts both the ACH and offset-fee controls.

All explicit waits are capped at 5s per the auto_tester wait policy; rely on
readiness signals, not longer timeouts.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

FAST_UI_TIMEOUT = 5000

ONLINE_PAYMENTS_TAB_PATH = "/app/settings/payments?tab=online-payments"
SAVE_BUTTON = '[data-qa="online-payments-tab-header-saveButton"]'


def first_visible(locators, timeout: int = FAST_UI_TIMEOUT):
    """Return the first visible locator from the list, polling within the cap."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for locator in locators:
            try:
                for index in range(locator.count()):
                    candidate = locator.nth(index)
                    if candidate.is_visible():
                        return candidate
            except Exception:
                continue
        time.sleep(0.1)
    return None


def find_control(page: Page, selector: str, timeout: int = FAST_UI_TIMEOUT):
    """Find the first visible match for `selector` across the page and all frames."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        scopes = [page, *page.frames]
        found = first_visible([scope.locator(selector) for scope in scopes], timeout=300)
        if found is not None:
            return found
        time.sleep(0.1)
    return None


def frame_with(page: Page, selector: str, timeout: int = FAST_UI_TIMEOUT):
    """Return the page/frame whose DOM contains `selector` (visible), or None."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for scope in [page, *page.frames]:
            try:
                locator = scope.locator(selector)
                for index in range(locator.count()):
                    if locator.nth(index).is_visible():
                        return scope
            except Exception:
                continue
        time.sleep(0.1)
    return None


def open_online_payments_tab(page: Page, context: dict):
    """Navigate to the POV Online Payments settings tab and return its scope.

    Hosts both the ACH checkbox (setup) and the offset-card-fees controls (test).
    """
    base = (context.get("base_url") or "").rstrip("/")
    target = f"{base}{ONLINE_PAYMENTS_TAB_PATH}"
    if page.url.rstrip("/") != target:
        page.goto(target, wait_until="domcontentloaded")
    scope = frame_with(page, SAVE_BUTTON, timeout=FAST_UI_TIMEOUT)
    if scope is None:
        raise AssertionError("Online Payments settings tab (save button) did not load")
    return scope


def save_online_payments(scope) -> None:
    """Click the Online Payments tab save button (enabled once a change is pending)."""
    save = scope.locator(SAVE_BUTTON).first
    save.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    save.click(timeout=FAST_UI_TIMEOUT)


def click_via_dom(locator) -> None:
    """DOM-click an element (zero-size inline Vuetify controls aren't actionable).

    Guards against the Playwright default 30s element-resolution hang by checking
    the locator resolves to at least one node before calling evaluate.
    """
    if locator.count() == 0:
        raise AssertionError("click_via_dom target not found")
    locator.first.evaluate("(el) => (el.closest('label') || el).click()")
