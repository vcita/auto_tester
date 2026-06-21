# Auto-generated from script.md
# Source: tests/salsa/payments/packages/usage_history/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md
"""View package usage history and open the meeting (usage dialog -> COMPLETED meeting).

Migrates automation-js features/salsa/packages.feature scenario "View package usage history".
"""

import time

from playwright.sync_api import Page

from tests.account_api import assign_package_to_client, create_package_via_api
from tests.salsa.payments.packages.packages_helpers import (
    assert_credit_quota,
    assert_history_has_service,
    assert_meeting_page,
    click_usage_item,
    create_redeemable_service_via_api,
    get_client_package_id,
    make_client,
    mark_appointment_completed,
    open_usage_history,
    redeem_appt_via_api,
    schedule_appointment_via_api,
    track_for_cleanup,
)


def test_usage_history(page: Page, context: dict) -> None:
    seq = str(int(time.time() * 1000))
    # Per-test unique client (the shared account accumulates clients across tests). This test
    # asserts the usage-history service + meeting, not the client name.
    client = make_client(context, seq, unique_name=True)
    client_id = client["id"]

    # A per-test "display a fee" service the redeem action renders reliably for (the BO calendar
    # appointment + the setup's "suggest to pay" service do not expose `redeem_package` on this
    # build — verified live). The usage-history/meeting assertions use this service's name.
    svc_name = f"usage_svc_{seq}"
    svc = create_redeemable_service_via_api(context, svc_name, price=100)

    print(f"  Step 1: Create package 'package' (specific service '{svc_name}', 2cr, $150) via API")
    package = create_package_via_api(
        context, "package", services=[svc], total_bookings=2, price=150,
    )
    track_for_cleanup(context, package_id=package["id"])

    print("  Step 2: Assign 'package' to the client via API")
    assign_package_to_client(context, client_id, package["id"], 150)
    client_package_id = get_client_package_id(context, client_id, "package")
    track_for_cleanup(context, client_package_id=client_package_id)

    print("  Step 3: Schedule meeting1 as an appointment (out-of-scope prerequisite)")
    meeting1 = schedule_appointment_via_api(context, service=svc, client_id=client_id)

    print("  Step 4: Redeem meeting1 against the package (consumes a credit), then ensure completed")
    # The BO `redeem_package` button does not render deterministically on this build (verified live),
    # so the redemption uses the same backend call the button makes (payment/client_packages
    # update_usage). The meeting is then marked COMPLETED in the UI (asserted in step 8).
    redeem_appt_via_api(context, meeting1, client_id)
    mark_appointment_completed(page, context, meeting1)

    print("  Step 5: Assert client credit quota == 1")
    assert_credit_quota(page, context, client_id, 1)

    print(f"  Step 6: Open the usage-history dialog and assert it lists '{svc_name}'")
    history_frame = open_usage_history(page, context, client_package_id)
    assert_history_has_service(history_frame, svc_name)

    print("  Step 7: Click the usage item to navigate to the meeting")
    click_usage_item(history_frame, svc_name)

    print("  Step 8: Assert meeting page opened (service, COMPLETED)")
    assert_meeting_page(page, meeting_name=svc_name, meeting_state="COMPLETED")
