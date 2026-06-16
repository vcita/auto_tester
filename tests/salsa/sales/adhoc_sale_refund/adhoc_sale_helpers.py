"""Helpers for the ad-hoc sale + refund scenario (migrated from automation-js).

Covers the client-portal public "make a payment" form paid through the mock
gateway popup, the back-office Orders status-filter assertion, the Sales detail
(sale page) reader, the Payments-Received search assertion, and a full refund.

Selector policy (see prefer-data-qa-selectors): data-qa first, then the legacy
stable Angular selectors for back-office Billing/Sales views that have no data-qa
yet (`[name="status_filter"]`, `[value="paid|cancelled"]`,
`f-ellipsis-tooltip.payment-title`, sale `span.main-title/price/status-text/data-part`).
Those data-qa attributes should be added in the product code.

Waits: element/dialog/state waits are capped at 5s. `NAV_TIMEOUT` (portal/app
(re)navigation) and `POPUP_TIMEOUT` (external mock-gateway popup round-trip) are
the only longer, justified readiness budgets; retries are capped at 2.
"""

from __future__ import annotations

import re
import time

from playwright.sync_api import Page, expect

from tests.salsa.sales.estimates.estimates_helpers import (
    CP_VITRAGE,
    NAV_TIMEOUT,
    billing_scope,
    pivot_uid,
)
from tests.salsa.payments.refunds_credits.partial_refund_helpers import (
    _refund_submit_button,
    _trigger_refund_action,
    open_payment_by_name,
)

FAST_UI_TIMEOUT = 5000
STATE_TIMEOUT = 5000
POPUP_TIMEOUT = 20000  # external mock-gateway popup round-trip (eventual consistency)
ORDERS_RELOAD_RETRIES = 2  # orders/transactions indexing can lag the synchronous order

CP_IFRAME = "#cp_iframe"
EMAIL_FIELD = '[data-qa="email-input"]'
CHECKOUT_BUTTON_RE = re.compile(r"checkout", re.I)
PROCEED_TO_PAYMENT = '[data-qa="perform-payment-action"]'
MOCK_SUBMIT = "button[type=submit]"
SUCCESS_PAGE = "[data-qa='payment-success-page']"
SUCCESS_TITLE = "span.briliant"
SUCCESS_SUBTITLE = "span.thanks"
SUCCESS_AMOUNT = "span.paymet-text"

PAYMENT_ROW = "f-ellipsis-tooltip.payment-title"
STATUS_FILTER = '[name="status_filter"]'
STATUS_VALUE = {"PAID": "paid", "CANCELLED": "cancelled"}

# Sale detail (legacy `vue_iframe_main`) fields
SALE_NAME = "span.main-title"
SALE_PRICE = "span.price"
SALE_STATUS = "span.status-text"
SALE_CLIENT = "span.data-part"


# --------------------------------------------------------------------------- #
# Client portal — public make-payment form
# --------------------------------------------------------------------------- #
def open_payment_form(page: Page, context: dict, *, pay_for: str, amount: str):
    """Open the public client-portal make-payment form in a fresh browser context.

    Mirrors legacy CPPaymentForm.goto: /site/{pivot}/make-payment?title=&amount=.
    Returns (cp_page, cp_context)."""
    cp_context = page.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/New_York"
    )
    cp_page = cp_context.new_page()
    url = f"{CP_VITRAGE}/site/{pivot_uid(context)}/make-payment?title={pay_for}&amount={amount}"
    cp_page.goto(url, wait_until="domcontentloaded")
    return cp_page, cp_context


def _fill_form_field(cp_frame, label: str, value: str, *, timeout: int = FAST_UI_TIMEOUT) -> None:
    """Fill a make-payment form field by label, with a legacy label/input fallback."""
    field = cp_frame.get_by_label(label)
    if field.count() == 0:
        field = cp_frame.locator(f"xpath=//label[contains(.,'{label}')]/../input")
    field.first.wait_for(state="visible", timeout=timeout)
    field.first.fill(value, timeout=FAST_UI_TIMEOUT)


def pay_via_mock_gateway(cp_page: Page, *, email: str, first_name: str) -> None:
    """Fill the payment form, submit, and pay through the mock-gateway popup.

    Mirrors legacy: submit form -> checkout proceed -> mock popup submit.
    The make-payment form renders inside `#cp_iframe`, which is a navigation-level
    load, so the first field uses the NAV readiness budget."""
    cp_frame = cp_page.frame_locator(CP_IFRAME)

    email_field = cp_frame.locator(EMAIL_FIELD).first
    email_field.wait_for(state="visible", timeout=NAV_TIMEOUT)
    email_field.fill(email, timeout=FAST_UI_TIMEOUT)
    _fill_form_field(cp_frame, "First Name", first_name)

    checkout = cp_frame.get_by_role("button", name=CHECKOUT_BUTTON_RE).first
    checkout.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    checkout.click(timeout=FAST_UI_TIMEOUT)

    proceed = cp_frame.locator(PROCEED_TO_PAYMENT).first
    proceed.wait_for(state="visible", timeout=NAV_TIMEOUT)
    with cp_page.context.expect_page(timeout=POPUP_TIMEOUT) as popup_info:
        proceed.click(timeout=FAST_UI_TIMEOUT)
    popup = popup_info.value
    popup.wait_for_load_state("domcontentloaded")
    submit = popup.locator(MOCK_SUBMIT).first
    submit.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    submit.click()
    try:
        popup.wait_for_event("close", timeout=POPUP_TIMEOUT)
    except Exception:
        pass


def assert_payment_success(cp_page: Page, *, title: str, subtitle: str, amount: str) -> None:
    """Verify the client-portal payment success page (title, subtitle, amount)."""
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    cp_frame.locator(SUCCESS_PAGE).first.wait_for(state="visible", timeout=NAV_TIMEOUT)

    expect(cp_frame.locator(SUCCESS_TITLE).first).to_contain_text(title, timeout=FAST_UI_TIMEOUT)
    expect(cp_frame.locator(SUCCESS_AMOUNT).first).to_contain_text(amount, timeout=FAST_UI_TIMEOUT)

    subtitle_el = cp_frame.locator(SUCCESS_SUBTITLE).first
    if subtitle_el.count() > 0:
        expect(subtitle_el).to_contain_text(subtitle, timeout=FAST_UI_TIMEOUT)


# --------------------------------------------------------------------------- #
# Back office — Orders list + status filter
# --------------------------------------------------------------------------- #
def _app_base(context: dict) -> str:
    return (context.get("base_url") or context.get("app_base_url") or "").rstrip("/")


def _goto_orders(page: Page, context: dict):
    page.goto(f"{_app_base(context)}/app/payments/orders", wait_until="domcontentloaded")
    return billing_scope(page)


def _apply_status_filter(page: Page, scope, status: str) -> None:
    """Select only the target status in the Orders status filter (mirrors legacy)."""
    value = STATUS_VALUE[status.upper()]
    dropdown = scope.locator(STATUS_FILTER).first
    dropdown.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    dropdown.click(timeout=FAST_UI_TIMEOUT)

    target = scope.locator(f'[value="{value}"]').first
    target.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)

    # Deselect any other currently-selected status options so only the target remains.
    for other in STATUS_VALUE.values():
        if other == value:
            continue
        opt = scope.locator(f'[value="{other}"]').first
        try:
            if opt.count() > 0 and opt.get_attribute("selected") is not None:
                opt.click(timeout=FAST_UI_TIMEOUT)
        except Exception:
            continue

    if target.get_attribute("selected") is None:
        target.click(timeout=FAST_UI_TIMEOUT)
    page.keyboard.press("Escape")


def assert_order_in_status(page: Page, context: dict, status: str, expected_title: str) -> None:
    """Filter Orders by status and assert the expected order title is listed."""
    last_error = None
    for attempt in range(ORDERS_RELOAD_RETRIES + 1):
        scope = _goto_orders(page, context)
        try:
            _apply_status_filter(page, scope, status)
            row = scope.locator(PAYMENT_ROW).filter(has_text=expected_title).first
            expect(row).to_be_visible(timeout=STATE_TIMEOUT)
            return
        except Exception as exc:  # noqa: BLE001 - bounded retry on indexing lag
            last_error = exc
            if attempt < ORDERS_RELOAD_RETRIES:
                page.wait_for_timeout(1000)
    raise AssertionError(
        f"Order '{expected_title}' not found under status '{status}': {last_error}"
    )


# --------------------------------------------------------------------------- #
# Back office — Payments Received search
# --------------------------------------------------------------------------- #
def assert_payment_in_search(page: Page, context: dict, search_term: str, expected_title: str) -> None:
    """Search Payments Received by name and assert the expected payment title is listed."""
    from tests.salsa.payments.refunds_credits.partial_refund_helpers import open_payments_received

    last_error = None
    for attempt in range(ORDERS_RELOAD_RETRIES + 1):
        scope = open_payments_received(page)
        try:
            search = scope.locator('input[name="name_filter"]').first
            search.wait_for(state="visible", timeout=STATE_TIMEOUT)
            search.fill(search_term, timeout=FAST_UI_TIMEOUT)
            row = scope.locator(PAYMENT_ROW).filter(has_text=expected_title).first
            expect(row).to_be_visible(timeout=STATE_TIMEOUT)
            return
        except Exception as exc:  # noqa: BLE001 - bounded retry on indexing lag
            last_error = exc
            if attempt < ORDERS_RELOAD_RETRIES:
                page.wait_for_timeout(1000)
    raise AssertionError(
        f"Payment '{expected_title}' not found in search '{search_term}': {last_error}"
    )


# --------------------------------------------------------------------------- #
# Back office — Sale detail page
# --------------------------------------------------------------------------- #
def _open_sale(page: Page, context: dict, sale_name: str) -> None:
    scope = _goto_orders(page, context)
    link = scope.locator(
        f"xpath=//div[normalize-space(text())={_xpath_literal(sale_name)}]/ancestor::a"
    ).first
    link.wait_for(state="visible", timeout=NAV_TIMEOUT)
    link.click(timeout=FAST_UI_TIMEOUT)


def _xpath_literal(value: str) -> str:
    """Quote a string for safe use as an XPath literal."""
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    parts = value.split("'")
    return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"


def _read_sale_data(page: Page) -> dict:
    """Read sale detail (name, amount, state, client) from the nested sale iframe."""
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    last_error = None
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(SALE_PRICE).count() == 0 or frame.locator(SALE_STATUS).count() == 0:
                    continue
                name = (frame.locator(SALE_NAME).first.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip()
                price = (frame.locator(SALE_PRICE).first.inner_text(timeout=FAST_UI_TIMEOUT) or "")
                price = price.replace("US", "").strip()
                state = (frame.locator(SALE_STATUS).first.inner_text(timeout=FAST_UI_TIMEOUT) or "")
                state = state.replace(":", "").strip()
                client = (frame.locator(SALE_CLIENT).first.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip()
                if name and price and state:
                    return {"sale_name": name, "amount": price, "state": state, "client_full_name": client}
            except Exception as exc:  # noqa: BLE001 - frame may detach mid SPA render
                last_error = exc
                continue
        page.wait_for_timeout(300)
    raise AssertionError(f"Sale detail did not render in any frame: {last_error}")


def assert_sale_page(
    page: Page,
    context: dict,
    *,
    sale_name: str,
    client_full_name: str,
    state: str,
    amount: str,
) -> None:
    """Open the order and assert the sale page name, client, state, and amount."""
    _open_sale(page, context, sale_name)
    data = _read_sale_data(page)
    _assert_eq(data["sale_name"], sale_name, "sale name")
    _assert_eq(data["state"], state, "sale state")
    _assert_in(amount, data["amount"], "sale amount")
    _assert_in(client_full_name, data["client_full_name"], "sale client")


def assert_sale_state(page: Page, context: dict, *, sale_name: str, state: str) -> None:
    """Re-open the order and assert only the sale state (used after refund)."""
    _open_sale(page, context, sale_name)
    data = _read_sale_data(page)
    _assert_eq(data["state"], state, "sale state")


def _assert_eq(actual: str, expected: str, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected '{expected}', got '{actual}'")


def _assert_in(expected: str, actual: str, label: str) -> None:
    if expected not in actual:
        raise AssertionError(f"{label}: expected to contain '{expected}', got '{actual}'")


# --------------------------------------------------------------------------- #
# Back office — full refund
# --------------------------------------------------------------------------- #
def refund_payment(page: Page, search_term: str, payment_name: str) -> None:
    """Open the payment from Payments Received and issue a full refund."""
    scope = open_payment_by_name(page, search_term, payment_name)
    _trigger_refund_action(page, scope)
    submit = _refund_submit_button(page)
    if submit is None:
        raise AssertionError("Refund confirm button did not appear")
    expect(submit).to_be_enabled(timeout=STATE_TIMEOUT)
    submit.click(timeout=FAST_UI_TIMEOUT)
    _wait_refund_acknowledged(page)


def _wait_refund_acknowledged(page: Page) -> None:
    """Best-effort wait for the refund toast/confirmation within the 5s cap."""
    deadline = time.monotonic() + STATE_TIMEOUT / 1000
    pattern = re.compile(r"refund issued|marked as refunded|refunded", re.I)
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.get_by_text(pattern).count() > 0:
                    return
            except Exception:
                continue
        time.sleep(0.2)
