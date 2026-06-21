# Auto-generated from script.md
# Source: tests/salsa/payments/packages/invoice_package/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md
"""Pay an invoiced single-service package (create -> assign -> invoice -> pay -> PAID).

Migrates automation-js features/salsa/packages.feature scenario
"user pays for an invoiced client (single-service) package".
"""

import time

from playwright.sync_api import Page

from tests.salsa.payments.cp_payment_actions.cp_payment_actions_helpers import (
    assert_payment_in_search,
)
from tests.salsa.payments.event_payments.event_payments_helpers import pay_for_invoice
from tests.salsa.payments.packages.packages_helpers import (
    assert_client_package,
    assign_package_via_client_card,
    create_package,
    get_client_package_id,
    invoice_client_package,
    make_client,
    track_for_cleanup,
)


def test_invoice_package(page: Page, context: dict) -> None:
    seq = str(int(time.time() * 1000))

    print("  Step 1: Create a fresh client via API")
    client = make_client(context, seq)

    print("  Step 2: Create package 'single1' (service, 2cr, $150) via UI")
    create_package(
        page, context, name="single1", service_name="service", amount="2", price="150",
        package_type="specific",
    )

    print("  Step 3: Assign 'single1' to the client via the client card")
    assign_package_via_client_card(
        page, context, client_id=client["id"], package_name="single1",
    )
    client_package_id = get_client_package_id(context, client["id"], "single1")
    track_for_cleanup(context, client_package_id=client_package_id)

    print("  Step 4: Invoice the package (single1_invoice) from the client-package card")
    invoice_client_package(
        page, context, client_package_id,
        invoice_name="single1_invoice", billing_address="blablablabla",
    )

    print("  Step 5: Pay the invoice single1_invoice #0000001 ($150)")
    pay_for_invoice(page, context, "single1_invoice #0000001", "150")

    print("  Step 6: Assert client-package request PAID $150.00 "
          "(API read-back confirms PAID propagation first)")
    assert_client_package(
        page, context, client_package_id,
        {"state": "PAID", "amount": "$150.00",
         "client_full_name": "first last", "package_name": "single1"},
        client_id=client["id"],
    )

    print("  Step 7: Assert 'Payment for single1_invoice #0000001' in Payments Received")
    assert_payment_in_search(
        page, first_name="first",
        expected_substrings=["Payment for single1_invoice #0000001"],
    )
