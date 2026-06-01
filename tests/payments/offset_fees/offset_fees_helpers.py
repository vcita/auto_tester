"""Fee-configuration and back-office verification helpers for offset_fees.

`enable_convenience_fee` / `enable_surcharge` configure the offset-fee mode on the
POV Online Payments tab (the feature under test). The back-office helpers reopen
the resulting payment and verify the client, name, amount, items, and fee, mirroring
the legacy PaymentsReceived / PaymentPage assertions.
"""

from __future__ import annotations

import re
import time

from playwright.sync_api import Page

from tests.payments.offset_fees.offset_fees_ui import (
    FAST_UI_TIMEOUT,
    click_via_dom,
    find_control,
    open_online_payments_tab,
    save_online_payments,
)

RADIO_GROUP = '[data-qa="online-payments-tab-offset-card-fees-radio-group"]'
MODE_INPUT = RADIO_GROUP + " input[value='{mode}']"
FORMAT_PERCENTAGE = '[data-qa="online-payments-tab-offset-card-fees-fee-format-item-1"]'
FORMAT_FLAT = '[data-qa="online-payments-tab-offset-card-fees-fee-format-item-0"]'
# The data-qa wrapper does not always nest the native input, so fall back to the
# offset-card-fees number input (mirrors the legacy fee-input fallback selector).
FEE_INPUT = (
    '[data-qa="online-payments-tab-offset-card-fees-fee-input"] input, '
    ".offset-card-fees input[type='number'], "
    ".offset-card-fees__fee-input-wrapper input"
)
# The data-qa wrapper may not contain a hittable <label>; fall back to the
# offset-card-fees acknowledgement label or the wrapper itself (mirrors legacy).
ACKNOWLEDGEMENT = (
    '[data-qa="online-payments-tab-offset-card-fees-acknowledgement-checkbox"] label, '
    ".offset-card-fees__acknowledgement label, "
    '[data-qa="online-payments-tab-offset-card-fees-acknowledgement-checkbox"]'
)

PAYMENTS_TRANSACTIONS = "/app/payments/transactions"
NAME_FILTER = 'input[name="name_filter"]'
# Returning from the client-portal live site to the back office is a full document
# navigation; the AngularJS Payments Received list cold-loads slower than a single
# in-page interaction, so its readiness is given a page-load budget (not an element wait).
BO_PAGE_LOAD_TIMEOUT = 15000
PAYMENT_NAME = "div.summary-header h3"
PAYMENT_AMOUNT = "div.summary-header h2 span"
PAYMENT_CLIENT = "span.contact-name, div .display-name-component span"
PAYMENT_ITEMS = "span.invoice-item-content-title"
FEE_ROW = "div.entity-summary-row"
FEE_REGEX = re.compile(r"(?:Surcharge|Convenience)(?:\s+Fee)?\s*\$?\s*([0-9]+\.[0-9]{2})", re.I)


def enable_convenience_fee(page: Page, context: dict, fee_format: str, value: str) -> None:
    """Enable a convenience fee of the given format ('percentage' or 'flat') and value."""
    scope = open_online_payments_tab(page, context)
    scope.locator(RADIO_GROUP).first.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    _select_mode(scope, "convenience_fee")
    # Percentage must be activated first; flat only becomes selectable afterwards.
    scope.locator(FORMAT_PERCENTAGE).first.click(timeout=FAST_UI_TIMEOUT)
    if fee_format == "flat":
        scope.locator(FORMAT_FLAT).first.click(timeout=FAST_UI_TIMEOUT)
    fee_input = find_control(page, FEE_INPUT, timeout=FAST_UI_TIMEOUT)
    if fee_input is None:
        raise AssertionError("Offset-fee value input did not appear (two payment methods required)")
    fee_input.fill(str(value), timeout=FAST_UI_TIMEOUT)
    _acknowledge_and_save(page, scope)


def enable_surcharge(page: Page, context: dict) -> None:
    """Enable the surcharge offset-fee mode (product default percentage, no value input)."""
    scope = open_online_payments_tab(page, context)
    scope.locator(RADIO_GROUP).first.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    _select_mode(scope, "surcharge_fee")
    _acknowledge_and_save(page, scope)


def assert_back_office_payment(
    page: Page, context: dict, amount: str, fee: str, items: list[str]
) -> None:
    """Reopen the payment from Payments Received and verify client, name, amount, items, fee."""
    scope = _open_payment(page, context)
    client_name = context["created_client_name"]
    # Mirror the legacy assertion: the detail header reads "Payment for <service>".
    payment_name = f"Payment for {context['offset_service_name']}"

    expect_text(scope.locator(PAYMENT_CLIENT).first, client_name)
    expect_text(scope.locator(PAYMENT_NAME).first, payment_name)
    expect_text(scope.locator(PAYMENT_AMOUNT).first, amount)

    actual_items = sorted(scope.locator(PAYMENT_ITEMS).all_inner_texts())
    assert sorted(items) == [i.strip() for i in actual_items], (
        f"Payment items mismatch: expected {sorted(items)}, got {actual_items}"
    )

    actual_fee = _read_fee(scope)
    assert actual_fee == fee, f"Payment fee mismatch: expected {fee}, got {actual_fee}"


def expect_text(locator, expected: str, timeout: int = FAST_UI_TIMEOUT) -> None:
    deadline = time.monotonic() + timeout / 1000
    last = ""
    while time.monotonic() < deadline:
        try:
            last = locator.inner_text(timeout=1000)
            if expected in last:
                return
        except Exception:
            pass
        time.sleep(0.2)
    raise AssertionError(f"Expected text '{expected}' but found '{last}'")


def _select_mode(scope, mode: str) -> None:
    mode_input = scope.locator(MODE_INPUT.format(mode=mode)).first
    mode_input.wait_for(state="attached", timeout=FAST_UI_TIMEOUT)
    click_via_dom(mode_input)


def _acknowledge_and_save(page: Page, scope) -> None:
    ack = find_control(page, ACKNOWLEDGEMENT, timeout=FAST_UI_TIMEOUT)
    if ack is None:
        raise AssertionError("Offset-fee acknowledgement checkbox did not appear")
    click_via_dom(ack)
    save_online_payments(scope)


def _billing_scope(page: Page):
    """Angular billing content renders inside the angularjs iframe."""
    if page.locator(".payment-component, .summary-header").count() > 0:
        return page
    iframe = page.locator('iframe[title="angularjs"]')
    if iframe.count() > 0:
        iframe.first.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
        return page.frame_locator('iframe[title="angularjs"]')
    return page


def _open_payment(page: Page, context: dict):
    base = (context.get("base_url") or "").rstrip("/")
    page.goto(f"{base}{PAYMENTS_TRANSACTIONS}", wait_until="domcontentloaded")

    search = _wait_search_input(page)
    if search is None:
        raise AssertionError("Payments Received search did not load")
    search.fill(context["created_client_name"].split(" ")[0], timeout=FAST_UI_TIMEOUT)

    # The list row title is the service name (the detail header reads "Payment for ...").
    service_name = context["offset_service_name"]
    scope = _billing_scope(page)
    link = scope.locator("a").filter(has_text=service_name).first
    deadline = time.monotonic() + FAST_UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if link.count() > 0 and link.is_visible():
            break
        time.sleep(0.3)
    link.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    link.evaluate("(el) => el.click()")
    page.wait_for_url(f"**{PAYMENTS_TRANSACTIONS}/**", wait_until="domcontentloaded", timeout=FAST_UI_TIMEOUT)
    return _billing_scope(page)


def _wait_search_input(page: Page):
    """Resolve the Payments Received name filter, re-resolving the Angular scope."""
    deadline = time.monotonic() + BO_PAGE_LOAD_TIMEOUT / 1000
    while time.monotonic() < deadline:
        search = _billing_scope(page).locator(NAME_FILTER).first
        try:
            if search.count() > 0 and search.is_visible():
                return search
        except Exception:
            pass
        time.sleep(0.3)
    return None


def _read_fee(scope) -> str:
    texts = scope.locator(FEE_ROW).all_inner_texts()
    match = FEE_REGEX.search(" ".join(texts))
    if not match:
        match = FEE_REGEX.search(scope.locator("body").first.inner_text(timeout=FAST_UI_TIMEOUT))
    return f"${float(match.group(1)):.2f}" if match else ""
