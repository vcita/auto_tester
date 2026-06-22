# Source: tests/payments/product_payments/invoiced_product/invoiced/script.md
# Migrated from automation-js/features/salsa/products.feature (VCITA2-13858)

from playwright.sync_api import Page

from tests.salsa.payments.product_payments.product_payments_helpers import (
    assert_product_payment_request,
    invoice_product,
    pay_for_invoice,
    search_payments,
)

INVOICE_NAME = "product_invoice"
INVOICE_FULL = "product_invoice #0000001"


def test_invoiced(page: Page, context: dict) -> None:
    """Invoice the product, pay the invoice in full, and assert the product
    payment request becomes PAID $10.00."""
    print("  Step 1: Invoice the product")
    invoice_product(page, context, INVOICE_NAME, "blablablabla", product_name="payable_item1")

    print("  Step 2: Pay the invoice $10")
    pay_for_invoice(page, context, INVOICE_FULL, "10")

    print("  Step 3: Product payment request is PAID $10.00")
    assert_product_payment_request(page, context, {
        "state": "PAID", "amount": "$10.00",
        "product_name": "payable_item1", "client_full_name": "first last",
    }, "payable_item1")

    print(f"  Step 4: Payments Received shows 'Payment for {INVOICE_FULL}'")
    search_payments(page, context, "first", f"Payment for {INVOICE_FULL}", expected_count=1)

    print("  [OK] pay-for-invoiced-product verified")
