"""UI flows for the invoice-deposit scenarios (deposits #1 quick-actions, #2 POS).

Records a payment (Quick Actions -> Record payment, custom item), creates and sends an
invoice with a custom line item via Quick Actions, assigns an existing payment as the
invoice deposit, and reads the back-office invoice summary (amount + deposit row).

The Quick Actions menu and the Angular record-payment dialog are POV/Angular top-level
controls; the invoice itemizable dialog renders in `#vue_wizard_iframe` (shared with
estimates, so the dialog helpers are reused from estimates_helpers). All explicit waits
are capped at 5s; the client-page/wizard mounts use a 15s page-readiness budget.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

from tests._functions.login.test import _get_login_context
from tests.salsa.payments.deposits.deposits_api import latest_invoice_for_client
from tests.salsa.sales.estimates.estimates_helpers import (
    add_custom_item,
    billing_scope,
    set_title,
    wizard_scope,
)

FAST_UI_TIMEOUT = 5000
LOAD_TIMEOUT = 15000

# Quick Actions (POV top-level)
QUICK_ACTIONS_BUTTON = '[data-qa="vcMenu-QuickAction"], .quick-actions button'
RECORD_PAYMENT_ITEM = "[data-qa='item-record_payment']"
INVOICE_ITEM = '[data-qa="item-invoice"]'

# Client picker (Angular md-dialog)
PICKER_SEARCH_INPUT = "div.search-clients input"
PICKER_RESULT = '.md-dialog-container [role="list"]:not([ng-hide]) .main-client-info'

# Record-payment dialog (Angular "old" payment dialog)
PAYMENT_TITLE_FIELD = 'input[name="paymentService"]'
CUSTOM_ITEM_OPTION = '.md-autocomplete-suggestions li:has-text("Custom Item")'
CUSTOM_ITEM_NAME = "input[name='custom_item_name']"
AMOUNT_INPUT = ".amount-field input"
RECORD_METHOD_SELECT = "md-select[name='payment_method']"
RECORD_METHOD_OPTION = 'div.md-select-menu-container.md-active md-option:has-text("Cash")'
PAYMENT_CONFIRM = 'button[data-qa="charge-payment"], button[data-qa="save-payment"]'

# Invoice itemizable dialog (#vue_wizard_iframe)
FROM_FOLD = "[data-qa='itemizable-from-fold']"
BILLING_EDIT_BUTTON = "[data-qa='itemizable-from-business-address-edit-button']"
BILLING_TEXTAREA = "[data-qa='itemizable-from-business-address-edit'] textarea"
ASSIGN_DEPOSIT_BUTTON = '[data-qa="assign-deposit-button-text"]'
DEPOSIT_DONE_BUTTON = 'button[data-qa="vc-footer-Done"]'
SEND_BUTTON = "[data-qa='itemizable-dialog-main']"

# Back-office invoice summary
INVOICE_TITLE = "div.summary-header h3"
INVOICE_AMOUNT = "div.summary-header h2 span"
INVOICE_STATE = '[data-qa="payment_status_state"]'
INVOICE_DEPOSIT_SUM = ".deposit-row > .invoice-right-side"


def _app_base(context: dict) -> str:
    return (context.get("base_url") or context.get("app_base_url") or "").rstrip("/")


def _find_control(page: Page, selector: str, timeout: int = FAST_UI_TIMEOUT):
    """Return the first visible match for `selector` across the page and all frames."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for scope in [page, *page.frames]:
            try:
                locator = scope.locator(selector)
                for index in range(locator.count()):
                    candidate = locator.nth(index)
                    if candidate.is_visible():
                        return candidate
            except Exception:
                continue
        time.sleep(0.1)
    return None


def _require(page: Page, selector: str, label: str, timeout: int = FAST_UI_TIMEOUT):
    control = _find_control(page, selector, timeout=timeout)
    if control is None:
        raise AssertionError(f"{label} did not appear")
    return control


def relogin(page: Page, context: dict) -> None:
    """Clear the session and log in fresh so feature-flag changes take effect.

    Feature flags are read into the session at login time (the legacy flow denies POS
    then re-logs in via API). A soft reload keeps the old entitlements, so denying POS
    requires a brand-new session. Clearing cookies sends the app to the central identity
    login (www, "Login to vcita"), whose form differs from the in-app Vue form, so this
    drives that central form directly; the SSO redirect lands back on the app dashboard
    with the updated entitlements.
    """
    try:
        page.evaluate("() => { window.localStorage.clear(); window.sessionStorage.clear(); }")
    except Exception:
        pass
    page.context.clear_cookies()
    # Blank the document first so the running SPA can't client-redirect a
    # cookie-less /app/login to the central (www) identity form.
    page.goto("about:blank")
    page.goto(f"{_app_base(context)}/app/login", wait_until="domcontentloaded")
    # Let the vue_iframe finish (re)mounting before resolving it, else the frame
    # reference detaches mid-fill.
    page.wait_for_timeout(1500)

    form = _get_login_context(page)
    email = form.locator('input[type="email"]')
    email.wait_for(state="visible", timeout=LOAD_TIMEOUT)
    email.fill(context["username"], timeout=FAST_UI_TIMEOUT)
    form.locator('input[type="password"]').fill(context["password"], timeout=FAST_UI_TIMEOUT)
    form.get_by_role("button", name="Log In").click(timeout=FAST_UI_TIMEOUT)

    # The central SSO login + redirect can be slow; absorb that with a generous budget and a
    # single resubmit if we're still parked on the login form (transient submit drop).
    try:
        page.wait_for_url("**/app/dashboard**", timeout=LOAD_TIMEOUT * 3, wait_until="domcontentloaded")
    except Exception:
        if "/login" in page.url:
            form = _get_login_context(page)
            form.get_by_role("button", name="Log In").click(timeout=FAST_UI_TIMEOUT)
        page.wait_for_url("**/app/dashboard**", timeout=LOAD_TIMEOUT * 3, wait_until="domcontentloaded")
    _require(page, QUICK_ACTIONS_BUTTON, "Quick Actions button", timeout=LOAD_TIMEOUT)


def _open_quick_action(page: Page, item_selector: str, label: str) -> None:
    button = _require(page, QUICK_ACTIONS_BUTTON, "Quick Actions button", timeout=LOAD_TIMEOUT)
    button.click(timeout=FAST_UI_TIMEOUT)
    item = _require(page, item_selector, f"{label} quick action")
    item.click(timeout=FAST_UI_TIMEOUT)


def _select_client(page: Page, client_name: str) -> None:
    """Search the Angular client picker and select the matching client."""
    for _ in range(5):
        search = _find_control(page, PICKER_SEARCH_INPUT, timeout=FAST_UI_TIMEOUT)
        if search is None:
            time.sleep(1)
            continue
        search.fill("", timeout=FAST_UI_TIMEOUT)
        search.type(client_name, delay=20)
        result = _find_control(page, PICKER_RESULT, timeout=FAST_UI_TIMEOUT)
        if result is not None:
            result.click(timeout=FAST_UI_TIMEOUT)
            return
        time.sleep(1)
    raise AssertionError(f"Client '{client_name}' did not appear in the picker")


def record_custom_payment(page: Page, context: dict, item_name: str, amount: str) -> None:
    """Record a custom-item payment via Quick Actions -> Record payment (Cash)."""
    client_name = context["deposit_client_name"]
    _open_quick_action(page, RECORD_PAYMENT_ITEM, "Record payment")
    _select_client(page, client_name)

    # Choose "Custom Item" from the title autocomplete, then name + amount.
    title_field = _require(page, PAYMENT_TITLE_FIELD, "Record payment title field")
    title_field.click(timeout=FAST_UI_TIMEOUT)
    title_field.type("Custom Item", delay=20)
    custom_option = _require(page, CUSTOM_ITEM_OPTION, "Custom Item option")
    custom_option.click(timeout=FAST_UI_TIMEOUT)

    name_field = _require(page, CUSTOM_ITEM_NAME, "Custom item name field")
    name_field.fill(item_name, timeout=FAST_UI_TIMEOUT)
    amount_field = _require(page, AMOUNT_INPUT, "Payment amount field")
    amount_field.fill(amount, timeout=FAST_UI_TIMEOUT)

    # Record method defaults to Cash in the legacy flow (enables the confirm button).
    method_select = _require(page, RECORD_METHOD_SELECT, "Record method picker")
    method_select.click(timeout=FAST_UI_TIMEOUT)
    cash_option = _require(page, RECORD_METHOD_OPTION, "Cash record method option")
    cash_option.click(timeout=FAST_UI_TIMEOUT)

    confirm = _require(page, PAYMENT_CONFIRM, "Record payment confirm button")
    confirm.click(timeout=FAST_UI_TIMEOUT)
    # Wait for the dialog to close (payment recorded).
    deadline = time.monotonic() + FAST_UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if _find_control(page, CUSTOM_ITEM_NAME, timeout=300) is None:
            return
        time.sleep(0.2)
    raise AssertionError("Record payment dialog did not close after recording the payment")


def _fill_billing_address(wizard, address: str) -> None:
    """Fill the required From billing address: expand the From fold, enable editing,
    type the address, then collapse the fold to commit it (legacy inputBillingAddress)."""
    wizard.locator(FROM_FOLD).first.click(timeout=FAST_UI_TIMEOUT)
    edit_button = wizard.locator(BILLING_EDIT_BUTTON).first
    edit_button.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    edit_button.click(timeout=FAST_UI_TIMEOUT)
    textarea = wizard.locator(BILLING_TEXTAREA).first
    textarea.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    textarea.fill(address, timeout=FAST_UI_TIMEOUT)
    wizard.locator(FROM_FOLD).first.click(timeout=FAST_UI_TIMEOUT)


def create_invoice_with_deposit(
    page: Page,
    context: dict,
    *,
    title: str,
    item_name: str,
    item_price: str,
    deposit_payment_title: str,
) -> None:
    """Create and send an invoice with a custom item and an assigned deposit payment."""
    client_name = context["deposit_client_name"]
    _open_quick_action(page, INVOICE_ITEM, "Invoice")
    _select_client(page, client_name)

    billing = billing_scope(page)
    wizard = wizard_scope(billing)
    wizard.locator("[data-qa='itemizable-details-header']").first.wait_for(
        state="visible", timeout=LOAD_TIMEOUT
    )

    set_title(wizard, title)
    add_custom_item(wizard, item_name, item_price, save_item=True)
    _fill_billing_address(wizard, "blablablabla")

    # Assign an existing recorded payment as the deposit.
    wizard.locator(ASSIGN_DEPOSIT_BUTTON).first.click(timeout=FAST_UI_TIMEOUT)
    payment_option = wizard.locator(f'[data-qa="{deposit_payment_title}"]')
    payment_option.first.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    payment_option.first.click(timeout=FAST_UI_TIMEOUT)
    wizard.locator(DEPOSIT_DONE_BUTTON).first.click(timeout=FAST_UI_TIMEOUT)

    # Send the invoice.
    wizard.locator(SEND_BUTTON).first.click(timeout=FAST_UI_TIMEOUT)
    page.wait_for_url("**/app/invoices/**", timeout=LOAD_TIMEOUT, wait_until="domcontentloaded")


def assert_invoice_deposit(
    page: Page, context: dict, *, amount: str, deposit_sum: str, state: str
) -> None:
    """Open the client's latest invoice and verify amount, state, and deposit sum."""
    invoice = latest_invoice_for_client(context, context["deposit_client_id"])
    page.goto(
        f"{_app_base(context)}/app/invoices/{invoice['uid']}", wait_until="domcontentloaded"
    )
    billing = billing_scope(page)

    title_el = billing.locator(INVOICE_TITLE).first
    title_el.wait_for(state="visible", timeout=LOAD_TIMEOUT)

    amount_el = billing.locator(INVOICE_AMOUNT).first
    actual_amount = (amount_el.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip()
    if amount not in actual_amount:
        raise AssertionError(f"Invoice amount: expected '{amount}', got '{actual_amount}'")

    state_el = billing.locator(INVOICE_STATE).first
    actual_state = (state_el.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip().rstrip(":")
    if state.upper() not in actual_state.upper():
        raise AssertionError(f"Invoice state: expected '{state}', got '{actual_state}'")

    deposit_el = billing.locator(INVOICE_DEPOSIT_SUM).first
    deposit_el.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    actual_deposit = (deposit_el.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip()
    if deposit_sum not in actual_deposit:
        raise AssertionError(f"Invoice deposit sum: expected '{deposit_sum}', got '{actual_deposit}'")
