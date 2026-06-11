"""Payment-confirmation + estimate-CP UI helpers for payments_emails (VCITA2-14027).

The confirmation scenarios record a payment (so the client gets a Payment
Confirmation email): pay an appointment (non-POS record), close a client's balance
(record / ACH), and record via POS (existing request + all open requests for a
client). Each ensures the "Send receipt to client" checkbox is checked, mirroring
the legacy take-payment flow.

``assert_cp_estimate_from_email`` opens the client-portal estimate link extracted
from the "New estimate from ..." email in a fresh browser context and asserts the
estimate entity page (title, price, client, items, pending-action buttons).
"""

from __future__ import annotations

import re
import time

from playwright.sync_api import Page

from tests.payments.appointment_payments.appointment_payments_helpers import (
    _open_appt_via_orders,
    open_appointment,
)
from tests.payments.deposits.deposits_invoice_ui import (
    FAST_UI_TIMEOUT,
    LOAD_TIMEOUT,
    QUICK_ACTIONS_BUTTON,
    _find_control,
    _require,
    _select_client,
)
from tests.payments.event_payments.event_payments_helpers import (
    CP_NAV_TIMEOUT,
    PAGE_TIMEOUT,
    TAKE_PAYMENT_BTN,
    app_base,
)
from tests.payments.payments_emails.payments_emails_helpers import (
    POS_ADD_OPEN_REQUESTS,
    POS_CHECKOUT_ACTIVATOR,
    POS_CHECKOUT_RECORD,
    POS_TAKE_PAYMENT_ITEM,
    RECORD_SECTION_BTN,
    TAKE_PAYMENT_DIALOG,
    choose_record_method,
    confirm_take_payment,
    ensure_send_receipt,
    fill_amount,
)

CLIENT_TAKE_PAYMENT_BTN = '[data-qa="action-button-matter_page-take_payment"][aria-disabled="false"]'
CP_IFRAME = "#cp_iframe"
CP_ESTIMATE_PAGE = ".payment-entity-page, span.payment-title"
POS_BILLABLE_ITEM = ".billable-item-container__name"
POS_ITEM_CONTAINER = ".billable-item-container"
POS_ITEM_NAME = ".billable-item-container__name"
POS_ITEM_REMOVE = '[data-qa="item-action-desktop-remove"]'
POS_CONFIRM_REMOVE = '[data-qa="vc-footer-Yes, remove"]'


def pay_appointment_with_receipt(page: Page, context: dict, amount: str, identifier: str) -> None:
    """Record a Cash payment against an appointment (non-POS) and send the receipt."""
    open_appointment(page, context, identifier)
    _require(page, TAKE_PAYMENT_BTN, "appointment take payment", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _require(page, RECORD_SECTION_BTN, "record-payment section", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    fill_amount(page, amount)
    choose_record_method(page, "Cash")
    ensure_send_receipt(page)
    confirm_take_payment(page, "record payment")


def close_client_balance(page: Page, context: dict, client_id: str, *, method: str = "ACH") -> None:
    """Close the client's outstanding balance from the client card (record / ACH).

    The client matter page's take-payment action opens the close-balance dialog
    pre-loaded with the balance, so no amount is entered."""
    page.goto(f"{app_base(context)}/app/clients/{client_id}",
              wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    _require(page, CLIENT_TAKE_PAYMENT_BTN, "client close-balance take payment",
             timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _require(page, RECORD_SECTION_BTN, "record-payment section", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    choose_record_method(page, method)
    ensure_send_receipt(page)
    confirm_take_payment(page, "close balance")


def _complete_pos_record(page: Page) -> None:
    """Cash method -> send receipt -> confirm, on an open POS take-payment dialog."""
    choose_record_method(page, "Cash")
    ensure_send_receipt(page)
    confirm_take_payment(page, "POS record")


def _pos_record_cash(page: Page) -> None:
    """Checkout -> Record payment -> Cash -> send receipt -> confirm (single-item sale)."""
    _require(page, POS_BILLABLE_ITEM, "POS checkout item", timeout=LOAD_TIMEOUT)
    if not _open_pos_record_dialog(page, dialog_timeout=LOAD_TIMEOUT):
        raise AssertionError("POS take-payment dialog did not appear")
    _complete_pos_record(page)


def _open_pos_record_dialog(page: Page, *, dialog_timeout: int = FAST_UI_TIMEOUT) -> bool:
    """Open the checkout actions menu, pick Record, and report whether the dialog shows.

    Both the activator and the menu item are clicked via JS: recording the prior
    payment leaves a transient Angular Material backdrop over the page that intercepts
    a real pointer click on the (otherwise enabled) Vue checkout button, so a synthetic
    click is the reliable path for these SPA controls (per the project's Vue/Angular
    click guidance)."""
    activator = _require(page, POS_CHECKOUT_ACTIVATOR, "POS checkout activator", timeout=LOAD_TIMEOUT)
    activator.evaluate("el => el.click()")
    record = _find_control(page, POS_CHECKOUT_RECORD, timeout=FAST_UI_TIMEOUT)
    if record is not None:
        record.evaluate("el => el.click()")
    return _find_control(page, TAKE_PAYMENT_DIALOG, timeout=dialog_timeout) is not None


def record_appointment_via_pos(page: Page, context: dict, identifier: str) -> None:
    """Record the service's existing payment request via its Billing & Invoicing
    order -> POS (mirrors legacy goToOrder + continuePosAndSelectItems('record-payment')).

    Routing through the order fulfils that specific require-to-pay request, so the
    client's only remaining open request afterwards is the assigned product - matching
    the legacy POS cart for the follow-up "record all open requests" step. (Opening the
    appointment directly instead records an ad-hoc sale that leaves the request open,
    which then double-loads the service into the next sale and stalls the checkout.)"""
    service_name = context["appointment_payments"]["service"]["name"]
    frame = _open_appt_via_orders(page, context, service_name)
    frame.locator(TAKE_PAYMENT_BTN).first.click(timeout=FAST_UI_TIMEOUT)
    _pos_record_cash(page)


def _drop_pos_line(page: Page, name: str) -> bool:
    """Remove one POS sale line whose item name equals ``name``; return True if removed.

    The per-line remove control is only mounted on hover, so hover the line first
    (matches the legacy removeItemFromSale flow)."""
    for scope in [page, *page.frames]:
        try:
            lines = scope.locator(POS_ITEM_CONTAINER)
            count = lines.count()
        except Exception:
            continue
        for index in range(count):
            line = lines.nth(index)
            try:
                title = line.locator(POS_ITEM_NAME).first
                if not title.count() or title.inner_text().strip() != name:
                    continue
                title.hover(timeout=FAST_UI_TIMEOUT)
                remove = line.locator(POS_ITEM_REMOVE).first
                remove.wait_for(state="attached", timeout=FAST_UI_TIMEOUT)
                remove.click(force=True, timeout=FAST_UI_TIMEOUT)
                confirm = _find_control(page, POS_CONFIRM_REMOVE, timeout=FAST_UI_TIMEOUT)
                if confirm is not None:
                    confirm.click(force=True, timeout=FAST_UI_TIMEOUT)
                return True
            except Exception:
                continue
    return False


def record_for_client_via_pos(page: Page, context: dict, client_name: str) -> None:
    """Open POS for a client, add all open requests, and record a Cash payment.

    "Add all open requests" can re-offer the appointment whose request was already
    recorded in Step 1 (added asynchronously, a moment after the product). A sale that
    still contains that already-paid require-to-pay line never finishes computing its
    checkout total, so the take-payment dialog never opens. We therefore detect the
    stall (dialog absent) and drop the stale appointment line, then retry - leaving the
    client's genuinely-open product request, which is what the legacy step settles."""
    _require(page, QUICK_ACTIONS_BUTTON, "Quick Actions button", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_TAKE_PAYMENT_ITEM, "POS quick action", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _select_client(page, client_name)
    _require(page, POS_ADD_OPEN_REQUESTS, "add all open requests", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_BILLABLE_ITEM, "POS checkout item", timeout=LOAD_TIMEOUT)

    service_name = context["appointment_payments"]["service"]["name"]
    # Only one stale line is ever re-added, so a single detect-drop-retry settles it;
    # the bounded loop (<=2 retries) absorbs async timing variance in that re-add.
    for _ in range(2):
        if _open_pos_record_dialog(page, dialog_timeout=FAST_UI_TIMEOUT):
            _complete_pos_record(page)
            return
        _drop_pos_line(page, service_name)
    if not _open_pos_record_dialog(page, dialog_timeout=LOAD_TIMEOUT):
        raise AssertionError("POS take-payment dialog did not open after dropping the stale appointment line")
    _complete_pos_record(page)


def assert_cp_estimate_from_email(page: Page, email_url: str, *, title: str, number: str,
                                  price: str, client: str, items: list,
                                  status_actions: list) -> None:
    """Open the CP estimate link from the email and assert the estimate entity page.

    Mirrors the legacy 'client navigates to CP from email' + 'CP estimate page
    displays': the link carries the client JWT, so it opens the estimate detail
    directly (asserted on the entity page, not the list)."""
    cp_context = page.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/New_York"
    )
    try:
        cp_page = cp_context.new_page()
        cp_page.goto(email_url, wait_until="domcontentloaded", timeout=CP_NAV_TIMEOUT)
        cp_frame = cp_page.frame_locator(CP_IFRAME)
        cp_frame.locator(CP_ESTIMATE_PAGE).first.wait_for(state="visible", timeout=CP_NAV_TIMEOUT)

        body = cp_frame.locator("body").first
        deadline = time.time() + CP_NAV_TIMEOUT / 1000
        text = ""
        while time.time() < deadline:
            text = body.inner_text(timeout=CP_NAV_TIMEOUT)
            if title in text and client in text:
                break
            cp_page.wait_for_timeout(500)
        _contains(text, title, "CP estimate title")
        _contains(text, number, "CP estimate number")
        _contains(text, f"${price}", "CP estimate price")
        _contains(text, client, "CP estimate client")
        for item in items:
            _contains(text, item["name"], f"CP item {item['name']}")
            if item.get("description"):
                _contains(text, item["description"], f"CP item desc {item['name']}")
            _contains(text, f"${item['price']}", f"CP item price {item['name']}")
        if status_actions and not any(re.search(a, text, re.I) for a in status_actions):
            raise AssertionError(f"CP estimate pending actions not found: {status_actions}")
    finally:
        cp_context.close()


def _contains(haystack: str, needle: str, label: str) -> None:
    if needle and needle not in haystack:
        raise AssertionError(f"{label}: expected to find '{needle}' on the CP estimate page")
