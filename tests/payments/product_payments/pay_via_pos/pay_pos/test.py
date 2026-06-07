# Source: tests/payments/product_payments/pay_via_pos/pay_pos/script.md
# Migrated from automation-js/features/salsa/products.feature (VCITA2-13858)

from playwright.sync_api import Page

from tests.payments.product_payments.product_payments_helpers import (
    assert_product_payment_request,
    record_product_via_pos,
    search_payments,
)


def test_pay_pos(page: Page, context: dict) -> None:
    """Record the product payment via Point of Sale (PAID $10.00) and verify the
    Sale payment in Payments Received."""
    print("  Step 1: Record payable_item1 payment via Point of Sale")
    record_product_via_pos(page, context, "payable_item1")
    assert_product_payment_request(page, context, {
        "state": "PAID", "amount": "$10.00",
        "product_name": "payable_item1", "client_full_name": "first last",
    }, "payable_item1")

    print("  Step 2: Verify the Sale payment in Payments Received")
    search_payments(page, context, "first", "Payment for Sale #1 - payable_item1",
                    expected_count=1)

    print("  [OK] pay-for-product via POS verified")
