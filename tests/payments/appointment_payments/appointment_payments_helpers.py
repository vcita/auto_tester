"""UI helpers for the appointment_payments migration (VCITA2-13857).

Appointments expose their payment request on the appointment detail page
(``/app/appointments/{id}``), unlike events which are reached through Orders.
Navigating by booking id also disambiguates same-service appointments (scenario
6 schedules two "service" appointments). The take-payment / invoice / POS /
Orders / Payments-Received flows are identical to events, so the entity-agnostic
helpers are imported from :mod:`event_payments_helpers` rather than duplicated.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page, Frame

from tests.payments.event_payments.event_payments_helpers import (  # generic, entity-agnostic
    app_base,
    _take_payment_record,
    _wizard_frame,
    assert_invoice_page,  # noqa: F401  re-exported for scenario use
    assert_order_in_status,  # noqa: F401
    assert_sale_page,  # noqa: F401
    pay_for_invoice,  # noqa: F401
    search_payments,  # noqa: F401
    UI_TIMEOUT,
    PAGE_TIMEOUT,
    NAV_TIMEOUT,
    SEND_INVOICE_BTN,
    WIZARD_TITLE,
    FROM_FOLD,
    BILLING_EDIT_BTN,
    BILLING_TEXTAREA,
    INVOICE_SEND_BTN,
    TAKE_PAYMENT_BTN,
)

# Appointment payment-status card (Angular) - tolerant selectors (the appointment
# page and the Orders booking view differ slightly in markup).
STATE_SELECTORS = ["span[data-qa='payment_status_state']", "div.status-payment"]
AMOUNT_SELECTORS = ["div.balance-due-amount"]
SERVICE_SELECTORS = ["div.summary-header h3"]
CLIENT_SELECTORS = ["[data-qa='display-name']", "div.client-name"]

PS_EDIT_BTN = 'button[data-qa="edit_payment_status"]'
PS_MORE_ACTIONS = 'button[data-qa="ps-more-actions"]'
PS_WAIVE = 'button[data-qa="waive_payment"]'
PS_CONFIRM_CANCEL = 'button[ng-click="cancel_payment()"]'
PS_COMPLETE = "[data-qa='complete']"
PS_REDEEM_PACKAGE = "button[data-qa='redeem_package']"
PS_CANCEL_REDEMPTION = "[data-qa='cancel_package_redemption']"
PS_APPROVE_REFUND_REDEMPTION = "[data-qa='approve_refund_redemption']"
PS_DETAILS = "[data-qa='payment_status_details']"
REDEEMED_CAPTION = "Redeemed with package"

# Appointment-level cancel (whole appointment, optional refund)
APPT_CANCEL_BTN = "[data-qa='cancel']"
APPT_REFUND_CHECKBOX = 'md-checkbox[ng-model="dialog.issue_refund"]'
APPT_CANCEL_CONFIRM = 'button[ng-click="cancelAppointment()"]'

# Confirmation dialog (mark completed)
CONFIRM_ACTION_BTN = "button[data-qa='confirm-action'], button[ng-click='confirmAction()']"


def _store(context: dict) -> dict:
    return context["appointment_payments"]


def _appt_id(context: dict, identifier: str | None = None) -> str:
    store = _store(context)
    if identifier in (None, "this"):
        return store["last_booking"]["id"]
    booking = store["bookings"].get(identifier)
    if not booking:
        raise AssertionError(f"No booking with identifier '{identifier}' in context")
    store["last_booking"] = booking
    return booking["id"]


def _payment_status_frame(page: Page, timeout_ms: int = NAV_TIMEOUT) -> Frame:
    """Frame hosting the appointment payment-status card (any state/take-payment marker)."""
    markers = STATE_SELECTORS + [TAKE_PAYMENT_BTN, PS_MORE_ACTIONS]
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            for marker in markers:
                try:
                    if frame.locator(marker).count() > 0:
                        return frame
                except Exception:
                    continue
        page.wait_for_timeout(300)
    raise AssertionError("Appointment payment-status card did not load")


def open_appointment(page: Page, context: dict, identifier: str | None = None) -> Frame:
    """Open an appointment detail page by booking id and return its payment-status frame."""
    appt_id = _appt_id(context, identifier)
    page.goto(f"{app_base(context)}/app/appointments/{appt_id}",
              wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    return _payment_status_frame(page)


def _first_text(frame: Frame, selectors: list[str]) -> str:
    for sel in selectors:
        try:
            loc = frame.locator(sel).first
            if loc.count() > 0:
                text = loc.inner_text(timeout=UI_TIMEOUT)
                if text and text.strip():
                    return text
        except Exception:
            continue
    return ""


def read_appt_payment_request(frame: Frame) -> dict:
    return {
        "service_name": _first_text(frame, SERVICE_SELECTORS).strip(),
        "client_full_name": _first_text(frame, CLIENT_SELECTORS).strip(),
        "amount": " ".join(_first_text(frame, AMOUNT_SELECTORS).split()),
        "state": _first_text(frame, STATE_SELECTORS).replace(":", "").strip(),
    }


# Keys that are verified through the payment-status detail rather than the header.
_SPECIAL_KEYS = {"redeemed_with_package", "package_credit_refunded",
                 "package_name", "meeting_identifier"}


def assert_appt_payment_request(page: Page, context: dict, expected: dict,
                                identifier: str | None = None) -> None:
    """Open the appointment and assert the payment request matches `expected`.

    `meeting_identifier` selects which appointment to read; `redeemed_with_package`
    / `package_credit_refunded` (+ `package_name`) are verified via the
    payment-status detail caption."""
    nav = identifier or expected.get("meeting_identifier")
    base = {k: v for k, v in expected.items() if k not in _SPECIAL_KEYS}
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    actual: dict = {}
    frame = open_appointment(page, context, nav)
    while time.monotonic() < deadline:
        actual = read_appt_payment_request(frame)
        if all(actual.get(k) == v for k, v in base.items()):
            break
        time.sleep(1.0)
        frame = open_appointment(page, context, nav)  # re-navigate (booking status is eventually consistent)
    else:
        mismatch = {k: (base[k], actual.get(k)) for k in base if actual.get(k) != base[k]}
        raise AssertionError(f"Appointment payment request mismatch (expected, actual): {mismatch}")
    _assert_package_details(frame, expected)


def _assert_package_details(frame: Frame, expected: dict) -> None:
    package_name = expected.get("package_name", "")
    if expected.get("redeemed_with_package") == "true":
        _wait_text(frame, f"{REDEEMED_CAPTION}", package_name,
                   "Redeemed-with-package caption")
    if expected.get("package_credit_refunded") == "true":
        _wait_text(frame, "credit refund", package_name,
                   "Package credit-refund detail")


def _wait_text(frame: Frame, needle: str, also: str, label: str) -> None:
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    body = ""
    while time.monotonic() < deadline:
        try:
            body = frame.locator("body").first.inner_text(timeout=2000)
        except Exception:
            body = ""
        if needle.lower() in body.lower() and (not also or also.lower() in body.lower()):
            return
        time.sleep(0.3)
    raise AssertionError(f"{label} not found (looking for '{needle}' + '{also}')")


def _click_ps_menu_item(page: Page, frame: Frame, item_selector: str) -> None:
    """Open a payment-status menu item. The appointment detail has two
    `ps-more-actions` triggers (appointment actions vs payment-card actions);
    try each until the requested item appears, then click it."""
    triggers = frame.locator(PS_MORE_ACTIONS)
    count = triggers.count()
    if count == 0:
        raise AssertionError("No ps-more-actions trigger on appointment page")
    for i in range(count):
        triggers.nth(i).click()
        item = frame.locator(item_selector).first
        try:
            item.wait_for(state="visible", timeout=2000)
            item.click()
            return
        except Exception:
            try:
                page.keyboard.press("Escape")
            except Exception:
                pass
    raise AssertionError(f"Menu item {item_selector!r} not found under any ps-more-actions")


def edit_appt_payment_amount(page: Page, context: dict, amount: str,
                             identifier: str | None = None) -> None:
    frame = open_appointment(page, context, identifier)
    _click_ps_menu_item(page, frame, PS_EDIT_BTN)
    amount_input = frame.locator('input[name="price"]').first
    amount_input.wait_for(state="visible", timeout=UI_TIMEOUT)
    amount_input.fill(str(amount))
    save = frame.locator('button[translate="common.dialog.save"]').first
    save.click()
    save.wait_for(state="hidden", timeout=UI_TIMEOUT)


def cancel_appt_payment_request(page: Page, context: dict,
                                identifier: str | None = None) -> None:
    """Waive (cancel) the appointment's payment request, no refund."""
    frame = open_appointment(page, context, identifier)
    _click_ps_menu_item(page, frame, PS_WAIVE)
    confirm = frame.locator(PS_CONFIRM_CANCEL).first
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    confirm.click()
    confirm.wait_for(state="hidden", timeout=UI_TIMEOUT)


def pay_for_appointment(page: Page, context: dict, amount: str,
                        identifier: str | None = None) -> None:
    """Record a Cash payment (point_of_sale denied -> legacy record dialog)."""
    frame = open_appointment(page, context, identifier)
    _take_payment_record(frame, amount)
    # The take-payment dialog hides optimistically before the record POST returns;
    # navigating away immediately aborts it, so let the save settle first.
    page.wait_for_timeout(3000)


def record_appt_payment_via_pos(page: Page, context: dict,
                                identifier: str | None = None) -> None:
    """Record the appointment payment through Point of Sale (POS enabled)."""
    from tests.payments.deposits.deposits_invoice_ui import (
        FAST_UI_TIMEOUT, LOAD_TIMEOUT, _find_control, _require,
    )
    from tests.payments.event_payments.event_payments_helpers import (
        POS_CHECKOUT_ACTIVATOR, POS_CHECKOUT_RECORD, POS_TAKE_PAYMENT_DIALOG,
        POS_METHOD_SELECT, POS_METHOD_OPTION, TAKE_PAYMENT_CONFIRM,
    )
    frame = open_appointment(page, context, identifier)
    frame.locator(TAKE_PAYMENT_BTN).first.click()
    _require(page, POS_CHECKOUT_ACTIVATOR, "POS checkout activator", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_CHECKOUT_RECORD, "POS record-payment action").click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_TAKE_PAYMENT_DIALOG, "Take payment dialog", timeout=LOAD_TIMEOUT)
    _require(page, POS_METHOD_SELECT, "Record method picker").click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_METHOD_OPTION, "Cash record option").click(timeout=FAST_UI_TIMEOUT)
    _require(page, TAKE_PAYMENT_CONFIRM, "Take payment confirm").click(timeout=FAST_UI_TIMEOUT)
    deadline = time.monotonic() + LOAD_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if _find_control(page, POS_TAKE_PAYMENT_DIALOG, timeout=300) is None:
            return
        time.sleep(0.2)
    raise AssertionError("Take payment dialog did not close after recording the sale")


# POS "price varies" item-edit panel (display-for-a-fee) selectors
POS_PRICE_INPUT = '[data-qa="price-value"]'
POS_TAX_PICKER = '[data-qa="tax-picker-tf"]'
POS_DISCOUNT_INPUT = '[data-qa="discount-value"]'
POS_DISCOUNT_FIXED = '[data-qa="discount-types-item-fixed"]'
POS_EDIT_SAVE = '[data-qa="vc-footer-Save"], [data-qa="vc-footer-Add"], [data-qa="vc-footer-Continue"]'


def pay_custom_fee_via_pos(page: Page, context: dict, *, amount: str,
                           tax_label: str, discount_value: str,
                           discount_type: str = "percentage",
                           identifier: str | None = None) -> None:
    """Pay a 'display for a fee' (price varies) appointment through POS.

    Mirrors PaymentStatusCard.payForPriceVaries -> Pos.applyPriceForActivity +
    performPaymentAction('record'): open the POS item-edit panel, set the price,
    pick the tax, apply the discount, save, then record the sale as Cash."""
    from tests.payments.deposits.deposits_invoice_ui import (
        FAST_UI_TIMEOUT, LOAD_TIMEOUT, _find_control, _require,
    )
    from tests.payments.event_payments.event_payments_helpers import (
        POS_CHECKOUT_ACTIVATOR, POS_CHECKOUT_RECORD, POS_TAKE_PAYMENT_DIALOG,
        POS_METHOD_SELECT, POS_METHOD_OPTION, TAKE_PAYMENT_CONFIRM,
    )
    frame = open_appointment(page, context, identifier)
    frame.locator(TAKE_PAYMENT_BTN).first.click()

    price = _require(page, POS_PRICE_INPUT, "POS price-varies amount input", timeout=LOAD_TIMEOUT)
    price.click(timeout=FAST_UI_TIMEOUT)
    price.fill("", timeout=FAST_UI_TIMEOUT)
    price.fill(str(amount), timeout=FAST_UI_TIMEOUT)

    tax = _require(page, POS_TAX_PICKER, "POS tax picker")
    tax.click(timeout=FAST_UI_TIMEOUT)
    option = _require(
        page,
        f'[role="option"]:has-text("{tax_label}"), .v-list-item:has-text("{tax_label}"), '
        f'li:has-text("{tax_label}"), label:has-text("{tax_label}")',
        f"Tax option '{tax_label}'",
    )
    option.click(timeout=FAST_UI_TIMEOUT)
    # Multi-select checkbox dropdown - close it so the selection commits before saving.
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)

    disc = _require(page, POS_DISCOUNT_INPUT, "POS discount input")
    disc.click(timeout=FAST_UI_TIMEOUT)
    disc.fill(str(discount_value), timeout=FAST_UI_TIMEOUT)
    if discount_type != "percentage":
        _require(page, POS_DISCOUNT_FIXED, "Fixed discount type").click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_EDIT_SAVE, "POS item-edit save").click(timeout=FAST_UI_TIMEOUT)

    _require(page, POS_CHECKOUT_ACTIVATOR, "POS checkout activator", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_CHECKOUT_RECORD, "POS record-payment action").click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_TAKE_PAYMENT_DIALOG, "Take payment dialog", timeout=LOAD_TIMEOUT)
    _require(page, POS_METHOD_SELECT, "Record method picker").click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_METHOD_OPTION, "Cash record option").click(timeout=FAST_UI_TIMEOUT)
    _require(page, TAKE_PAYMENT_CONFIRM, "Take payment confirm").click(timeout=FAST_UI_TIMEOUT)
    deadline = time.monotonic() + LOAD_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if _find_control(page, POS_TAKE_PAYMENT_DIALOG, timeout=300) is None:
            return
        time.sleep(0.2)
    raise AssertionError("Take payment dialog did not close after recording the custom-fee sale")


def cancel_appointment(page: Page, context: dict, identifier: str | None = None,
                       refund: bool = False) -> None:
    """Cancel the whole appointment from its detail page, optionally issuing a refund."""
    from tests.payments.deposits.deposits_invoice_ui import (
        FAST_UI_TIMEOUT, LOAD_TIMEOUT, _find_control,
    )
    appt_id = _appt_id(context, identifier)
    page.goto(f"{app_base(context)}/app/appointments/{appt_id}",
              wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    cancel = _find_control(page, APPT_CANCEL_BTN, timeout=LOAD_TIMEOUT)
    if cancel is None:
        cancel = _find_control(page, "role=button[name=/Cancel Appointment/i]", timeout=LOAD_TIMEOUT)
    if cancel is None:
        raise AssertionError("Appointment cancel button not found")
    cancel.click(timeout=FAST_UI_TIMEOUT)
    if refund:
        check = _find_control(page, APPT_REFUND_CHECKBOX, timeout=LOAD_TIMEOUT)
        if check is None:
            raise AssertionError("Refund checkbox not found in cancel-appointment dialog")
        check.click(timeout=FAST_UI_TIMEOUT)
    confirm = _find_control(page, APPT_CANCEL_CONFIRM, timeout=LOAD_TIMEOUT)
    if confirm is None:
        confirm = _find_control(page, "role=button[name=/Submit/i]", timeout=LOAD_TIMEOUT)
    confirm.click(timeout=FAST_UI_TIMEOUT)
    page.wait_for_timeout(2000)


def mark_appt_completed(page: Page, context: dict, identifier: str | None = None) -> None:
    """Mark the appointment as completed (More actions -> Complete -> confirm).

    Past/now appointments auto-complete, so the Complete menu item may be absent;
    treat that as already-completed and return."""
    frame = open_appointment(page, context, identifier)
    try:
        _click_ps_menu_item(page, frame, PS_COMPLETE)
    except AssertionError:
        return  # already completed (no Complete action available)
    confirm = frame.locator(CONFIRM_ACTION_BTN).first
    try:
        confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
        confirm.click()
    except Exception:
        pass
    page.wait_for_timeout(1500)


def _open_appt_via_orders(page: Page, context: dict, service_name: str) -> Frame:
    """Reach the appointment payment-status card through POV SPA routing.

    The appointment-page "Create invoice" button only mounts the POV invoice
    wizard (``/vue/#/itemizable``) when the appointment page is entered via
    in-app SPA navigation; a direct deep-link (``page.goto`` to
    ``/app/appointments/{id}``) loads the appointment app without the POV
    wizard host, so the button click is a silent no-op. Navigating from
    Billing & Invoicing and clicking the order row performs the SPA navigation
    that keeps the POV router/state alive. The order row is only present for a
    DUE request (require-to-pay), which is why the invoiced scenario seeds a
    require-to-pay service - the invoice->PAID behavior under test is identical.
    """
    from tests.payments.event_payments.event_payments_helpers import (
        _orders_frame, ORDERS_RELOAD_RETRIES,
    )
    for _ in range(ORDERS_RELOAD_RETRIES + 1):
        page.goto(f"{app_base(context)}/app/payments/orders",
                  wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
        _, row = _orders_frame(page, service_name)
        if row is not None:
            row.click()
            return _payment_status_frame(page)
        page.wait_for_timeout(1500)
    raise AssertionError(f"Order row for '{service_name}' not found in Billing & Invoicing")


def invoice_appointment(page: Page, context: dict, invoice_name: str,
                        billing_address: str, identifier: str | None = None) -> None:
    """Create an invoice from the appointment payment request (POV-routed)."""
    service_name = identifier or "service"
    frame = _open_appt_via_orders(page, context, service_name)
    frame.locator(SEND_INVOICE_BTN).first.click()
    wizard = _wizard_frame(page)
    title = wizard.locator(f"{WIZARD_TITLE} input").first
    if title.count() == 0:
        title = wizard.locator(WIZARD_TITLE).first
    title.wait_for(state="visible", timeout=NAV_TIMEOUT)
    title.fill(invoice_name)
    wizard.locator(FROM_FOLD).first.click()
    edit = wizard.locator(BILLING_EDIT_BTN).first
    edit.wait_for(state="visible", timeout=UI_TIMEOUT)
    edit.click()
    textarea = wizard.locator(BILLING_TEXTAREA).first
    textarea.wait_for(state="visible", timeout=UI_TIMEOUT)
    textarea.fill(billing_address)
    wizard.locator(FROM_FOLD).first.click()
    wizard.locator(INVOICE_SEND_BTN).first.click()
    page.wait_for_url("**/app/invoices/**", timeout=NAV_TIMEOUT, wait_until="domcontentloaded")


def cancel_package_redemption(page: Page, context: dict,
                              identifier: str | None = None) -> None:
    """Refund a package redemption from the appointment payment request."""
    frame = open_appointment(page, context, identifier)
    cancel = frame.locator(PS_CANCEL_REDEMPTION).first
    cancel.wait_for(state="visible", timeout=NAV_TIMEOUT)
    cancel.click()
    approve = frame.locator(PS_APPROVE_REFUND_REDEMPTION).first
    approve.wait_for(state="visible", timeout=UI_TIMEOUT)
    approve.click()
    page.wait_for_timeout(1500)


def redeem_appt_with_package(page: Page, context: dict,
                             identifier: str | None = None) -> None:
    """Redeem the appointment payment request with the client's package -> PAID."""
    frame = open_appointment(page, context, identifier)
    redeem = frame.locator(PS_REDEEM_PACKAGE).first
    redeem.wait_for(state="visible", timeout=NAV_TIMEOUT)
    redeem.click()
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if "PAID" in read_appt_payment_request(frame)["state"].upper():
            return
        page.wait_for_timeout(500)


def assert_payment_refunded(page: Page, context: dict, payment_title: str,
                            first_name: str) -> None:
    """Open a payment from Payments Received and assert its title (refund check)."""
    from tests.payments.event_payments.event_payments_helpers import (
        PAYMENT_ROW, NAME_FILTER, _frame_with, ORDERS_RELOAD_RETRIES,
    )
    last_error = None
    for _ in range(ORDERS_RELOAD_RETRIES + 1):
        page.goto(f"{app_base(context)}/app/payments/transactions",
                  wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
        frame = _frame_with(page, NAME_FILTER)
        if frame is None:
            last_error = "Payments Received search box not found"
            continue
        frame.locator(NAME_FILTER).first.fill(first_name, timeout=UI_TIMEOUT)
        row = frame.locator(PAYMENT_ROW).filter(has_text=payment_title)
        deadline = time.monotonic() + UI_TIMEOUT / 1000
        while time.monotonic() < deadline:
            if row.count() > 0 and row.first.is_visible():
                return
            page.wait_for_timeout(300)
        last_error = f"payment '{payment_title}' not found"
        page.wait_for_timeout(1000)
    raise AssertionError(f"Refunded payment assertion failed: {last_error}")
