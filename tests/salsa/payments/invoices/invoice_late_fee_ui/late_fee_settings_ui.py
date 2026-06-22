"""UI helper to set invoice late-fee settings (invoice_late_fee_ui subcategory).

Migrated from automation-js pages/desktop/Frontage/Settings/lateFee.js (setLateFeeSettings).
The late-fee controls live on the Billing & Invoicing settings page, Invoices & Estimates
tab (`?tab=invoices_and_estimates`). They are Angular-Material controls (md-radio-button),
which on this page render either directly in the angular iframe or in the nested
`#vue-app-tab` frame, so the scope is resolved by locating the late-fee toggle across both
(same fallback shape as taxes_settings).
"""

import time

from playwright.sync_api import Page

UI_TIMEOUT = 5000
PAGE_TIMEOUT = 20000
SAVE_SETTLE_TIMEOUT = 10000

ANGULAR_IFRAME = 'iframe[title="angularjs"]'
VUE_TAB = "#vue-app-tab"

LATE_FEE_ENABLED = '[name="lateFeeEnabled"]'
# Legacy: md-radio-button[value="${isPercent}"] — amount = value "false".
LATE_FEE_AMOUNT_RADIO = '.late-fee-radio-group md-radio-button[value="false"]'
LATE_FEE_AMOUNT_INPUT = '[name="amountFeeType"]'
LATE_FEE_DAYS_INPUT = '[name="lateFeeDays"]'
SAVE_BUTTON = 'button[data-qa="action-button-payments_settings-save"]'
SETTINGS_ENDPOINT = "/v2/settings"


def _angular_scope(page: Page):
    page.locator(ANGULAR_IFRAME).first.wait_for(state="visible", timeout=PAGE_TIMEOUT)
    return page.frame_locator(ANGULAR_IFRAME)


def _candidate_scopes(page: Page):
    """Scopes that may hold the late-fee controls: angular iframe directly, and the
    nested `#vue-app-tab` frame. A missing nested frame raises on access, so callers
    guard each scope individually."""
    angular = _angular_scope(page)
    return (angular, angular.frame_locator(VUE_TAB))


def _has_control(scope) -> bool:
    try:
        return scope.locator(LATE_FEE_ENABLED).count() > 0
    except Exception:
        return False


def open_late_fee_settings(page: Page):
    """Navigate to the Invoices & Estimates settings tab and return the late-fee scope.

    The settings content loads asynchronously (a spinner precedes it), and the controls
    render either directly in the angular iframe or in the nested `#vue-app-tab` frame, so
    both scopes are polled (bounded by the page-load budget) until the toggle appears."""
    if "billing_and_invoicing" not in page.url:
        app_base = page.url.split("/app/")[0]
        page.goto(
            f"{app_base}/app/settings/billing_and_invoicing?tab=invoices_and_estimates",
            wait_until="domcontentloaded",
            timeout=PAGE_TIMEOUT,
        )
        page.wait_for_url("**/billing_and_invoicing**", timeout=PAGE_TIMEOUT,
                          wait_until="domcontentloaded")

    deadline = time.monotonic() + PAGE_TIMEOUT / 1000
    while time.monotonic() < deadline:
        for scope in _candidate_scopes(page):
            if _has_control(scope):
                scope.locator(LATE_FEE_ENABLED).first.wait_for(state="visible", timeout=UI_TIMEOUT)
                return scope
        time.sleep(0.3)
    raise AssertionError("Late-fee settings did not load on the Invoices & Estimates tab")


def _fill(scope, selector: str, value: str) -> None:
    field = scope.locator(selector).first
    field.wait_for(state="visible", timeout=UI_TIMEOUT)
    field.click()
    field.fill("")
    field.type(value, delay=20)


def set_amount_late_fee(page: Page, *, amount: str, days: str) -> None:
    """Enable late fees with a fixed amount fee after N days, then save (legacy
    setLateFeeSettings with type=amount)."""
    scope = open_late_fee_settings(page)

    toggle = scope.locator(LATE_FEE_ENABLED).first
    if (toggle.get_attribute("aria-checked") or "false") != "true":
        toggle.click()

    amount_radio = scope.locator(LATE_FEE_AMOUNT_RADIO).first
    amount_radio.wait_for(state="visible", timeout=UI_TIMEOUT)
    amount_radio.click()

    _fill(scope, LATE_FEE_AMOUNT_INPUT, amount)
    _fill(scope, LATE_FEE_DAYS_INPUT, days)

    save_button = _angular_scope(page).locator(SAVE_BUTTON).first
    save_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    # Confirm persistence by waiting for the settings PUT to succeed (the page is not
    # reloaded, so the DOM alone would not prove the save landed).
    with page.expect_response(
        lambda response: SETTINGS_ENDPOINT in response.url
        and response.request.method not in ("GET", "OPTIONS")
        and response.ok,
        timeout=SAVE_SETTLE_TIMEOUT,
    ):
        save_button.click()


def assert_late_fee_enabled(page: Page) -> None:
    """Re-open the settings tab and assert the late-fee toggle persisted as enabled."""
    scope = open_late_fee_settings(page)
    toggle = scope.locator(LATE_FEE_ENABLED).first
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if (toggle.get_attribute("aria-checked") or "false") == "true":
            return
        time.sleep(0.3)
    raise AssertionError("Late-fee setting did not persist as enabled")
