# Source: tests/payments/product_payments/edit_cancel_request/edit_cancel/script.md
# Migrated from automation-js/features/salsa/products.feature (VCITA2-13858)

from playwright.sync_api import Page

from tests.salsa.payments.product_payments.product_payments_helpers import (
    assert_product_payment_request,
    cancel_product_request,
    edit_product_amount,
)


def test_edit_cancel(page: Page, context: dict) -> None:
    """Edit the product payment request to $20 (DUE) then cancel it (CANCELLED)."""
    print("  Step 1: Edit product payment request amount to $20")
    edit_product_amount(page, context, "20", "payable_item1")
    assert_product_payment_request(page, context, {
        "state": "DUE", "amount": "$20.00",
        "product_name": "payable_item1", "client_full_name": "first last",
    }, "payable_item1")

    print("  Step 2: Cancel the product payment request")
    cancel_product_request(page, context, refund=False, product_name="payable_item1")
    assert_product_payment_request(page, context, {
        "state": "CANCELLED", "amount": "$20.00",
        "product_name": "payable_item1", "client_full_name": "first last",
    }, "payable_item1")

    print("  [OK] edit + cancel product payment request verified")
