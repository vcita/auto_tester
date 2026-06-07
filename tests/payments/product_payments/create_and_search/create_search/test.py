# Source: tests/payments/product_payments/create_and_search/create_search/script.md
# Migrated from automation-js/features/salsa/products.feature (VCITA2-13858)

from playwright.sync_api import Page

from tests.payments.product_payments.product_payments_api import assign_taxes
from tests.payments.product_payments.product_payments_helpers import (
    create_product_ui,
    search_products_ui,
)


def test_create_search(page: Page, context: dict) -> None:
    """Create product2 via the Add product dialog and find it by name and SKU."""
    tax = assign_taxes(context)[0]

    print("  Step 1: Create product2 via the Add product dialog")
    create_product_ui(
        page, context,
        name="product2",
        description="description for payable item2",
        price="10",
        cost="5",
        sku="1234678",
        taxes=[tax],
    )

    print("  Step 2: Search by name 'product2' -> [product2]")
    search_products_ui(page, context, "product2", ["product2"])

    print("  Step 3: Search by SKU '1234678' -> [product2]")
    search_products_ui(page, context, "1234678", ["product2"])

    print("  [OK] product created and found by name and SKU")
