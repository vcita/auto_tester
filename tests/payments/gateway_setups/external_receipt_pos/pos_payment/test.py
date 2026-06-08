from playwright.sync_api import Page

from tests.payments.deposits.deposits_pos_ui import record_pos_custom_payment
from tests.payments.gateway_setups.gateway_setups_ui import (
    assert_external_receipt,
    assert_payment_page,
    open_payment,
)

ITEM_NAME = "some_item"
ITEM_PRICE = "20"
PAYMENT_TITLE = "Payment for Sale #1 - some_item"


def test_pos_payment(page: Page, context: dict) -> None:
    client_name = context["receipt_client_name"]
    # The reused deposits POS helper reads the client from context["deposit_client_name"].
    context["deposit_client_name"] = client_name

    print("  Step 1: Create a custom item ($20) and record a Cash sale via POS for 'simon bolivar'")
    record_pos_custom_payment(page, context, ITEM_NAME, ITEM_PRICE)

    print("  Step 2: Open the payment and verify client + 'Payment for Sale #1 - some_item'")
    open_payment(page, client_name, PAYMENT_TITLE)
    assert_payment_page(page, client_name=client_name, payment_title=PAYMENT_TITLE)

    print("  Step 3: Verify the payment exposes the external (mockreceipts) receipt")
    assert_external_receipt(page)
