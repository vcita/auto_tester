"""Shared UI helpers for the tips_settings subcategories.

Tips tab navigation and assertions (POV). All explicit waits honor the 5s
autotester cap. The mock-gateway connection flow lives in :mod:`tips_gateway`.
"""

import time

from playwright.sync_api import Page, expect

FAST_UI_TIMEOUT = 5000

TIPS_TAB = '[data-qa="tips-tab"]'
NO_GATEWAY_ALERT = '[data-qa="tips-tab-no-gateway-alert"]'
TIP_AMOUNT_1 = '[data-qa="tips-tab-amount-1"]'
PREVIEW_AMOUNT = ".tips-preview__tip-option-amount"


def scope_with(page: Page, selector: str, timeout: int = FAST_UI_TIMEOUT):
    """Return the first frame (POV is top-level, but content can nest) that contains selector."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(selector).count() > 0:
                    return frame
            except Exception:
                continue
        time.sleep(0.1)
    return None


def clear_profile_cache(page: Page) -> None:
    """Drop the cached account profile (localStorage account_* keys) so the POV re-fetches
    fresh settings on the next load. Mirrors the legacy clearProfileCache after a settings API call.
    """
    try:
        page.evaluate(
            "() => { Object.keys(localStorage)"
            ".filter((k) => k.startsWith('account_'))"
            ".forEach((k) => localStorage.removeItem(k)); }"
        )
    except Exception as error:
        print(f"  [debug] clear_profile_cache skipped (localStorage unavailable): {error}")


def _tips_url(context: dict) -> str:
    base = (context.get("base_url") or "").rstrip("/")
    if not base:
        raise ValueError("base_url missing from context")
    return f"{base}/app/settings/payments?tab=tips"


def open_tips_settings(page: Page, context: dict):
    """Navigate to the tips tab and return the frame/scope that holds it."""
    page.goto(_tips_url(context), wait_until="domcontentloaded")
    scope = scope_with(page, TIPS_TAB)
    if scope is None:
        raise AssertionError("Tips tab did not render at /app/settings/payments?tab=tips")
    scope.locator(TIPS_TAB).first.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    return scope


def get_tips_status(scope) -> str:
    """Resolve 'disabled' (no-gateway alert) or 'enabled' (tip amount inputs present)."""
    deadline = time.monotonic() + FAST_UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if scope.locator(NO_GATEWAY_ALERT).count() > 0 and scope.locator(NO_GATEWAY_ALERT).first.is_visible():
            return "disabled"
        if scope.locator(TIP_AMOUNT_1).count() > 0 and scope.locator(TIP_AMOUNT_1).first.is_visible():
            return "enabled"
        time.sleep(0.1)
    raise AssertionError("Tips settings status did not resolve to enabled or disabled")


def _read_preview_amounts(scope) -> list:
    amounts = scope.locator(PREVIEW_AMOUNT)
    texts = []
    for index in range(amounts.count()):
        text = (amounts.nth(index).inner_text() or "").strip()
        if text:
            texts.append(text)
    return texts


def get_preview_amounts(scope, expected: list = None) -> list:
    """Return the preview tip-option amounts (e.g. ['$55.00','$66.00','$77.00']).

    The preview renders default tips first and updates once the store re-fetches the saved
    settings, so when ``expected`` is provided the read is polled until it matches (within
    the UI cap) to avoid the transient default-values race.
    """
    expect(scope.locator(PREVIEW_AMOUNT).first).to_be_visible(timeout=FAST_UI_TIMEOUT)
    if expected is None:
        return _read_preview_amounts(scope)
    deadline = time.monotonic() + FAST_UI_TIMEOUT / 1000
    texts = _read_preview_amounts(scope)
    while time.monotonic() < deadline:
        texts = _read_preview_amounts(scope)
        if texts == expected:
            return texts
        time.sleep(0.1)
    return texts
