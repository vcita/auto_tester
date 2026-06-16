"""UI flow for the POS record path of the deposits invoice scenario (#2).

Opens the POS via Quick Actions -> Take payment, creates a custom item, and records a
Cash payment (sale). Each call produces one "Sale" whose payment is titled
"Payment for Sale #N - <item>"; the invoice then assigns that payment as its deposit
(reusing the invoice helpers from deposits_invoice_ui).

The POS page and take-payment dialog are POV/Angular top-level controls, so controls are
resolved across the page and all frames. Explicit waits are capped at 5s.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

from tests.salsa.payments.deposits.deposits_invoice_ui import (
    FAST_UI_TIMEOUT,
    LOAD_TIMEOUT,
    QUICK_ACTIONS_BUTTON,
    _find_control,
    _require,
    _select_client,
)

# Quick Actions (POS entry)
TAKE_PAYMENT_ITEM = '[data-qa="VcLargeQuickAction-point_of_sale"]'

# POS page
POS_ADD_CUSTOM_ITEM = '[data-qa="pos-add-custom-item"]'
POS_CHECKOUT_ACTIVATOR = '[data-qa="checkout-actions-activator"]'
POS_CHECKOUT_RECORD = '[data-qa="checkout-action-record"]'

# Create-custom-item dialog
CUSTOM_ITEM_NAME = "[data-qa=item-name]"
CUSTOM_ITEM_PRICE = "[data-qa=custom-item-price]"
CUSTOM_ITEM_ADD = 'button[data-qa="vc-footer-Add"]'

# Take-payment dialog (sale mode)
TAKE_PAYMENT_DIALOG = "md-dialog.take-payment-wrapper, md-dialog.close-balance-content"
RECORD_METHOD_SELECT = "md-select[name='payment_method']"
RECORD_METHOD_OPTION = 'div.md-select-menu-container.md-active md-option:has-text("Cash")'
TAKE_PAYMENT_CONFIRM = '[data-qa="take-payment-confirmation"][aria-disabled="false"]'


def record_pos_custom_payment(page: Page, context: dict, item_name: str, price: str) -> None:
    """Open the POS for the client, create a custom item, and record a Cash sale."""
    client_name = context["deposit_client_name"]

    button = _require(page, QUICK_ACTIONS_BUTTON, "Quick Actions button", timeout=LOAD_TIMEOUT)
    button.click(timeout=FAST_UI_TIMEOUT)
    take_payment = _require(page, TAKE_PAYMENT_ITEM, "Take payment (POS) quick action")
    take_payment.click(timeout=FAST_UI_TIMEOUT)

    _select_client(page, client_name)

    # Create the custom item on the POS catalog.
    add_item = _require(page, POS_ADD_CUSTOM_ITEM, "POS add custom item button", timeout=LOAD_TIMEOUT)
    add_item.click(timeout=FAST_UI_TIMEOUT)
    _require(page, CUSTOM_ITEM_NAME, "Custom item name field").fill(item_name, timeout=FAST_UI_TIMEOUT)
    _require(page, CUSTOM_ITEM_PRICE, "Custom item price field").fill(price, timeout=FAST_UI_TIMEOUT)
    _require(page, CUSTOM_ITEM_ADD, "Custom item Add button").click(timeout=FAST_UI_TIMEOUT)

    # Checkout -> Record payment (Cash).
    activator = _require(page, POS_CHECKOUT_ACTIVATOR, "POS checkout activator", timeout=LOAD_TIMEOUT)
    activator.click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_CHECKOUT_RECORD, "POS record-payment action").click(timeout=FAST_UI_TIMEOUT)

    _require(page, TAKE_PAYMENT_DIALOG, "Take payment dialog", timeout=LOAD_TIMEOUT)
    _require(page, RECORD_METHOD_SELECT, "Record method picker").click(timeout=FAST_UI_TIMEOUT)
    _require(page, RECORD_METHOD_OPTION, "Cash record method option").click(timeout=FAST_UI_TIMEOUT)
    _require(page, TAKE_PAYMENT_CONFIRM, "Take payment confirm button").click(timeout=FAST_UI_TIMEOUT)

    # The sale is recorded once the take-payment dialog closes.
    deadline = time.monotonic() + LOAD_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if _find_control(page, TAKE_PAYMENT_DIALOG, timeout=300) is None:
            return
        time.sleep(0.2)
    raise AssertionError("Take payment dialog did not close after recording the sale")
