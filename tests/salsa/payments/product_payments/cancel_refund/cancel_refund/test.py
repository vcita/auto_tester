# Source: tests/payments/product_payments/cancel_refund/cancel_refund/script.md
# Migrated from automation-js/features/salsa/products.feature (VCITA2-13858)

from playwright.sync_api import Page

from tests.salsa.payments.event_payments.event_payments_helpers import (
    open_payment_detail_and_assert_title,
)
from tests.salsa.payments.product_payments.product_payments_helpers import (
    assert_product_payment_request,
    cancel_product_request,
    pay_for_product,
)


def test_cancel_refund(page: Page, context: dict) -> None:
    """Pay $5, cancel the product request with refund (CANCELLED $10.00), and
    open the refunded payment to assert its detail header (legacy 'payment was
    refunded')."""
    print("  Step 1: Pay $5 for payable_item1")
    pay_for_product(page, context, "5", "payable_item1")

    print("  Step 2: Cancel the product payment request with a refund")
    cancel_product_request(page, context, refund=True, product_name="payable_item1")
    assert_product_payment_request(page, context, {
        "state": "CANCELLED", "amount": "$10.00",
        "product_name": "payable_item1", "client_full_name": "first last",
    }, "payable_item1")

    print("  Step 3: Payment refunded (open payment, assert detail title)")
    open_payment_detail_and_assert_title(
        page, context, "first", "Payment for payable_item1")

    print("  [OK] cancel & refund paid product verified")
