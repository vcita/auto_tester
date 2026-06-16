from playwright.sync_api import Page

from tests.salsa.payments.deposits.deposits_invoice_ui import record_custom_payment
from tests.salsa.payments.gateway_setups.gateway_setups_ui import (
    assert_external_receipt,
    assert_payment_page,
    open_payment,
)

ITEM_NAME = "some_item"
ITEM_AMOUNT = "5"
PAYMENT_TITLE = "Payment for some_item"


def test_record_payment(page: Page, context: dict) -> None:
    client_name = context["receipt_client_name"]
    # The reused deposits record helper reads the client from context["deposit_client_name"].
    context["deposit_client_name"] = client_name

    print("  Step 1: Record a custom-item ($5) payment for 'simon bolivar' via Quick Actions")
    record_custom_payment(page, context, ITEM_NAME, ITEM_AMOUNT)

    print("  Step 2: Open the payment and verify client + 'Payment for some_item'")
    open_payment(page, client_name, PAYMENT_TITLE)
    assert_payment_page(page, client_name=client_name, payment_title=PAYMENT_TITLE)

    print("  Step 3: Verify the payment exposes the external (mockreceipts) receipt")
    assert_external_receipt(page)
