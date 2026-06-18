# Auto-generated from script.md
# Source: tests/salsa/payments/cp_packages/redeem_and_repurchase/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md
"""Client uses his packages: redeem an appointment from a package, then re-purchase it.

Migrates automation-js features/salsa/cp/packages.feature
(scenario: client uses his packages, (redeem and repurchase)).

Packages are assigned to the client via API (independent of the purchase_packages test).
"""

from playwright.sync_api import Page

from tests.account_api import assign_package_to_client
from tests.salsa.payments.cp_packages.cp_packages_helpers import (
    assert_booking_confirmation,
    assert_description_page,
    assert_history_has_service,
    assert_purchased_packages,
    assert_scheduler_services,
    close_history_dialog,
    make_client,
    navigate_purchased_packages,
    open_history_dialog,
    open_portal,
    purchase_package,
    schedule_appointment,
    start_repurchase_from_package,
    start_scheduling_from_package,
)


def test_redeem_and_repurchase(page: Page, context: dict) -> None:
    packages = context["cp_packages_packages"]
    client = make_client(context)
    token = client["token"]
    package1 = packages["package1"]
    package2 = packages["package2"]

    print("  Step 1: Assign package1 + package2 to the client via API")
    assign_package_to_client(context, client["id"], package1["id"], package1["price"])
    assign_package_to_client(context, client["id"], package2["id"], package2["price"])

    cp_page, cp_context = open_portal(page, context, token)
    try:
        print("  Step 2: Client navigates to the purchased-packages page")
        navigate_purchased_packages(cp_page, context, token)

        print("  Step 3: Start the scheduling flow from package1")
        start_scheduling_from_package(cp_page, "package1")

        print("  Step 4: Scheduler services page shows r2p_appointment + s2p_appointment")
        assert_scheduler_services(cp_page, ["r2p_appointment", "s2p_appointment"])

        print("  Step 5: Schedule a new r2p_appointment")
        schedule_appointment(cp_page, "r2p_appointment")

        print("  Step 6: Booking confirmation 'Confirmed!' redeemed with package")
        assert_booking_confirmation(cp_page, title="Confirmed!", redeemed_with_package=True)

        print("  Step 7: Purchased-packages shows package2 active + package1 1/1 fully_redeemed")
        assert_purchased_packages(
            cp_page, context, token,
            [
                {"name": "package2", "used": "0", "total": "2",
                 "services": ["s2p_appointment"], "state": "active"},
                {"name": "package1", "used": "1", "total": "1",
                 "services": ["r2p_appointment", "s2p_appointment", "r2p_event"],
                 "state": "fully"},
            ],
        )

        print("  Step 8: package1 history dialog shows the r2p_appointment booking")
        open_history_dialog(cp_page, "package1")
        assert_history_has_service(cp_page, "r2p_appointment")
        close_history_dialog(cp_page)

        print("  Step 9: Re-purchase package1 from the finished package -> description page")
        navigate_purchased_packages(cp_page, context, token)
        start_repurchase_from_package(cp_page, context, "package1", package1["id"], token)
        assert_description_page(cp_page, "package1")

        print("  Step 10: Purchase package1 with a new card")
        purchase_package(cp_page, new_card=True)

        print("  Step 11: Purchased-packages shows package1 active + package2 + package1 fully_redeemed")
        assert_purchased_packages(
            cp_page, context, token,
            [
                {"name": "package1", "used": "0", "total": "1",
                 "services": ["r2p_appointment", "s2p_appointment", "r2p_event"], "state": "active"},
                {"name": "package2", "used": "0", "total": "2",
                 "services": ["s2p_appointment"], "state": "active"},
                {"name": "package1", "used": "1", "total": "1",
                 "services": ["r2p_appointment", "s2p_appointment", "r2p_event"],
                 "state": "fully"},
            ],
        )
        print("  [OK] redeem_and_repurchase: redeem + history + re-purchase verified")
    finally:
        cp_context.close()
