"""Shared UI helpers for the payments_emails migration (VCITA2-14027).

Low-level take-payment dialog primitives (frame-scanning, send-receipt, record
method, amount) plus the three "send payment-request link by email" flows the
feature exercises:

- ``send_appointment_payment_link`` - appointment payment-status card, non-POS
  (legacy PaymentStatusCard.sendPaymentLink -> setCurrentStage('send')).
- ``send_appointment_link_via_pos`` - POS checkout "send-link" action.
- ``send_invoice_payment_link`` - invoice detail, newTakePayment "send" stage.

Each opens the take-payment dialog, picks the **email** channel, confirms, and
closes. Controls are resolved across the page and all frames (the dialog renders
inside the POV/Angular iframe), reusing the deposits ``_find_control``/``_require``
scanners. Element waits stay <=5s; navigation/iframe mounts use the bounded
LOAD/PAGE budgets (documented nested-iframe exceptions).
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

from tests.payments.appointment_payments.appointment_payments_helpers import open_appointment
from tests.payments.deposits.deposits_api import latest_invoice_for_client
from tests.payments.deposits.deposits_invoice_ui import (
    FAST_UI_TIMEOUT,
    LOAD_TIMEOUT,
    _find_control,
    _require,
)
from tests.payments.event_payments.event_payments_helpers import (
    PAGE_TIMEOUT,
    TAKE_PAYMENT_BTN,
    app_base,
)

# Take-payment dialog (shared by send-link + record flows)
TAKE_PAYMENT_DIALOG = "md-dialog.take-payment-wrapper, md-dialog.close-balance-content"
TAKE_PAYMENT_CONFIRM = '[data-qa="take-payment-confirmation"][aria-disabled="false"]'
DONE_BTN = "div.md-dialog-container button.gray-btn"
SEND_RECEIPT_CHECKBOX = 'md-checkbox[aria-label="Send receipt to client"]'

# Record section + method picker
RECORD_SECTION_BTN = '[data-qa="record_payment_button"], [data-qa="record"]'
METHOD_SELECT = "md-select[name='payment_method']"
AMOUNT_INPUT = "input.amount-input:visible, input[name='money_amount']:visible"

# Send-link stages
SEND_STAGE_BTN = "button[ng-click=\"setCurrentStage('send')\"]"
TAKE_PAYMENT_SEND_BTN = 'button[data-qa="send"]'
EMAIL_OPTION = ".channel-option.email-option md-radio-button"

# POS checkout (POV top-level)
POS_CHECKOUT_ACTIVATOR = '[data-qa="checkout-actions-activator"]'
POS_CHECKOUT_SEND = '[data-qa="checkout-action-send"]'
POS_CHECKOUT_RECORD = '[data-qa="checkout-action-record"]'
POS_TAKE_PAYMENT_ITEM = '[data-qa="VcLargeQuickAction-point_of_sale"]'
POS_ADD_OPEN_REQUESTS = '.client-details-container [role="alert"] [type="button"]'


def method_option(method: str) -> str:
    return f'div.md-select-menu-container.md-active md-option:has-text("{method}")'


MD_SELECT_MENU = "div.md-select-menu-container.md-active"


def choose_record_method(page: Page, method: str = "Cash") -> None:
    """Open the record-method picker and select ``method`` (Cash / ACH).

    Waits for the md-select menu (and its backdrop) to close after selection so the
    overlay does not intercept the subsequent confirm click."""
    _require(page, METHOD_SELECT, "record method picker").click(timeout=FAST_UI_TIMEOUT)
    option = _require(page, method_option(method), f"{method} record option")
    option.evaluate("el => el.click()")
    _wait_menu_closed(page)


def _wait_menu_closed(page: Page) -> None:
    """Bounded wait for the md-select dropdown overlay to disappear."""
    deadline = time.monotonic() + FAST_UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if _find_control(page, MD_SELECT_MENU, timeout=300) is None:
            return
        time.sleep(0.15)


def fill_amount(page: Page, amount: str) -> None:
    """Fill the masked money input (keystrokes only; clear then type, commit on Tab)."""
    amount_input = _require(page, AMOUNT_INPUT, "record amount input")
    amount_input.click(timeout=FAST_UI_TIMEOUT)
    amount_input.press("Meta+A")
    amount_input.press("Backspace")
    amount_input.press_sequentially(str(amount), delay=50)
    amount_input.press("Tab")


def ensure_send_receipt(page: Page) -> None:
    """Make sure the 'Send receipt to client' checkbox is checked (idempotent).

    Mirrors the legacy ``_sendReceiptToClientCheckbox(true)`` so recording a payment
    sends the client the Payment Confirmation email."""
    checkbox = _find_control(page, SEND_RECEIPT_CHECKBOX, timeout=FAST_UI_TIMEOUT)
    if checkbox is None:
        return
    try:
        if (checkbox.get_attribute("aria-checked") or "").lower() != "true":
            checkbox.click(timeout=FAST_UI_TIMEOUT)
    except Exception:
        pass


def _dialog_open(page: Page) -> bool:
    return _find_control(page, TAKE_PAYMENT_DIALOG, timeout=300) is not None


def wait_dialog_closed(page: Page, label: str = "take payment") -> None:
    deadline = time.monotonic() + LOAD_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if not _dialog_open(page):
            return
        time.sleep(0.2)
    raise AssertionError(f"{label} dialog did not close")


def confirm_take_payment(page: Page, label: str = "take payment") -> None:
    """Click the take-payment confirm (Record/Charge) and wait for the dialog to close.

    If the dialog is still open after a short grace window (the first click can land
    while an md-select overlay is still dismissing), the confirm is clicked once more
    (bounded single retry) before the full close wait."""
    _wait_menu_closed(page)
    _require(page, TAKE_PAYMENT_CONFIRM, f"{label} confirm").click(timeout=FAST_UI_TIMEOUT)
    grace = time.monotonic() + 3
    while time.monotonic() < grace:
        if not _dialog_open(page):
            return
        time.sleep(0.2)
    confirm = _find_control(page, TAKE_PAYMENT_CONFIRM, timeout=FAST_UI_TIMEOUT)
    if confirm is not None:
        try:
            confirm.click(timeout=FAST_UI_TIMEOUT)
        except Exception:
            pass
    wait_dialog_closed(page, label)


def _complete_send_link(page: Page) -> None:
    """Pick the email channel, confirm, and close the take-payment dialog."""
    _require(page, EMAIL_OPTION, "email channel option", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _require(page, TAKE_PAYMENT_CONFIRM, "send-link confirm").click(timeout=FAST_UI_TIMEOUT)
    done = _find_control(page, DONE_BTN, timeout=FAST_UI_TIMEOUT)
    if done is not None:
        try:
            done.click(timeout=FAST_UI_TIMEOUT)
        except Exception:
            pass


def send_appointment_payment_link(page: Page, context: dict, identifier: str) -> None:
    """Send the appointment payment-request link by email (non-POS dialog)."""
    open_appointment(page, context, identifier)
    _require(page, TAKE_PAYMENT_BTN, "appointment take payment", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _require(page, SEND_STAGE_BTN, "send-link stage button", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _complete_send_link(page)


def send_appointment_link_via_pos(page: Page, context: dict, identifier: str) -> None:
    """Send the appointment payment-request link by email through POS checkout."""
    open_appointment(page, context, identifier)
    _require(page, TAKE_PAYMENT_BTN, "appointment take payment", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_CHECKOUT_ACTIVATOR, "POS checkout activator", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_CHECKOUT_SEND, "POS send-link action").click(timeout=FAST_UI_TIMEOUT)
    _require(page, TAKE_PAYMENT_DIALOG, "take payment dialog", timeout=LOAD_TIMEOUT)
    _complete_send_link(page)


def open_latest_invoice(page: Page, context: dict, client_id: str) -> dict:
    """Open the client's newest invoice detail page (ready for take-payment)."""
    invoice = latest_invoice_for_client(context, client_id)
    page.goto(f"{app_base(context)}/app/invoices/{invoice['uid']}",
              wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    _require(page, TAKE_PAYMENT_BTN, "invoice detail take payment", timeout=LOAD_TIMEOUT)
    return invoice


def send_invoice_payment_link(page: Page, context: dict, client_id: str) -> None:
    """Send the invoice payment-request link by email (newTakePayment 'send' stage)."""
    open_latest_invoice(page, context, client_id)
    _require(page, TAKE_PAYMENT_BTN, "invoice take payment", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _require(page, TAKE_PAYMENT_SEND_BTN, "newTakePayment send button", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _complete_send_link(page)
