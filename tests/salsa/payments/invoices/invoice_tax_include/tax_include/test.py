from playwright.sync_api import Page

from tests.salsa.payments.invoices.invoice_billing_ui import (
    assert_invoice_page,
    create_and_send_invoice,
)

FAST_UI_TIMEOUT = 5000


def test_tax_include(page: Page, context: dict) -> None:
    page.set_default_timeout(FAST_UI_TIMEOUT)
    page.set_default_navigation_timeout(20000)

    tax = {"name": context["invoice_tax_name"], "rate": context["invoice_tax_rate"]}
    new_items = [
        {"product_name": "product", "description": "short desc", "price": "15",
         "save_item": True, "taxes": [tax]},
        {"product_name": "product1", "description": "long desc", "price": "50",
         "save_item": False},
    ]

    print("  Step 1: Create + send invoice 'product_invoice' (tax mode include)")
    create_and_send_invoice(
        page, context, name="product_invoice", client_name="first last",
        billing_address="blablablabla", new_items=new_items,
    )
    print("  Step 2: Assert invoice page (#0000001, ISSUED, $65.00)")
    assert_invoice_page(
        page, context, title="product_invoice", number=1, client="first last",
        state="ISSUED", amount="$65.00",
    )
