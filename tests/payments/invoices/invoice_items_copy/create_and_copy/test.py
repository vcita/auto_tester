from playwright.sync_api import Page

from tests.payments.invoices.invoice_billing_ui import (
    assert_invoice_page,
    copy_invoice,
    create_and_send_invoice,
    search_orders,
)

FAST_UI_TIMEOUT = 5000


def test_create_and_copy(page: Page, context: dict) -> None:
    page.set_default_timeout(FAST_UI_TIMEOUT)
    page.set_default_navigation_timeout(20000)

    tax = {"name": context["invoice_tax_name"], "rate": context["invoice_tax_rate"]}
    new_items = [
        {"product_name": "product", "description": "short desc", "price": "15",
         "save_item": True, "taxes": [tax]},
        {"product_name": "product1", "description": "long desc", "price": "50",
         "save_item": False},
    ]

    print("  Step 1: Create + send invoice 'product_invoice' with new items")
    create_and_send_invoice(
        page, context, name="product_invoice", client_name="first last",
        billing_address="blablablabla", new_items=new_items,
    )
    print("  Step 2: Assert invoice page (#0000001, ISSUED, $66.95)")
    assert_invoice_page(
        page, context, title="product_invoice", number=1, client="first last",
        state="ISSUED", amount="$66.95",
    )
    print("  Step 3: Assert orders list after first invoice")
    search_orders(page, ["product_invoice #0000001"])

    print("  Step 4: Create + send invoice 'new_invoice' reusing existing items")
    create_and_send_invoice(
        page, context, name="new_invoice", client_name="first last",
        existing_items=[context["invoice_service_name"], "product"],
    )
    print("  Step 5: Assert orders list after second invoice")
    search_orders(page, ["new_invoice #0000002", "product_invoice #0000001"])

    print("  Step 6: Copy the newest invoice for 'first last'")
    copy_invoice(page, context, "first last")
    print("  Step 7: Assert orders list after copy")
    search_orders(page, [
        "new_invoice #0000003", "new_invoice #0000002", "product_invoice #0000001",
    ])
