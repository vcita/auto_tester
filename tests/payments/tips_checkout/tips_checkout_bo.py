"""Back-office tipping UI flows for the tips_checkout migration (VCITA2-13899).

Covers the BO surfaces of automation-js/features/salsa/tips.feature:
- close a client's payments balance with a tip (scenario 1, action 1),
- record a custom-item payment with a tip via Quick Actions (scenario 1, action 2),
- add a follow-up tip to an invoice (charge) / event payment (record) (scenarios 5/6),
- assert the back-office payment page including the tip row.

Reuses the Quick Actions record-payment primitives from ``deposits_invoice_ui`` and
the Payments Received search/detail readers from ``event_payments_helpers``. The tip
picker (Angular ``md-select[name='tip_option']`` + ``input[name='tip_amount']``) and the
payment-page tip row (``.tip-row .invoice-right-side``) have no data-qa in the product,
so the stable legacy selectors are reused and documented (suggest adding data-qa).
"""

from __future__ import annotations

import time

from playwright.sync_api import Page, Frame

from tests.account_api import pivot_uid
from tests.payments.deposits.deposits_invoice_ui import (
    AMOUNT_INPUT,
    CUSTOM_ITEM_NAME,
    CUSTOM_ITEM_OPTION,
    FAST_UI_TIMEOUT,
    LOAD_TIMEOUT,
    PAYMENT_CONFIRM,
    PAYMENT_TITLE_FIELD,
    RECORD_METHOD_OPTION,
    RECORD_METHOD_SELECT,
    RECORD_PAYMENT_ITEM,
    _find_control,
    _open_quick_action,
    _require,
    _select_client,
)
from tests.payments.event_payments.event_payments_helpers import (
    NAV_TIMEOUT,
    PAGE_TIMEOUT,
    UI_TIMEOUT,
    _frame_with,
    app_base,
)

# Tip picker (Angular md-select, shared by close-balance / record / add-tip dialogs)
TIP_SELECT = "md-select[name='tip_option']"
TIP_OPTION = 'div.md-select-menu-container.md-active md-option:has-text("{label}")'
TIP_AMOUNT_INPUT = "input[name='tip_amount']"

# Client-page close balance
CLIENT_TAKE_PAYMENT = '[data-qa="action-button-matter_page-take_payment"]'
CLOSE_BALANCE_DIALOG = "md-dialog.take-payment-wrapper, md-dialog.close-balance-content"
RECORD_SECTION_BTN = "[data-qa='record_payment_button'], [data-qa='record']"
SEND_RECEIPT_CHECKBOX = 'md-checkbox[aria-label="Send receipt to client"]'
TAKE_PAYMENT_CONFIRM = '[data-qa="take-payment-confirmation"]'
METHOD_SELECT = "md-select[name='payment_method']"
METHOD_OPTION = 'div.md-select-menu-container.md-active md-option:has-text("{label}")'

# Add-a-tip dialog (invoice/event follow-up tip)
ADD_TIP_BTN = '[data-qa="add_tip"], [data-qa="addTip"]'
PS_MORE_ACTIONS = "button[data-qa='ps-more-actions']"
ADD_TIP_DIALOG = "md-dialog.add-tip-content, md-dialog.take-payment-wrapper"
# Add-tip dialog charge opener: the legacy add-tip dialog uses the translate-attr button;
# accept the newTakePayment data-qa variants too.
CHARGE_SECTION_BTN = ('button[translate="payment.take_payment.charge"], '
                      "[data-qa='charge_payment_button'], [data-qa='charge']")
GATEWAY_IFRAME_CARD = "#card"
MOCK_CARD_NUMBER = "4242424242424242"

# Back-office payment page (Payments Received detail)
PAYMENT_NAME = "div.summary-header h3"
PAYMENT_AMOUNT = "div.summary-header h2 span"
PAYMENT_CLIENT = "span.contact-name, div .display-name-component span"
PAYMENT_TYPE = "div.entity-summary-row .icon-v + div span.caption.wrap"
PAYMENT_ITEM = "span.invoice-item-content-title"
PAYMENT_TIP = ".tip-row .invoice-right-side"
NAME_FILTER = 'input[name="name_filter"]'
PAYMENT_ROW = "f-ellipsis-tooltip.payment-title"


# --------------------------------------------------------------------------- #
# Shared tip + method pickers
# --------------------------------------------------------------------------- #
def _select_md_option(scope, select_selector: str, option_template: str, label: str) -> None:
    select = scope.locator(select_selector).first
    select.wait_for(state="visible", timeout=UI_TIMEOUT)
    select.click()
    option = scope.locator(option_template.format(label=label)).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.evaluate("el => el.click()")
    overlay = scope.locator("div.md-select-menu-container.md-active")
    if overlay.count() > 0:
        try:
            overlay.first.wait_for(state="hidden", timeout=UI_TIMEOUT)
        except Exception:
            pass


def _apply_tip(scope, tip_option: str, tip_amount: str | None = None) -> None:
    """Pick a tip option. ``Custom`` reveals an amount input filled with ``tip_amount``."""
    _select_md_option(scope, TIP_SELECT, TIP_OPTION, tip_option)
    if tip_option.lower() == "custom":
        if tip_amount is None:
            raise ValueError("Custom tip requires tip_amount")
        amount = scope.locator(TIP_AMOUNT_INPUT).first
        amount.wait_for(state="visible", timeout=UI_TIMEOUT)
        amount.fill(str(tip_amount))


def _confirm_and_close(scope, dialog_selector: str) -> None:
    """Click the take-payment confirmation once it is enabled, then wait for the
    dialog to disappear. The confirm button flips to ``aria-disabled="true"`` while
    submitting, so we key completion on the dialog container (not the button) and
    re-click once if the first click did not register (observed flakiness)."""
    confirm = scope.locator(TAKE_PAYMENT_CONFIRM).first
    confirm.wait_for(state="visible", timeout=NAV_TIMEOUT)
    enabled_deadline = time.monotonic() + UI_TIMEOUT / 1000
    while time.monotonic() < enabled_deadline:
        if confirm.get_attribute("aria-disabled") != "true":
            break
        time.sleep(0.2)
    dialog = scope.locator(dialog_selector).first
    for attempt in range(2):
        confirm.click()
        try:
            dialog.wait_for(state="hidden", timeout=NAV_TIMEOUT)
            return
        except Exception:
            if attempt == 0 and confirm.count() > 0 and confirm.is_visible():
                continue
            raise


def _scope_with(page: Page, selector: str, timeout_ms: int = NAV_TIMEOUT):
    """Return the page or frame whose `selector` is present (close-balance/add-tip
    dialogs render either top-level POV or inside the Angular billing iframe)."""
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for scope in [page, *page.frames]:
            try:
                if scope.locator(selector).count() > 0:
                    return scope
            except Exception:
                continue
        page.wait_for_timeout(300)
    return None


# --------------------------------------------------------------------------- #
# Scenario 1, action 1: close a client's balance with a tip
# --------------------------------------------------------------------------- #
def close_client_balance(page: Page, context: dict, *, client_id: str,
                         record_type: str, tip_option: str,
                         send_receipt: bool = False) -> None:
    """Open the client card, take payment (close balance: all unpaid items),
    record with ``record_type``, apply ``tip_option`` and (optionally) send receipt.

    Mirrors legacy Client.closeBalance -> TakePaymentDialog.takePayment(record)."""
    page.goto(f"{app_base(context)}/app/clients/{client_id}",
              wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    take = _find_control(page, CLIENT_TAKE_PAYMENT, timeout=LOAD_TIMEOUT)
    if take is None:
        raise AssertionError("Client-card take-payment action not found")
    take.click(timeout=FAST_UI_TIMEOUT)
    scope = _scope_with(page, CLOSE_BALANCE_DIALOG) or page
    record = scope.locator(RECORD_SECTION_BTN).first
    record.wait_for(state="visible", timeout=NAV_TIMEOUT)
    record.click()
    _select_md_option(scope, METHOD_SELECT, METHOD_OPTION, record_type)
    _apply_tip(scope, tip_option)
    if send_receipt:
        receipt = scope.locator(SEND_RECEIPT_CHECKBOX).first
        if receipt.count() > 0 and receipt.get_attribute("aria-checked") != "true":
            receipt.click()
    _confirm_and_close(scope, CLOSE_BALANCE_DIALOG)


# --------------------------------------------------------------------------- #
# Scenario 1, action 2: record a custom-item payment with a tip (Quick Actions)
# --------------------------------------------------------------------------- #
def record_custom_payment_with_tip(page: Page, context: dict, *, client_name: str,
                                   item_name: str, amount: str, tip_option: str,
                                   tip_amount: str | None = None) -> None:
    """Quick Actions -> Record payment, custom item + amount, tip, Cash, confirm.

    Extends deposits_invoice_ui.record_custom_payment with the tip picker."""
    _open_quick_action(page, RECORD_PAYMENT_ITEM, "Record payment")
    _select_client(page, client_name)

    title_field = _require(page, PAYMENT_TITLE_FIELD, "Record payment title field")
    title_field.click(timeout=FAST_UI_TIMEOUT)
    title_field.type("Custom Item", delay=20)
    _require(page, CUSTOM_ITEM_OPTION, "Custom Item option").click(timeout=FAST_UI_TIMEOUT)
    _require(page, CUSTOM_ITEM_NAME, "Custom item name field").fill(item_name, timeout=FAST_UI_TIMEOUT)
    _require(page, AMOUNT_INPUT, "Payment amount field").fill(amount, timeout=FAST_UI_TIMEOUT)

    method_select = _require(page, RECORD_METHOD_SELECT, "Record method picker")
    method_select.click(timeout=FAST_UI_TIMEOUT)
    _require(page, RECORD_METHOD_OPTION, "Cash record method option").click(timeout=FAST_UI_TIMEOUT)

    dialog_scope = _scope_with(page, TIP_SELECT) or page
    _apply_tip(dialog_scope, tip_option, tip_amount)

    confirm = _require(page, PAYMENT_CONFIRM, "Record payment confirm button")
    confirm.click(timeout=FAST_UI_TIMEOUT)
    deadline = time.monotonic() + FAST_UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if _find_control(page, CUSTOM_ITEM_NAME, timeout=300) is None:
            return
        time.sleep(0.2)
    raise AssertionError("Record payment dialog did not close after recording")


# --------------------------------------------------------------------------- #
# Scenarios 5/6: follow-up tip on invoice (charge) / event payment (record)
# --------------------------------------------------------------------------- #
def add_followup_tip(page: Page, context: dict, *, tip_option: str,
                     payment_type: str, tip_amount: str | None = None) -> None:
    """Click Add a tip on the currently-open payment/invoice/event payment page and
    take the tip via ``charge`` (mock card) or ``record`` (cash). Caller navigates to
    the payment page first (invoice detail or event attendee payment status)."""
    _open_add_tip(page)
    scope = _scope_with(page, ADD_TIP_DIALOG) or page
    if payment_type == "charge":
        charge = scope.locator(CHARGE_SECTION_BTN).first
        if charge.count() > 0:
            charge.click()
        _fill_mock_card(page)
    else:
        record = scope.locator(RECORD_SECTION_BTN).first
        if record.count() > 0:
            record.click()
        # The add-tip record dialog requires a payment method ("Payment received via");
        # RECORD stays disabled until one is chosen, so default to Cash.
        method = scope.locator(METHOD_SELECT).first
        if method.count() > 0:
            _select_md_option(scope, METHOD_SELECT, METHOD_OPTION, "Cash")
    _apply_tip(scope, tip_option, tip_amount)
    _confirm_and_close(scope, ADD_TIP_DIALOG)


def _open_add_tip(page: Page) -> None:
    """Click the Add a tip action, opening the ``ps-more-actions`` overflow first when
    the action is not directly visible (matches legacy invoice/event behaviour)."""
    add = _find_control(page, ADD_TIP_BTN, timeout=LOAD_TIMEOUT)
    if add is None:
        more = _find_control(page, PS_MORE_ACTIONS, timeout=FAST_UI_TIMEOUT)
        if more is not None:
            more.click(timeout=FAST_UI_TIMEOUT)
            add = _find_control(page, ADD_TIP_BTN, timeout=LOAD_TIMEOUT)
    if add is None:
        raise AssertionError("Add a tip action not found on the payment page")
    add.click(timeout=FAST_UI_TIMEOUT)


def _fill_mock_card(page: Page) -> None:
    """Fill the mock gateway card number inside the gateway iframe (charge tip)."""
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                card = frame.locator(GATEWAY_IFRAME_CARD)
                if card.count() > 0:
                    card.first.fill(MOCK_CARD_NUMBER, timeout=UI_TIMEOUT)
                    return
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise AssertionError("Mock gateway card field did not load for charge tip")


def open_invoice_payment_page(page: Page, context: dict, invoice_uid: str) -> None:
    page.goto(f"{app_base(context)}/app/invoices/{invoice_uid}",
              wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)


def open_paid_event_order(page: Page, context: dict, event_name: str) -> None:
    """Open the paid event attendance booking payment-status (order) detail - the page that
    exposes Add a tip for an event follow-up tip (the Payments Received transaction detail
    does NOT show Add a tip, only the booking payment-status / order detail does).

    The attendance is pre-paid via API, so its order is PAID and hidden under the Billing &
    Invoicing OVERDUE/DUE default filter; switch the Orders status filter to PAID, then open
    the matching order row (reuses the event_payments Orders navigation primitives)."""
    from tests.payments.event_payments import event_payments_helpers as ev
    for _ in range(ev.ORDERS_RELOAD_RETRIES + 1):
        page.goto(f"{app_base(context)}/app/payments/orders",
                  wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
        frame = ev._frame_with(page, ev.STATUS_FILTER)
        if frame is None:
            continue
        ev._apply_status_filter(page, frame, ev.STATUS_VALUE["PAID"])
        row = frame.locator(ev.ORDER_ROW).filter(has_text=event_name)
        deadline = time.monotonic() + NAV_TIMEOUT / 1000
        while time.monotonic() < deadline:
            if row.count() > 0 and row.first.is_visible():
                row.first.click()
                ev._payment_status_frame(page)
                return
            page.wait_for_timeout(300)
        page.wait_for_timeout(1000)
    raise AssertionError(f"Paid order for '{event_name}' not found in Billing & Invoicing")


# --------------------------------------------------------------------------- #
# Back-office payment page assertion (with tip)
# --------------------------------------------------------------------------- #
def assert_payment_page_with_tip(page: Page, context: dict, expected: dict) -> None:
    """Open the payment by name from Payments Received and assert every provided field:
    client_name, name, amount, type, items (comma list, sorted), tip."""
    _open_payment(page, context, expected)
    detail = _frame_with(page, PAYMENT_NAME)
    if detail is None:
        raise AssertionError("Payment detail page did not load")
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    actual: dict = {}
    while time.monotonic() < deadline:
        actual = _read_payment(detail, expected)
        if all(actual.get(k) == v for k, v in expected.items() if k != "search"):
            return
        page.wait_for_timeout(400)
    mismatch = {k: (v, actual.get(k)) for k, v in expected.items()
                if k != "search" and actual.get(k) != v}
    raise AssertionError(f"Payment page mismatch (expected, actual): {mismatch}")


def _open_payment(page: Page, context: dict, expected: dict) -> None:
    search_term = expected.get("search") or expected.get("client_name") or ""
    title = expected["name"]
    for _ in range(3):
        page.goto(f"{app_base(context)}/app/payments/transactions",
                  wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
        frame = _frame_with(page, NAME_FILTER)
        if frame is None:
            continue
        if search_term:
            frame.locator(NAME_FILTER).first.fill(search_term, timeout=UI_TIMEOUT)
        row = frame.locator(PAYMENT_ROW).filter(has_text=title)
        deadline = time.monotonic() + UI_TIMEOUT / 1000
        while time.monotonic() < deadline:
            if row.count() > 0 and row.first.is_visible():
                row.first.locator("xpath=ancestor::a[1]").click()
                return
            page.wait_for_timeout(300)
        page.wait_for_timeout(1000)
    raise AssertionError(f"Payment '{title}' not found in Payments Received")


def _read_payment(frame: Frame, expected: dict) -> dict:
    frame.locator(PAYMENT_NAME).first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    data: dict = {"name": frame.locator(PAYMENT_NAME).first.inner_text().strip()}
    if "amount" in expected:
        data["amount"] = " ".join(frame.locator(PAYMENT_AMOUNT).first.inner_text().split())
    if "client_name" in expected:
        el = frame.locator(PAYMENT_CLIENT).first
        data["client_name"] = el.inner_text().strip() if el.count() > 0 else ""
    if "type" in expected:
        el = frame.locator(PAYMENT_TYPE).first
        data["type"] = el.inner_text().strip() if el.count() > 0 else ""
    if "items" in expected:
        items = [i.strip() for i in frame.locator(PAYMENT_ITEM).all_inner_texts()]
        data["items"] = ",".join(sorted(items))
    if "tip" in expected:
        el = frame.locator(PAYMENT_TIP).first
        data["tip"] = el.inner_text().strip() if el.count() > 0 else ""
    return data
