"""UI helpers for the Payment Settings migration (VCITA2-13901).

The payment settings page (`/app/settings/payments`) renders POV/Angular components
across nested frames, so element lookups scan the page frames for the target data-qa
(mirroring the tips_gateway providers-dialog frame scan). Only the bits the legacy
scenarios assert in the UI live here: the terms-and-policies textarea value and the
online-payments provider banner; all settings writes are done via the API.

Selector policy: data-qa first (legacy POV `terms-and-policies-tab-text-area`,
`online-payments-tab-banner`). Element waits are capped at 5s; page (re)navigation gets
the longer NAV budget because the settings page mounts nested frames.
"""

import time

from playwright.sync_api import Page

UI_TIMEOUT = 5000
NAV_TIMEOUT = 20000

TERMS_TEXTAREA = '[data-qa="terms-and-policies-tab-text-area"]'
PROVIDER_BANNER = '[data-qa="online-payments-tab-banner"]'


def _app_base(context: dict) -> str:
    return (context.get("base_url") or context.get("app_base_url") or "").rstrip("/")


def _find_in_frames(page: Page, selector: str, timeout: int = NAV_TIMEOUT):
    """Return the first frame containing `selector` (the settings page mounts nested frames)."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(selector).count() > 0:
                    return frame
            except Exception:
                continue
        time.sleep(0.2)
    return None


def goto_payments_settings(page: Page, context: dict, tab: str | None = None) -> None:
    url = f"{_app_base(context)}/app/settings/payments"
    if tab:
        url += f"?tab={tab}"
    page.goto(url, wait_until="domcontentloaded")


def read_terms_text(page: Page, context: dict) -> str:
    """Navigate to the terms-and-policies tab and read the textarea value."""
    goto_payments_settings(page, context, tab="terms-and-policies")
    frame = _find_in_frames(page, TERMS_TEXTAREA)
    if frame is None:
        raise AssertionError("Terms-and-policies textarea did not render on the settings page")
    textarea = frame.locator(TERMS_TEXTAREA).first
    textarea.wait_for(state="visible", timeout=UI_TIMEOUT)
    return (textarea.input_value(timeout=UI_TIMEOUT) or "").strip()


def assert_provider_banner_displayed(page: Page, context: dict) -> None:
    """Assert the online-payments provider banner is displayed on the payments settings page."""
    goto_payments_settings(page, context)
    frame = _find_in_frames(page, PROVIDER_BANNER)
    if frame is None:
        raise AssertionError("Online-payments provider banner did not appear on the settings page")
    frame.locator(PROVIDER_BANNER).first.wait_for(state="visible", timeout=UI_TIMEOUT)
