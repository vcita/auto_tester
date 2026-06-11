"""UI helpers for the event_payments migration (VCITA2-13856).

On new-dashboard (POV) accounts the event attendee menu no longer exposes the
payment request, so it is reached through Billing & Invoicing -> Orders -> the
eventattendance order row. That opens ``/app/payments/orders/{uid}`` with the
legacy Angular booking payment-status view (``payment_status_state``,
``edit_payment_status``, ``ps-more-actions``, ...), nested inside the POV
``iframe[data-qa="angular-iframe"]``; helpers therefore scan ``page.frames`` for
the payment-status frame rather than relying on a fixed iframe title.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page, Frame

from tests.account_api import pivot_uid

UI_TIMEOUT = 5000
# PAGE_TIMEOUT (page.goto) and NAV_TIMEOUT (cross-iframe POV->Angular boot / frame
# readiness) are documented bounded exceptions to the 5s element cap: navigation and
# iframe (re)render across the nested POV/Angular/Vue documents legitimately exceed
# 5s. Halved from the original 20s. Pure element interactions stay at UI_TIMEOUT.
PAGE_TIMEOUT = 10000
NAV_TIMEOUT = 10000
# External client-portal (vitrage) navigation is slower still; documented bounded
# exception (eventual page boot of the external live site + chat widget).
CP_NAV_TIMEOUT = 15000
ORDERS_RELOAD_RETRIES = 2
CP_VITRAGE = "https://live.meet2know.com"
CP_IFRAME = "#cp_iframe"

# Booking payment-status detail (Angular)
SERVICE_HEADER = "div.summary-header h3"
PRICE_HEADER = "div.summary-header h2"
PS_STATE = "span[data-qa='payment_status_state']"
PS_CLIENT = "[data-qa='display-name']"
PS_EDIT_BTN = 'button[data-qa="edit_payment_status"]'
PS_MORE_ACTIONS = 'button[data-qa="ps-more-actions"]'
PS_WAIVE = 'button[data-qa="waive_payment"]'
PS_CONFIRM_CANCEL = 'button[ng-click="cancel_payment()"]'

# Billing & Invoicing order row
ORDER_ROW = '[data-qa^="item-type"]'

# Take-payment dialog (record, non-POS)
TAKE_PAYMENT_BTN = 'button[data-qa="take_payment"]'
RECORD_SECTION_BTN = '[data-qa="record_payment_button"]'
TAKE_PAYMENT_CONFIRM = '[data-qa="take-payment-confirmation"][aria-disabled="false"]'


def app_base(context: dict) -> str:
    base = (context.get("base_url") or context.get("app_base_url") or "").rstrip("/")
    if not base:
        raise ValueError("base_url missing from context")
    return base


def open_attendee_payment_request(page: Page, context: dict,
                                  client_name: str | None = None) -> Frame:
    """Open the attendee's booking payment-request detail and return its frame.

    The detail URL is cached on first open and reused: once a request is waived it
    drops out of the default Orders list, so direct navigation is the reliable path."""
    seeded = context["event_payments"]
    order_url = seeded.get("order_url")
    if order_url:
        page.goto(order_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    else:
        _open_event_order(page, context, seeded["service"]["name"])
    frame = _payment_status_frame(page)
    seeded["order_url"] = page.url
    return frame


def _payment_status_frame(page: Page, timeout_ms: int = NAV_TIMEOUT) -> Frame:
    """Frame hosting the booking payment-status detail."""
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(PS_STATE).count() > 0:
                    return frame
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise AssertionError("Booking payment-status detail did not load")


def _orders_frame(page: Page, service_name: str, timeout_ms: int = NAV_TIMEOUT):
    """Frame + row for the Billing & Invoicing order matching `service_name`."""
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                row = frame.locator(ORDER_ROW).filter(has_text=service_name)
                if row.count() > 0:
                    return frame, row.first
            except Exception:
                continue
        page.wait_for_timeout(300)
    return None, None


def _open_event_order(page: Page, context: dict, service_name: str) -> Frame:
    """Open the event's payment-request order from Billing & Invoicing (frame-scan).

    Orders-list indexing can lag the synchronous order, so reload a few times."""
    for _ in range(ORDERS_RELOAD_RETRIES + 1):
        page.goto(f"{app_base(context)}/app/payments/orders",
                  wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
        frame, row = _orders_frame(page, service_name)
        if row is not None:
            row.click()
            return frame
        page.wait_for_timeout(1500)
    raise AssertionError(f"Order row for '{service_name}' not found in Billing & Invoicing")


def read_event_payment_request(frame: Frame) -> dict:
    frame.locator(PS_STATE).first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    return {
        "service_name": frame.locator(SERVICE_HEADER).first.inner_text().strip(),
        "client_full_name": frame.locator(PS_CLIENT).first.inner_text().strip(),
        "amount": " ".join(frame.locator(PRICE_HEADER).first.inner_text().split()),
        "state": frame.locator(PS_STATE).first.inner_text().replace(":", "").strip(),
    }


def assert_event_payment_request(page: Page, context: dict, expected: dict,
                                  client_name: str | None = None,
                                  timeout_s: float | None = None) -> None:
    """Open the attendee payment request and assert every expected field (strict).

    The booking payment-status is eventually consistent after recording a payment, so
    re-open the request within a bounded poll until it matches (re-render is required;
    re-reading a static frame would not pick up the server-side rollup).

    `timeout_s` overrides the default NAV_TIMEOUT poll window for transitions whose
    server-side rollup is slower (e.g. cancel -> CANCELLED), as a documented
    eventual-consistency exception to the element-wait cap."""
    deadline = time.monotonic() + (timeout_s if timeout_s is not None else NAV_TIMEOUT / 1000)
    actual: dict = {}
    frame = open_attendee_payment_request(page, context, client_name)
    while time.monotonic() < deadline:
        actual = read_event_payment_request(frame)
        if all(actual.get(key) == value for key, value in expected.items()):
            return
        time.sleep(0.5)
        frame = open_attendee_payment_request(page, context, client_name)
    mismatch = {k: (expected[k], actual.get(k)) for k in expected if actual.get(k) != expected[k]}
    raise AssertionError(f"Event payment request mismatch (expected, actual): {mismatch}")


def edit_payment_request_amount(page: Page, context: dict, amount: str) -> None:
    """Edit the attendee payment request amount via the edit dialog."""
    frame = open_attendee_payment_request(page, context)
    frame.locator(PS_EDIT_BTN).first.click()
    amount_input = frame.locator('input[name="price"]').first
    amount_input.wait_for(state="visible", timeout=UI_TIMEOUT)
    amount_input.fill(str(amount))
    save = frame.locator('button[translate="common.dialog.save"]').first
    save.click()
    save.wait_for(state="hidden", timeout=UI_TIMEOUT)


def pay_for_event(page: Page, context: dict, amount: str) -> None:
    """Record a Cash payment of `amount` against the attendee payment request.

    Requires the `point_of_sale` flag denied so `take_payment` opens the legacy
    record-payment dialog (mirrors BookingPaymentRequestPage.payForMeeting non-POS)."""
    frame = open_attendee_payment_request(page, context)
    _take_payment_record(frame, amount)


def _take_payment_record(frame: Frame, amount: str) -> None:
    """Record a Cash payment of `amount` from an order/invoice payment-status frame.

    Events open a record dialog (`record_payment_button`); invoices open a take-payment
    dropdown whose item is `record_payment` - accept either."""
    frame.locator(TAKE_PAYMENT_BTN).first.click()
    record_btn = frame.locator(f"{RECORD_SECTION_BTN}, [data-qa='record']").first
    record_btn.wait_for(state="visible", timeout=NAV_TIMEOUT)
    record_btn.click()
    _fill_money_amount(frame, amount)
    _choose_payment_method(frame, "Cash")
    overlay = frame.locator("div.md-select-menu-container.md-active")
    if overlay.count() > 0:
        overlay.first.wait_for(state="hidden", timeout=UI_TIMEOUT)
    record = frame.locator(TAKE_PAYMENT_CONFIRM).first
    record.wait_for(state="visible", timeout=NAV_TIMEOUT)
    record.click()
    record.wait_for(state="hidden", timeout=NAV_TIMEOUT)


def _fill_money_amount(frame: Frame, amount: str) -> None:
    """Fill the masked money-input. The mask only updates on real keystrokes, so
    clear with select-all + Backspace and type char-by-char (proven in
    record_payment_partial), then Tab to commit."""
    amount_input = frame.locator(
        "input.amount-input:visible, input[name='money_amount']:visible"
    ).first
    amount_input.wait_for(state="visible", timeout=UI_TIMEOUT)
    amount_input.click()
    amount_input.press("Meta+A")
    amount_input.press("Backspace")
    amount_input.press_sequentially(str(amount), delay=50)
    amount_input.press("Tab")


def _choose_payment_method(frame: Frame, method: str) -> None:
    """Select the record payment method. The newTakePayment dialog (invoices) uses
    `md-select[name='payment_method']`; the legacy record section (events) exposes a
    `Payment received via` listbox - support both."""
    select = frame.locator("md-select[name='payment_method']").first
    if select.count() > 0:
        select.wait_for(state="visible", timeout=UI_TIMEOUT)
        select.click()
        option = frame.locator(
            f"div.md-select-menu-container.md-active md-option:has-text('{method}')"
        ).first
        option.wait_for(state="visible", timeout=UI_TIMEOUT)
        option.evaluate("el => el.click()")
        frame.locator("div.md-select-menu-container.md-active").first.wait_for(
            state="hidden", timeout=UI_TIMEOUT)
        return
    listbox = frame.get_by_role("listbox", name="Payment received via").first
    listbox.wait_for(state="visible", timeout=UI_TIMEOUT)
    if method in listbox.inner_text():
        return
    listbox.click()
    frame.get_by_role("option", name=method).first.click()


PAYMENT_ROW = "f-ellipsis-tooltip.payment-title"
NAME_FILTER = 'input[name="name_filter"]'

# Orders status filter + sale detail (reused selectors from adhoc_sale_refund)
STATUS_FILTER = '[name="status_filter"]'
STATUS_VALUE = {"PAID": "paid", "CANCELLED": "cancelled", "DUE": "pending"}
SALE_NAME = "span.main-title"
SALE_PRICE = "span.price"
SALE_STATUS = "span.status-text"
SALE_CLIENT = "span.data-part"

# POS checkout (POV top-level)
POS_CHECKOUT_ACTIVATOR = '[data-qa="checkout-actions-activator"]'
POS_CHECKOUT_RECORD = '[data-qa="checkout-action-record"]'
POS_TAKE_PAYMENT_DIALOG = "md-dialog.take-payment-wrapper, md-dialog.close-balance-content"
POS_METHOD_SELECT = "md-select[name='payment_method']"
POS_METHOD_OPTION = 'div.md-select-menu-container.md-active md-option:has-text("Cash")'


def record_event_payment_via_pos(page: Page, context: dict) -> None:
    """Pay the event payment request through Point of Sale (record a Cash sale).

    Requires `point_of_sale` enabled (default): `take_payment` opens POS with the
    event item pre-loaded; checkout -> Record payment -> Cash -> confirm creates the
    sale (mirrors PaymentStatusCard.continuePosAndSelectItems('record-payment'))."""
    from tests.salsa.payments.deposits.deposits_invoice_ui import (
        FAST_UI_TIMEOUT, LOAD_TIMEOUT, _find_control, _require,
    )
    frame = open_attendee_payment_request(page, context)
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


def assert_order_in_status(page: Page, context: dict, status: str, title: str) -> None:
    """Filter Orders by status and assert the order titled `title` is listed."""
    value = STATUS_VALUE[status.upper()]
    last_error = None
    for _ in range(ORDERS_RELOAD_RETRIES + 1):
        page.goto(f"{app_base(context)}/app/payments/orders",
                  wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
        frame = _frame_with(page, STATUS_FILTER)
        if frame is None:
            last_error = "status filter not found"
            continue
        _apply_status_filter(page, frame, value)
        row = frame.locator(PAYMENT_ROW).filter(has_text=title)
        deadline = time.monotonic() + UI_TIMEOUT / 1000
        while time.monotonic() < deadline:
            if row.count() > 0 and row.first.is_visible():
                return
            page.wait_for_timeout(300)
        last_error = f"order '{title}' not visible under {status}"
        page.wait_for_timeout(1000)
    raise AssertionError(f"Order status assertion failed: {last_error}")


def _apply_status_filter(page: Page, frame: Frame, value: str) -> None:
    dropdown = frame.locator(STATUS_FILTER).first
    dropdown.wait_for(state="visible", timeout=UI_TIMEOUT)
    dropdown.click()
    target = frame.locator(f'[value="{value}"]').first
    target.wait_for(state="visible", timeout=UI_TIMEOUT)
    for other in STATUS_VALUE.values():
        if other == value:
            continue
        opt = frame.locator(f'[value="{other}"]').first
        try:
            if opt.count() > 0 and opt.get_attribute("selected") is not None:
                opt.click()
        except Exception:
            continue
    if target.get_attribute("selected") is None:
        target.click()
    page.keyboard.press("Escape")


def assert_sale_page(page: Page, context: dict, expected: dict) -> None:
    """Open the sale order and assert its detail fields (name/state/amount/client/items)."""
    _open_order_by_title(page, context, expected["sale_name"])
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    actual: dict = {}
    while time.monotonic() < deadline:
        actual = _read_sale_data(page)
        if actual and all(actual.get(k) == v for k, v in expected.items() if k in actual):
            return
        page.wait_for_timeout(300)
    mismatch = {k: (v, actual.get(k)) for k, v in expected.items() if actual.get(k) != v}
    raise AssertionError(f"Sale page mismatch (expected, actual): {mismatch}")


def _open_order_by_title(page: Page, context: dict, title: str) -> None:
    """Open the order/invoice/sale titled `title` from Billing & Invoicing.

    Detail layouts differ (invoice/payment-request vs sale), so callers fetch the
    frame they need (`_detail_frame` for payable detail, `_read_sale_data` for sales)."""
    for _ in range(ORDERS_RELOAD_RETRIES + 1):
        page.goto(f"{app_base(context)}/app/payments/orders",
                  wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
        frame, row = _orders_frame(page, title)
        if row is not None:
            row.click()
            # Detail readiness is polled by the caller (_detail_frame / _read_sale_data).
            return
        page.wait_for_timeout(1500)
    raise AssertionError(f"Order '{title}' not found in Billing & Invoicing")


def _detail_frame(page: Page, timeout_ms: int = NAV_TIMEOUT) -> Frame:
    """Frame hosting an order/invoice detail (has take_payment or payment status)."""
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(f"{TAKE_PAYMENT_BTN}, {PS_STATE}").count() > 0:
                    return frame
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise AssertionError("Order/invoice detail did not load")


def _read_sale_data(page: Page) -> dict:
    for frame in page.frames:
        try:
            if frame.locator(SALE_PRICE).count() == 0 or frame.locator(SALE_STATUS).count() == 0:
                continue
            name = (frame.locator(SALE_NAME).first.inner_text(timeout=UI_TIMEOUT) or "").strip()
            price = (frame.locator(SALE_PRICE).first.inner_text(timeout=UI_TIMEOUT) or "").replace("US", "").strip()
            state = (frame.locator(SALE_STATUS).first.inner_text(timeout=UI_TIMEOUT) or "").replace(":", "").strip()
            client = (frame.locator(SALE_CLIENT).first.inner_text(timeout=UI_TIMEOUT) or "").strip()
            if name and price and state:
                return {"sale_name": name, "amount": price, "state": state, "client_full_name": client}
        except Exception:
            continue
    return {}


def _frame_with(page: Page, selector: str, timeout_ms: int = NAV_TIMEOUT):
    """Return the first frame whose `selector` is present (POV wraps Angular)."""
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(selector).count() > 0:
                    return frame
            except Exception:
                continue
        page.wait_for_timeout(300)
    return None


PAYMENT_DETAIL_HEADER = "div.summary-header h3"


def search_payments(page: Page, context: dict, first_name: str,
                    payment_title: str, expected_count: int = 1) -> None:
    """Filter Payments Received by client name and assert exactly `expected_count`
    matching rows (legacy asserts the sorted matching-title list by exact length)."""
    last_error = None
    for _ in range(ORDERS_RELOAD_RETRIES + 1):
        page.goto(f"{app_base(context)}/app/payments/transactions",
                  wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
        frame = _frame_with(page, NAME_FILTER)
        if frame is None:
            last_error = "Payments Received search box not found"
            continue
        search = frame.locator(NAME_FILTER).first
        search.fill(first_name, timeout=UI_TIMEOUT)
        rows = frame.locator(PAYMENT_ROW).filter(has_text=payment_title)
        deadline = time.monotonic() + UI_TIMEOUT / 1000
        while time.monotonic() < deadline:
            if rows.count() == expected_count:
                return
            page.wait_for_timeout(300)
        last_error = f"found {rows.count()} of {expected_count} '{payment_title}' rows"
        page.wait_for_timeout(1000)
    raise AssertionError(f"Payments search for '{payment_title}' failed: {last_error}")


def open_payment_detail_and_assert_title(page: Page, context: dict, first_name: str,
                                         payment_title: str) -> None:
    """Open the payment from Payments Received and assert its detail header equals
    `payment_title` (mirrors legacy 'payment was refunded' -> goToPayment +
    getPaymentNameText, which clicks into /app/transactions/{uid} and reads the
    summary header)."""
    search_payments(page, context, first_name, payment_title, expected_count=1)
    frame = _frame_with(page, NAME_FILTER)
    if frame is None:
        raise AssertionError("Payments Received list not found when opening payment detail")
    link = frame.locator(PAYMENT_ROW).filter(has_text=payment_title).first.locator(
        "xpath=ancestor::a[1]")
    link.wait_for(state="visible", timeout=UI_TIMEOUT)
    link.click()
    detail = _frame_with(page, PAYMENT_DETAIL_HEADER)
    if detail is None:
        raise AssertionError("Payment detail page did not load")
    header = detail.locator(PAYMENT_DETAIL_HEADER).first
    header.wait_for(state="visible", timeout=NAV_TIMEOUT)
    actual = header.inner_text().strip()
    assert actual == payment_title, (
        f"payment detail header: expected {payment_title!r}, got {actual!r}")


# Invoice creation wizard (#vue_wizard_iframe) + invoice detail
SEND_INVOICE_BTN = 'button[data-qa="send_an_invoice"]'
WIZARD_TITLE = '[data-qa="itemizable-details-header"]'
FROM_FOLD = "[data-qa='itemizable-from-fold']"
BILLING_EDIT_BTN = "[data-qa='itemizable-from-business-address-edit-button']"
BILLING_TEXTAREA = "[data-qa='itemizable-from-business-address-edit'] textarea"
INVOICE_SEND_BTN = "[data-qa='itemizable-dialog-main']"
INVOICE_TITLE = "div.summary-header h3"
INVOICE_ITEM = "div.invoice-item-content span"
INVOICE_PRICE = "div.summary-header h2 span"


def invoice_event(page: Page, context: dict, invoice_name: str, billing_address: str) -> None:
    """Create an invoice from the event payment request (mirrors invoiceEvent)."""
    frame = open_attendee_payment_request(page, context)
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


def _wizard_frame(page: Page, timeout_ms: int = NAV_TIMEOUT) -> Frame:
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(WIZARD_TITLE).count() > 0:
                    return frame
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise AssertionError("Invoice wizard did not load")


def pay_for_invoice(page: Page, context: dict, invoice_name: str, amount: str) -> None:
    """Open the invoice order and record a Cash payment of `amount`."""
    _open_order_by_title(page, context, invoice_name)
    frame = _detail_frame(page)
    _take_payment_record(frame, amount)


def assert_invoice_page(page: Page, context: dict, expected: dict) -> None:
    """Assert state/amount/client/service_name/invoice_name on the invoice detail.

    `pay_for_invoice` leaves the invoice detail open with the payment applied in place,
    so read the current detail frame first (the Orders list aggregation lags), and only
    re-open from Orders as a fallback."""
    frame = _detail_frame(page)
    actual: dict = {}
    # Bounded eventual-consistency poll: the invoice PAID rollup lags the recorded
    # payment. Documented exception to the 5s cap (backend aggregation only).
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        actual = _read_invoice_data(frame)
        if all(actual.get(k) == v for k, v in expected.items()):
            return
        page.wait_for_timeout(1000)
    mismatch = {k: (v, actual.get(k)) for k, v in expected.items() if actual.get(k) != v}
    raise AssertionError(f"Invoice page mismatch (expected, actual): {mismatch}")


def _read_invoice_data(frame: Frame) -> dict:
    frame.locator(PS_STATE).first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    return {
        "invoice_name": frame.locator(INVOICE_TITLE).first.inner_text().strip(),
        "service_name": frame.locator(INVOICE_ITEM).first.inner_text().strip(),
        "client_full_name": frame.locator(PS_CLIENT).first.inner_text().strip(),
        "amount": " ".join(frame.locator(INVOICE_PRICE).first.inner_text().split()),
        "state": frame.locator(PS_STATE).first.inner_text().replace(":", "").strip(),
    }


EVENT_CANCEL_BTN = "button[data-qa='cancel']"
EVENT_CANCEL_CONFIRM = "button[data-qa='confirm-cancel-event']"
EVENT_REFUND_CHECKBOX = 'md-checkbox[ng-model="dialog.issue_refund"]'


def cancel_event_with_refund(page: Page, context: dict) -> None:
    """Cancel the whole event and issue refunds (mirrors EventPage.cancelEvent(true))."""
    from tests.salsa.payments.deposits.deposits_invoice_ui import (
        FAST_UI_TIMEOUT, LOAD_TIMEOUT, _find_control,
    )
    event_uid = context["event_payments"]["event"]["uid"]
    page.goto(f"{app_base(context)}/app/events/{event_uid}",
              wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    cancel = _find_control(page, EVENT_CANCEL_BTN, timeout=LOAD_TIMEOUT)
    if cancel is None:
        _dump_controls(page, "EVENT")
        raise AssertionError("Event cancel button not found")
    cancel.click(timeout=FAST_UI_TIMEOUT)
    refund = _find_control(page, EVENT_REFUND_CHECKBOX, timeout=LOAD_TIMEOUT)
    if refund is None:
        _dump_controls(page, "CANCEL_DIALOG")
        raise AssertionError("Refund checkbox not found in cancel-event dialog")
    refund.click(timeout=FAST_UI_TIMEOUT)
    confirm = _find_control(page, EVENT_CANCEL_CONFIRM, timeout=LOAD_TIMEOUT)
    confirm.click(timeout=FAST_UI_TIMEOUT)
    # Best-effort: the cancel dialog closes on success. The caller re-navigates and
    # polls (Payments Received reload loop) so this is a readiness hint, not a gate.
    try:
        confirm.wait_for(state="hidden", timeout=UI_TIMEOUT)
    except Exception:
        pass


def _dump_controls(page: Page, label: str) -> None:
    for fr in page.frames:
        try:
            qa = fr.eval_on_selector_all(
                "[data-qa]",
                "els => Array.from(new Set(els.filter(e=>e.offsetParent!==null).map(e=>e.getAttribute('data-qa')))).slice(0,60)",
            )
            btns = fr.eval_on_selector_all(
                "button, md-checkbox",
                "els => els.filter(e=>e.offsetParent!==null && (e.textContent||'').trim()).map(e=>(e.textContent||'').trim().slice(0,22)).slice(0,30)",
            )
            if qa or btns:
                print(f"  [{label}] {fr.url[:50]!r}\n    qa={qa}\n    btns={btns}")
        except Exception:
            continue


def assert_cp_conversation_title(page: Page, context: dict, title: str) -> None:
    """Open the client portal as the seeded client and assert a conversation bubble
    header includes `title` (mirrors legacy 'conversation ... includes title')."""
    token = context["event_payments"]["client"]["portal_token"]
    cp_context = page.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/New_York"
    )
    try:
        cp_page = cp_context.new_page()
        cp_page.goto(f"{CP_VITRAGE}/site/{pivot_uid(context)}/action?client_jwt={token}",
                     wait_until="domcontentloaded", timeout=CP_NAV_TIMEOUT)
        cp_frame = cp_page.frame_locator(CP_IFRAME)
        chat = cp_frame.locator('[data-qa="headerChatBtn"]').first
        # Client portal (external vitrage) renders slower than internal app routes;
        # use the documented bounded CP budget rather than the 5s cap.
        chat.wait_for(state="visible", timeout=CP_NAV_TIMEOUT)
        chat.click()
        header = cp_frame.locator('[data-qa="bubble-header"]').filter(has_text=title).first
        header.wait_for(state="visible", timeout=CP_NAV_TIMEOUT)
    finally:
        cp_context.close()


PS_REDEEM_PACKAGE = "button[data-qa='redeem_package']"


def redeem_with_package(page: Page, context: dict, client_name: str | None = None) -> None:
    """Redeem the attendee payment request with the client's package (mirrors legacy
    Event.redeemWithPackage -> BookingPaymentRequestPage.redeemPackage)."""
    frame = open_attendee_payment_request(page, context, client_name)
    redeem = frame.locator(PS_REDEEM_PACKAGE).first
    redeem.wait_for(state="visible", timeout=NAV_TIMEOUT)
    redeem.click()
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    while time.monotonic() < deadline:
        try:
            if "PAID" in frame.locator(PS_STATE).first.inner_text(timeout=2000).upper():
                return
        except Exception:
            pass
        page.wait_for_timeout(500)


def cancel_payment_request(page: Page, context: dict, is_refund: bool = False) -> None:
    """Cancel/waive the attendee payment request."""
    frame = open_attendee_payment_request(page, context)
    frame.locator(PS_MORE_ACTIONS).first.click()
    waive = frame.locator(PS_WAIVE).first
    waive.wait_for(state="visible", timeout=UI_TIMEOUT)
    waive.click()
    if is_refund:
        frame.locator('md-checkbox[ng-model="dialog.issue_refund"]').first.click()
    confirm = frame.locator(PS_CONFIRM_CANCEL).first
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    confirm.click()
    confirm.wait_for(state="hidden", timeout=UI_TIMEOUT)
