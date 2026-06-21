# Auto-generated from script.md
# Source: tests/salsa/payments/packages/pay_via_pos/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md
"""Pay an any-service package via Point of Sale (-> PAID $150.00, Sale #1 searchable).

Migrates automation-js features/salsa/packages.feature scenario
"pay for assigned (any service) package with pos".
"""

import time

from playwright.sync_api import Page

from tests.salsa.payments.cp_payment_actions.cp_payment_actions_helpers import (
    assert_payment_in_search,
)
from tests.salsa.payments.packages.packages_helpers import (
    assert_client_package,
    assign_package_via_client_card,
    create_package,
    get_client_package_id,
    make_client,
    pay_client_package_via_pos,
    track_for_cleanup,
)


def test_pay_via_pos(page: Page, context: dict) -> None:
    seq = str(int(time.time() * 1000))

    print("  Step 1: Create a fresh client via API")
    client = make_client(context, seq)

    print("  Step 2: Create package 'bundle1' (any service, 5cr, $150) via UI")
    create_package(
        page, context, name="bundle1", package_type="any",
        service_list=["service", "r2p_event"], amount="5", price="150",
    )

    print("  Step 3: Assign 'bundle1' to the client via the client card")
    assign_package_via_client_card(
        page, context, client_id=client["id"], package_name="bundle1",
    )
    client_package_id = get_client_package_id(context, client["id"], "bundle1")
    track_for_cleanup(context, client_package_id=client_package_id)

    print("  Step 4: Pay the package full balance via the BO Take-payment record path (POS sale)")
    pay_client_package_via_pos(page, context, client_package_id, amount="150")

    print("  Step 5: Assert client-package request PAID $150.00 "
          "(API read-back confirms PAID propagation first)")
    assert_client_package(
        page, context, client_package_id,
        {"state": "PAID", "amount": "$150.00",
         "client_full_name": "first last", "package_name": "bundle1"},
        client_id=client["id"],
    )

    # Product change: on the current build a client-package "Take payment" opens the Take Payment
    # dialog directly (no POS sale page / `checkout-actions-activator` exists for a client-package
    # — verified live, see changelog), so recording the balance emits the standard package payment
    # title "Payment for <package> - Package purchased", NOT the legacy POS "Sale #N" title. The
    # in-scope coverage preserved here is: the full balance was paid via a real BO take-payment
    # action and the resulting payment is searchable in Payments Received.
    print("  Step 6: Assert 'Payment for bundle1 - Package purchased' in Payments Received")
    assert_payment_in_search(
        page, first_name="first",
        expected_substrings=["Payment for bundle1 - Package purchased"],
    )
