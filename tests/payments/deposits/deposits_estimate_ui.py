"""UI flows for the back-office estimate-deposit scenario (deposits #3).

Creates an estimate with a deposit request (createDeposit dialog), reads the back-office
estimate deposit status (DUE/PAID), and runs approve-and-take-payment. Reuses the estimate
itemizable-dialog helpers from estimates_helpers and the cross-frame control finders from
deposits_invoice_ui. All explicit waits are capped at 5s; estimate (re)load points use a
longer page-readiness budget.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

from tests.payments.deposits.deposits_invoice_ui import (
    FAST_UI_TIMEOUT,
    LOAD_TIMEOUT,
    _require,
    _select_client,
)
from tests.sales.estimates.estimates_helpers import (
    NAV_TIMEOUT,
    add_custom_item,
    billing_scope,
    latest_estimate_for_client,
    open_bo_estimate,
    open_estimates_list,
    send_estimate,
    set_billing_address,
    set_title,
    wizard_scope,
)

# Create-deposit dialog (#vue_wizard_iframe)
CREATE_DEPOSIT_BUTTON = '[data-qa="create-deposit-button-text"]'
DEPOSIT_AMOUNT = 'input[data-qa="deposit-amount-value"]'
DEPOSIT_FIXED_TYPE = '[data-qa="deposit-amount-types-item-fixed"]'
DEPOSIT_DISABLE_PAY_ONLINE = 'input[data-qa="deposit-disable-client-pay-online-checkbox"]'
DEPOSIT_DONE = 'button[data-qa="vc-footer-Done"]'

# Back-office estimate deposit status
DEPOSIT_ITEM_VALUE = 'div[data-qa="deposit-item-value"]'
DEPOSIT_ITEM_TEXT_DUE = 'div[data-qa="deposit-item-text"]'
DEPOSIT_ITEM_TEXT_PAID = 'div[data-qa="deposit-item-text-paid"]'

# Approve & take payment
APPROVE_AND_TAKE_PAYMENT = 'button[data-qa="approve_and_take_payment"]'
APPROVE_CHECKBOX_ROOT = '[data-qa="approve-checkbox"]'
APPROVE_CHECKBOX = '[data-qa="approve-checkbox"] .md-container.md-ink-ripple'
DEPOSIT_TAKE_PAYMENT = 'button[data-qa="deposit-take-payment"]'
RECORD_SECTION_BUTTON = '[data-qa="record_payment_button"]'
RECORD_METHOD_SELECT = "md-select[name='payment_method']"
RECORD_METHOD_OPTION = 'div.md-select-menu-container.md-active md-option:has-text("Cash")'
TAKE_PAYMENT_CONFIRM = "[data-qa='take-payment-confirmation'][aria-disabled='false']"


def _open_new_estimate(page: Page, context: dict):
    """Open the new-estimate dialog and pick the client via the shared Angular picker.

    "New -> Estimate" opens the same client-picker-component used by Quick Actions, so this
    reuses the proven `_select_client` helper. Returns (billing, wizard)."""
    open_estimates_list(page)
    billing = billing_scope(page)
    billing.get_by_role("button", name="New").first.click(timeout=FAST_UI_TIMEOUT)
    billing.get_by_role("menuitem", name="Estimate").first.click(timeout=FAST_UI_TIMEOUT)

    # "New -> Estimate" opens the same Angular client-picker-component used by Quick
    # Actions, so reuse the proven picker selectors (div.search-clients input / .main-client-info).
    _select_client(page, context["deposit_client_name"])

    wizard = wizard_scope(billing)
    wizard.locator('[data-qa="itemizable-details-header"]').first.wait_for(
        state="visible", timeout=NAV_TIMEOUT
    )
    return billing, wizard


def _create_deposit_request(wizard, amount: str, can_client_pay: bool) -> None:
    wizard.locator(CREATE_DEPOSIT_BUTTON).first.click(timeout=FAST_UI_TIMEOUT)
    amount_field = wizard.locator(DEPOSIT_AMOUNT).first
    amount_field.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    amount_field.fill(amount, timeout=FAST_UI_TIMEOUT)
    wizard.locator(DEPOSIT_FIXED_TYPE).first.click(timeout=FAST_UI_TIMEOUT)
    if not can_client_pay:
        # Hidden Vuetify checkbox; toggle natively (estimates_helpers pattern).
        checkbox = wizard.locator(DEPOSIT_DISABLE_PAY_ONLINE).first
        checkbox.wait_for(state="attached", timeout=FAST_UI_TIMEOUT)
        checkbox.evaluate("el => el.click()")
    wizard.locator(DEPOSIT_DONE).first.click(timeout=FAST_UI_TIMEOUT)


def create_estimate_with_deposit(
    page: Page,
    context: dict,
    *,
    title: str,
    item_name: str,
    item_price: str,
    address: str,
    deposit_amount: str,
    can_client_pay: bool = True,
) -> str:
    """Create and send an estimate with a fixed deposit request. Returns the estimate uid."""
    _billing, wizard = _open_new_estimate(page, context)
    set_title(wizard, title)
    add_custom_item(wizard, item_name, item_price, save_item=False)
    set_billing_address(wizard, address)
    _create_deposit_request(wizard, deposit_amount, can_client_pay)
    send_estimate(wizard)
    page.wait_for_url("**/app/payments/estimates/**", timeout=LOAD_TIMEOUT, wait_until="domcontentloaded")
    return latest_estimate_for_client(context, context["deposit_client_id"])["uid"]


TAKE_PAYMENT_DIALOG = "md-dialog.take-payment-wrapper, md-dialog.close-balance-content"


def _wait_take_payment_done(page: Page) -> None:
    """Wait until the Take Payment dialog closes (payment + approval persisted)."""
    page.locator(TAKE_PAYMENT_DIALOG).first.wait_for(state="hidden", timeout=LOAD_TIMEOUT)


def approve_and_take_payment(page: Page, context: dict, estimate_uid: str) -> None:
    """Approve the estimate and record the deposit payment as Cash (back office)."""
    open_bo_estimate(page, context, estimate_uid)
    _require(page, APPROVE_AND_TAKE_PAYMENT, "Approve & take payment button", timeout=LOAD_TIMEOUT).click(
        timeout=FAST_UI_TIMEOUT
    )
    # The approve checkbox defaults to checked; clicking it unconditionally would toggle it
    # OFF (deposit still gets paid, but the estimate stays SENT). Mirror legacy enableCheckbox:
    # only click when it is not already checked.
    # The approve consent checkbox gates whether the estimate is actually approved (vs. just
    # recording the deposit payment). A normal click on the md-checkbox ripple does not toggle
    # the Angular ng-model, so JS-click the ripple (legacy enableCheckbox pattern) and confirm
    # aria-checked flips to true before continuing.
    root = _require(page, APPROVE_CHECKBOX_ROOT, "Approve checkbox")
    if (root.get_attribute("aria-checked") or "").lower() != "true":
        _require(page, APPROVE_CHECKBOX, "Approve checkbox ripple").evaluate("el => el.click()")
        deadline = time.monotonic() + FAST_UI_TIMEOUT / 1000
        while time.monotonic() < deadline:
            if (root.get_attribute("aria-checked") or "").lower() == "true":
                break
            time.sleep(0.2)
        else:
            raise AssertionError("Approve consent checkbox did not become checked")
    # aria-checked flips before Angular commits the `consent` model to scope; clicking TAKE
    # PAYMENT in the same tick occasionally records the deposit without approving (estimate
    # stays SENT). Let the digest settle and re-confirm consent before proceeding.
    page.wait_for_timeout(800)
    if (root.get_attribute("aria-checked") or "").lower() != "true":
        raise AssertionError("Approve consent checkbox did not stay checked")
    _require(page, DEPOSIT_TAKE_PAYMENT, "Deposit take-payment button").click(timeout=FAST_UI_TIMEOUT)
    _require(page, RECORD_SECTION_BUTTON, "Record payment section button").click(timeout=FAST_UI_TIMEOUT)
    _require(page, RECORD_METHOD_SELECT, "Record method picker").click(timeout=FAST_UI_TIMEOUT)
    _require(page, RECORD_METHOD_OPTION, "Cash record method option").click(timeout=FAST_UI_TIMEOUT)
    confirm = _require(page, TAKE_PAYMENT_CONFIRM, "Take payment confirm button")
    confirm.click(timeout=FAST_UI_TIMEOUT)
    # Recording the deposit also approves the estimate, but the approval POST is still in flight
    # when the Take Payment dialog closes. Navigating (reloading the estimate) at that point
    # cancels the approval XHR, so the deposit is PAID but the estimate stays SENT. Wait for the
    # dialog to close, then settle (no navigation) so the approval request completes first.
    _wait_take_payment_done(page)
    # networkidle rarely fires on this SPA (background polling), so cap it low; the real safety
    # net is the reload-poll in assert_bo_estimate_deposit. Keep a short settle so the in-flight
    # approval POST is not cancelled by the next navigation.
    try:
        page.wait_for_load_state("networkidle", timeout=4000)
    except Exception:
        pass
    page.wait_for_timeout(1500)


def assert_bo_estimate_deposit(
    page: Page, context: dict, estimate_uid: str, *, estimate_state: str, deposit_state: str, deposit_amount: str
) -> None:
    """Open the back-office estimate and verify its state plus the deposit state and amount."""
    billing = open_bo_estimate(page, context, estimate_uid)

    text_sel = DEPOSIT_ITEM_TEXT_DUE if deposit_state.upper() == "DUE" else DEPOSIT_ITEM_TEXT_PAID
    text_el = billing.locator(text_sel).first
    text_el.wait_for(state="visible", timeout=LOAD_TIMEOUT)

    amount_el = billing.locator(DEPOSIT_ITEM_VALUE).first
    amount_el.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    actual_amount = (amount_el.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip()
    if deposit_amount not in actual_amount:
        raise AssertionError(f"Deposit amount: expected '{deposit_amount}', got '{actual_amount}'")

    # The estimate state change (e.g. SENT -> APPROVED) lands asynchronously after the deposit
    # is recorded, and the BO view does not always self-refresh, so re-open the estimate between
    # polls until the expected state appears.
    deadline = time.monotonic() + LOAD_TIMEOUT * 2 / 1000
    while time.monotonic() < deadline:
        if estimate_state.upper() in _all_frames_text(page).upper():
            return
        time.sleep(1.0)
        open_bo_estimate(page, context, estimate_uid)
    raise AssertionError(f"Estimate state '{estimate_state}' not found in back-office view")


def _all_frames_text(page: Page) -> str:
    """Concatenate body text from every attached frame, skipping frames that detach mid-read."""
    parts = []
    for frame in page.frames:
        try:
            body = frame.locator("body")
            if body.count() > 0:
                parts.append(body.inner_text(timeout=FAST_UI_TIMEOUT))
        except Exception:
            continue
    return "\n".join(parts)
