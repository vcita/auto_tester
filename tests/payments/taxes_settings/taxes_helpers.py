"""UI helpers for the taxes_settings subcategory.

The Taxes settings live in a Vue app (`#vue-app-tab`) nested inside the frontage
angular iframe. Tax rows expose stable `data-qa="line-tax-{name}-{rate}"` markers,
so all create/edit/delete/list assertions key off those.
"""

import re
import time

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

UI_TIMEOUT = 15000
PAGE_TIMEOUT = 20000
TOAST_TIMEOUT = 8000
LIST_SETTLE_SECONDS = 5

SAVE_BUTTON = 'button[data-qa="action-button-payments_settings-save"]'
ADD_TAX_BUTTON = ".add-tax"
NEW_ROW = 'div[data-qa="line-tax-undefined-undefined"]'
TAX_NAME_INPUT = 'input[data-qa="tax-name"]'
TAX_RATE_INPUT = 'input[data-qa="tax-rate"]'
SUCCESS_TOAST = '.v-snack--active .success, [data-qa="success-toast"], md-toast.announce'


def _angular_scope(page: Page):
    page.locator('iframe[title="angularjs"]').first.wait_for(state="visible", timeout=UI_TIMEOUT)
    return page.frame_locator('iframe[title="angularjs"]')


def taxes_scope(page: Page):
    """Resolve the scope that holds the tax rows (nested vue iframe, with angular fallback)."""
    angular = _angular_scope(page)
    if angular.locator("#vue-app-tab").count() > 0:
        return angular.frame_locator("#vue-app-tab")
    return angular


def open_taxes_settings(page: Page):
    """Navigate to the Taxes tab in Billing & Invoicing and return the tax-rows scope."""
    if "billing_and_invoicing" not in page.url:
        app_base = page.url.split("/app/")[0]
        page.goto(
            f"{app_base}/app/settings/billing_and_invoicing?tab=taxes",
            wait_until="domcontentloaded",
            timeout=PAGE_TIMEOUT,
        )
        page.wait_for_url("**/billing_and_invoicing**", timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")

    scope = taxes_scope(page)
    try:
        scope.locator(ADD_TAX_BUTTON).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    except PlaywrightTimeoutError:
        _select_taxes_tab(page)
        scope = taxes_scope(page)
        scope.locator(ADD_TAX_BUTTON).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    return scope


def _select_taxes_tab(page: Page) -> None:
    tab = _angular_scope(page).get_by_role("tab", name=re.compile(r"^Taxes"))
    tab.wait_for(state="visible", timeout=UI_TIMEOUT)
    tab.click()


def _row(scope, name: str, rate: str):
    return scope.locator(f'div[data-qa="line-tax-{name}-{rate}"]')


def _resolve_handle(locator):
    # A tax row's data-qa mutates as its name/rate change, so a value-scoped locator
    # goes stale mid-edit. Resolve the input to an element handle (which survives
    # attribute changes) up front and operate on that.
    locator.wait_for(state="visible", timeout=UI_TIMEOUT)
    handle = locator.element_handle()
    if handle is None:
        raise AssertionError("Could not resolve a tax input element handle")
    return handle


def _set_value(handle, value: str) -> None:
    handle.click()
    handle.fill("")
    handle.type(value, delay=20)


def add_tax(scope, name: str, rate: str) -> None:
    scope.locator(ADD_TAX_BUTTON).first.click()
    new_row = scope.locator(NEW_ROW)
    new_row.wait_for(state="visible", timeout=UI_TIMEOUT)
    name_input = _resolve_handle(new_row.locator(TAX_NAME_INPUT))
    rate_input = _resolve_handle(new_row.locator(TAX_RATE_INPUT))
    _set_value(name_input, name)
    _set_value(rate_input, rate)
    _row(scope, name, rate).wait_for(state="visible", timeout=UI_TIMEOUT)


def edit_tax(scope, current_name: str, current_rate: str, name: str, rate: str) -> None:
    row = _row(scope, current_name, current_rate)
    name_input = _resolve_handle(row.locator(TAX_NAME_INPUT))
    rate_input = _resolve_handle(row.locator(TAX_RATE_INPUT))
    _set_value(name_input, name)
    _set_value(rate_input, rate)
    _row(scope, name, rate).wait_for(state="visible", timeout=UI_TIMEOUT)


def delete_tax(scope, name: str, rate: str) -> None:
    _row(scope, name, rate).locator('[data-qa="tax-delete"]').click()
    scope.locator('[data-qa="tax-menu-actions-0"]').first.click()
    _row(scope, name, rate).wait_for(state="hidden", timeout=UI_TIMEOUT)


def save_changes(page: Page) -> None:
    save_button = _angular_scope(page).locator(SAVE_BUTTON)
    save_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    save_button.click()
    _wait_for_save_toast(page)


def _wait_for_save_toast(page: Page) -> None:
    toast = _angular_scope(page).locator(SUCCESS_TOAST)
    try:
        toast.first.wait_for(state="visible", timeout=TOAST_TIMEOUT)
    except PlaywrightTimeoutError:
        return
    try:
        toast.first.wait_for(state="hidden", timeout=TOAST_TIMEOUT)
    except PlaywrightTimeoutError:
        pass


def list_taxes(scope) -> list:
    rows = scope.locator(
        'div[data-qa*="line-tax-"]:not([data-qa="line-tax-undefined-undefined"])'
    )
    return [rows.nth(index).get_attribute("data-qa") for index in range(rows.count())]


def assert_taxes(page: Page, expected: list) -> None:
    deadline = time.monotonic() + LIST_SETTLE_SECONDS
    actual = []
    while time.monotonic() < deadline:
        actual = list_taxes(taxes_scope(page))
        if actual == expected:
            return
        time.sleep(0.5)
    raise AssertionError(f"Expected taxes list {expected}, got {actual}")


def set_tax_mode(page: Page, scope, mode: str) -> None:
    radio = scope.locator(f'[data-qa="radio-{mode}"]')
    radio.wait_for(state="visible", timeout=UI_TIMEOUT)
    radio.click()
    save_changes(page)


def assert_tax_mode(page: Page, mode: str) -> None:
    selected = taxes_scope(page).locator(".v-item--active .label-container")
    selected.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    data_qa = selected.first.get_attribute("data-qa") or ""
    actual = data_qa.split("-")[1] if "-" in data_qa else data_qa
    if actual != mode:
        raise AssertionError(f"Expected tax mode '{mode}', got '{actual}' (data-qa='{data_qa}')")
