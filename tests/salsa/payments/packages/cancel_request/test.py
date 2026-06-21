# Auto-generated from script.md
# Source: tests/salsa/payments/packages/cancel_request/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md
"""Cancel (waive) a package payment request (-> CANCELLED $150.00).

Migrates automation-js features/salsa/packages.feature scenario
"cancel package payment request".
"""

import time

from playwright.sync_api import Page

from tests.account_api import assign_package_to_client, create_package_via_api
from tests.salsa.payments.packages.packages_helpers import (
    assert_client_package,
    cancel_request,
    get_client_package_id,
    make_client,
    track_for_cleanup,
)


def test_cancel_request(page: Page, context: dict) -> None:
    seq = str(int(time.time() * 1000))
    services = context["packages_services"]

    print("  Step 1: Create a fresh client via API")
    client = make_client(context, seq)

    print("  Step 2: Create package 'package' (specific r2p_event, 2cr, $150) via API")
    package = create_package_via_api(
        context, "package", services=[services["r2p_event"]], total_bookings=2, price=150,
    )
    track_for_cleanup(context, package_id=package["id"])

    print("  Step 3: Assign 'package' to the client via API")
    assign_package_to_client(context, client["id"], package["id"], 150)
    client_package_id = get_client_package_id(context, client["id"], "package")
    track_for_cleanup(context, client_package_id=client_package_id)

    print("  Step 4: Cancel (waive) the client-package payment request via UI")
    cancel_request(page, context, client_package_id)

    print("  Step 5: Assert client-package request CANCELLED $150.00 "
          "(API read-back confirms CANCELLED propagation first)")
    assert_client_package(
        page, context, client_package_id,
        {"state": "CANCELLED", "amount": "$150.00",
         "client_full_name": "first last", "package_name": "package"},
        client_id=client["id"],
    )
