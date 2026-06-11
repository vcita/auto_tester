# Source: tests/payments/product_payments/pay_for_product/pay_product/script.md
# Migrated from automation-js/features/salsa/products.feature (VCITA2-13858)

from playwright.sync_api import Page

from tests.salsa.payments.product_payments.product_payments_helpers import (
    assert_order_listed,
    assert_product_payment_request,
    pay_for_product,
    search_payments,
)


def test_pay_product(page: Page, context: dict) -> None:
    """Record a $2 payment (DUE $8.00 of $10.00) then an $8 payment (PAID $10.00),
    verifying the order listing and Payments Received after each."""
    payment_title = "Payment for payable_item1"

    print("  Step 1: Pay $2 -> DUE $8.00 (out of $10.00)")
    pay_for_product(page, context, "2", "payable_item1")
    assert_product_payment_request(page, context, {
        "state": "DUE", "amount": "$8.00 (out of $10.00)",
        "product_name": "payable_item1", "client_full_name": "first last",
    }, "payable_item1")
    assert_order_listed(page, context, "payable_item1")
    search_payments(page, context, "first", payment_title, expected_count=1)

    print("  Step 2: Pay $8 -> PAID $10.00")
    pay_for_product(page, context, "8", "payable_item1")
    assert_product_payment_request(page, context, {
        "state": "PAID", "amount": "$10.00",
        "product_name": "payable_item1", "client_full_name": "first last",
    }, "payable_item1")
    search_payments(page, context, "first", payment_title, expected_count=2)

    print("  [OK] pay-for-product partial + full verified")
