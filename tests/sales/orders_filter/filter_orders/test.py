# Source: tests/sales/orders_filter/filter_orders/script.md
# Migrated from automation-js/features/steps/orders.feature (VCITA2-13852)

from playwright.sync_api import Page

from tests.account_api import (
    assign_package_to_client,
    create_appointment_via_api,
    create_package_via_api,
)
from tests.sales.orders_filter.orders_filter_helpers import assert_orders_filtered

PACKAGE_NAME = "test_package"
PACKAGE_PRICE = "150"
PACKAGE_CREDITS = 2
PACKAGE_ORDER_TITLE = "test_package - Package purchased"


def test_filter_orders(page: Page, context: dict) -> None:
    """Filter the back-office Orders list by payable type and assert the exact,
    order-sensitive result lists for bookings, packages, both, and invoices."""
    client = context["orders_client"]
    service = context["orders_service"]

    print("  Step 1: Schedule a paid appointment via API (creates a booking order)")
    create_appointment_via_api(context, service, {"id": client["id"]})

    print("  Step 2: Orders filtered by 'bookings' shows ['service']")
    assert_orders_filtered(page, context, ["bookings"], [service["name"]])

    print("  Step 3: Create the package and assign it to the client via API")
    package = create_package_via_api(
        context,
        PACKAGE_NAME,
        services=[service],
        total_bookings=PACKAGE_CREDITS,
        price=PACKAGE_PRICE,
    )
    assign_package_to_client(context, client["id"], package["id"], PACKAGE_PRICE)

    print("  Step 4: Orders filtered by 'packages' shows the purchased package")
    assert_orders_filtered(page, context, ["packages"], [PACKAGE_ORDER_TITLE])

    print("  Step 5: Orders filtered by 'bookings'+'packages' shows both (package first)")
    assert_orders_filtered(
        page, context, ["bookings", "packages"], [PACKAGE_ORDER_TITLE, service["name"]]
    )

    print("  Step 6: Orders filtered by 'invoices' shows an empty list")
    assert_orders_filtered(page, context, ["invoices"], [])

    print("  [OK] order type filters verified")
