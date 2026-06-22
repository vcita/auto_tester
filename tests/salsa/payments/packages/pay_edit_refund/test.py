# Auto-generated from script.md
# Source: tests/salsa/payments/packages/pay_edit_refund/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md
"""Pay, edit and complete an any-service package request (partial -> edit -> PAID).

Migrates automation-js features/salsa/packages.feature scenario
"pay, edit, and refund assigned (any service) package".
"""

import time

from playwright.sync_api import Page

from tests.account_api import deny_features
from tests.salsa.payments.cp_payment_actions.cp_payment_actions_helpers import (
    record_package_payment,
)
from tests.salsa.payments.packages.packages_helpers import (
    assert_client_package,
    assert_payment_count_in_search,
    assign_package_via_client_card,
    create_package,
    edit_request_amount,
    get_client_package_id,
    make_client,
    track_for_cleanup,
)


def test_pay_edit_refund(page: Page, context: dict) -> None:
    seq = str(int(time.time() * 1000))

    print("  Step 1: Deny point_of_sale via API (forces record-payment dialog)")
    deny_features(context, "point_of_sale")

    print("  Step 2: Create a fresh client via API")
    client = make_client(context, seq)

    print("  Step 3: Create package 'bundle1' (any service, 5cr, $150) via UI")
    create_package(
        page, context, name="bundle1", package_type="any",
        service_list=["service", "r2p_event"], amount="5", price="150",
    )

    print("  Step 4: Assign 'bundle1' to the client via the client card")
    assign_package_via_client_card(
        page, context, client_id=client["id"], package_name="bundle1",
    )
    client_package_id = get_client_package_id(context, client["id"], "bundle1")
    track_for_cleanup(context, client_package_id=client_package_id)

    print("  Step 5: Pay $10 -> DUE $140.00 (out of $150.00)")
    record_package_payment(page, context, client_package_id=client_package_id, amount="10")
    assert_client_package(
        page, context, client_package_id,
        {"state": "DUE", "amount": "$140.00 (out of $150.00)",
         "client_full_name": "first last", "package_name": "bundle1"},
        client_id=client["id"],
    )

    print("  Step 6: Edit request amount to $50 -> DUE $40.00 (out of $50.00)")
    edit_request_amount(page, context, client_package_id, "50")
    assert_client_package(
        page, context, client_package_id,
        {"state": "DUE", "amount": "$40.00 (out of $50.00)",
         "client_full_name": "first last", "package_name": "bundle1"},
        client_id=client["id"],
    )

    print("  Step 7: Pay $40 -> PAID $50.00")
    record_package_payment(page, context, client_package_id=client_package_id, amount="40")
    assert_client_package(
        page, context, client_package_id,
        {"state": "PAID", "amount": "$50.00",
         "client_full_name": "first last", "package_name": "bundle1"},
        client_id=client["id"],
    )

    print("  Step 8: Assert two 'Payment for bundle1 - Package purchased' in Payments Received")
    assert_payment_count_in_search(
        page, first_name="first",
        title="Payment for bundle1 - Package purchased", expected_count=2,
    )
