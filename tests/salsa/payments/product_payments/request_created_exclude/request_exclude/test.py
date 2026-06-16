# Source: tests/payments/product_payments/request_created_exclude/request_exclude/script.md
# Migrated from automation-js/features/salsa/products.feature (VCITA2-13858)

from playwright.sync_api import Page

from tests.salsa.payments.product_payments.product_payments_api import assign_taxes
from tests.salsa.payments.product_payments.product_payments_helpers import (
    assert_product_request_via_orders,
    assign_product_ui,
)


def test_request_exclude(page: Page, context: dict) -> None:
    """Assign a product with two taxes via the client card and assert the payment
    request is DUE $12.61 (price + tax, exclusive mode)."""
    print("  Step 1: Assign payable_item1 with two taxes via the client card")
    assign_product_ui(page, context, product_name="payable_item1", taxes=assign_taxes(context))

    print("  Step 2: Product payment request is DUE $12.61")
    assert_product_request_via_orders(page, context, {
        "state": "DUE", "amount": "$12.61",
        "product_name": "payable_item1", "client_full_name": "first last",
    }, "payable_item1")

    print("  [OK] product payment request created (tax exclude) verified")
