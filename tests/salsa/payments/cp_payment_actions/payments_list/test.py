"""CP payments list with multiple requests (product + invoice + package).

Migrates automation-js features/salsa/cp/payment-actions.feature
(Scenario: "Client portals payments list: client opens list with multiple requests").
"""

from playwright.sync_api import Page

from tests.account_api import assign_package_to_client, create_package_via_api
from tests.salsa.payments.cp_payment_actions.cp_payment_actions_api import (
    get_client_package_id,
    invoice_due_date,
    make_invoice_items,
)
from tests.salsa.payments.cp_payment_actions.cp_payment_actions_helpers import (
    assert_rows,
    open_payments_list,
    pay_one_item,
    record_package_payment,
    reopen_payments_list,
)
from tests.salsa.payments.invoices.invoice_billing_api import create_invoice_via_api
from tests.salsa.payments.product_payments.product_payments_api import (
    assign_product_via_api,
    create_product_via_api,
)


def test_payments_list(page: Page, context: dict) -> None:
    store = context["cp_payment_actions"]
    service = store["service"]
    client = store["client"]

    # Point the product_payments store at the setup client so assign_product_via_api uses
    # the same client that owns the invoice + package (one client owns all three requests).
    context.setdefault("product_payments", {})["client"] = {
        "id": client["id"], "name": client["name"], "first": client["first"],
        "email": client["email"], "portal_token": client["portal_token"],
    }

    print("  Step 1: Create invoice ($20 + 10% tax -> $22.00) via API")
    create_invoice_via_api(
        context, title="invoice", client_id=client["id"], address="persepolis, persia",
        items=make_invoice_items(title="product_item200", price="20",
                                 description="short desc",
                                 taxes=[{"name": "tax1", "rate": "10"}]),
        due_date=invoice_due_date(),
    )

    print("  Step 2: Create product 'product2' ($10) via API")
    create_product_via_api(context, name="product2", price="10",
                           description="description for payable item2")

    print("  Step 3: Create package 'package1' ($150, specific, total_bookings 2) via API")
    package = create_package_via_api(
        context, name="package1",
        services=[{"id": service["id"], "name": service["name"],
                   "price": "100", "currency": "USD"}],
        total_bookings=2, price="150",
    )

    print("  Step 4: Assign product2 to the client via API")
    assign_product_via_api(context, product_name="product2")

    print("  Step 5: Assign package1 to the client via API")
    assign_package_to_client(context, client["id"], package["id"], price="150")

    print("  Step 6: Record a $100 payment on the package in the back office")
    client_package_id = get_client_package_id(context, client["id"], "package1")
    record_package_payment(page, context, client_package_id=client_package_id, amount="100")

    print("  Step 7: Open the CP payments list and assert 3 rows")
    cp_page, cp_context, cp_frame = open_payments_list(page, context, client["portal_token"])
    try:
        assert_rows(cp_frame, [
            {"item_name": "product2", "price": "$10.00", "sub_title_type": "Product"},
            {"item_name": "invoice #0000001", "price": "$22.00", "sub_title_type": "Invoice"},
            {"item_name": "package1", "price": "$50.00", "sub_title_type": "Package",
             "comment": "Out of $150.00"},
        ])

        print("  Step 8: Pay the package1 item from the list (mock gateway)")
        pay_one_item(cp_page, cp_frame, "package1")

        print("  Step 9: Re-open the payments list and assert it now shows 2 rows (package1 gone)")
        cp_frame = reopen_payments_list(cp_page, context, client["portal_token"])
        assert_rows(cp_frame, [
            {"item_name": "product2", "price": "$10.00", "sub_title_type": "Product"},
            {"item_name": "invoice #0000001", "price": "$22.00", "sub_title_type": "Invoice"},
        ])
        print("  [OK] CP payments list: 3 rows -> paid package1 -> 2 rows")
    finally:
        cp_context.close()
