"""UI assertions for the external-receipt gateway_setups subcategories (4 & 5).

Opens the recorded payment from Payments Received, verifies the payment-page client
name + title, then opens the external receipt (``mockreceipts`` app) in a new tab and
asserts its URL — mirroring the legacy ``payment page displays`` + ``first payment has
external receipt`` steps. The legacy check is a URL substring (the mock app redirects to
``this-is-a-receipt-for-pdf-<id>``), so success = the View-receipt tab lands on that URL.

The Angular payment detail renders inside the ``angularjs`` iframe, so assertions resolve
the billing scope first (reusing the partial-refund pattern). Waits are capped at 5s;
the receipt tab open (external redirect) gets a bounded 15s budget.
"""

import re

from playwright.sync_api import Page

from tests.payments.refunds_credits.partial_refund_helpers import (
    FAST_UI_TIMEOUT,
    get_billing_scope,
    open_payment_by_name,
)

NEW_TAB_TIMEOUT = 15000
MOCK_RECEIPT_URL = "this-is-a-receipt-for-pdf-"

PAYMENT_TITLE = "div.summary-header h3"
PAYMENT_CLIENT = "span.contact-name, div .display-name-component span"
VIEW_RECEIPT = "[data-qa='view_receipt']"


def open_payment(page: Page, client_name: str, payment_title: str):
    """Open the recorded payment by title from Payments Received; return the billing scope."""
    return open_payment_by_name(page, client_name, payment_title)


def assert_payment_page(page: Page, *, client_name: str, payment_title: str) -> None:
    """Assert the open payment page shows the expected client name and payment title."""
    scope = get_billing_scope(page)
    title_el = scope.locator(PAYMENT_TITLE).first
    title_el.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    actual_title = (title_el.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip()
    if payment_title not in actual_title:
        raise AssertionError(f"Payment title: expected '{payment_title}', got '{actual_title}'")

    client_el = scope.locator(PAYMENT_CLIENT).first
    client_el.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    actual_client = (client_el.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip()
    if client_name.lower() not in actual_client.lower():
        raise AssertionError(f"Payment client: expected '{client_name}', got '{actual_client}'")


def assert_external_receipt(page: Page) -> None:
    """Open the external receipt from the open payment page and assert its mock URL.

    The View-receipt link opens the mockreceipts redirect in a new tab; success is the
    tab URL containing the mock receipt substring (legacy ``url.should.include``).
    """
    scope = get_billing_scope(page)
    view_receipt = scope.locator(VIEW_RECEIPT).first
    view_receipt.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)

    with page.context.expect_page(timeout=NEW_TAB_TIMEOUT) as new_tab_info:
        view_receipt.click(timeout=FAST_UI_TIMEOUT)
    receipt_tab = new_tab_info.value
    try:
        receipt_tab.wait_for_load_state("domcontentloaded", timeout=NEW_TAB_TIMEOUT)
        url = receipt_tab.url or ""
        if MOCK_RECEIPT_URL not in url:
            raise AssertionError(
                f"External receipt URL did not contain '{MOCK_RECEIPT_URL}': got '{url}'"
            )
    finally:
        if not receipt_tab.is_closed():
            receipt_tab.close()
