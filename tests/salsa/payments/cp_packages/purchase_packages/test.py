# Auto-generated from script.md
# Source: tests/salsa/payments/cp_packages/purchase_packages/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md
"""Client purchases packages using the business purchase links (new card + saved card).

Migrates automation-js features/salsa/cp/packages.feature
(scenario: Client purchases packages using links from business).
"""

from playwright.sync_api import Page

from tests.salsa.payments.cp_packages.cp_packages_helpers import (
    assert_purchased_packages,
    make_client,
    open_packages_list,
    open_portal,
    open_single_package,
    purchase_package,
    select_package,
)


def test_purchase_packages(page: Page, context: dict) -> None:
    packages = context["cp_packages_packages"]
    client = make_client(context)
    token = client["token"]

    cp_page, cp_context = open_portal(page, context, token)
    try:
        print("  Step 1: Client accesses the purchase-packages link -> CP packages list page")
        open_packages_list(cp_page, context, token)

        print("  Step 2: Select package2 from the list -> package description page")
        select_package(cp_page, "package2")

        print("  Step 3: Purchase package2 with a NEW card (mock gateway popup)")
        purchase_package(cp_page, new_card=True)

        print("  Step 4: Purchased-packages page shows package2 (0/2, s2p_appointment, active)")
        assert_purchased_packages(
            cp_page, context, token,
            [
                {"name": "package2", "used": "0", "total": "2",
                 "services": ["s2p_appointment"], "state": "active"},
            ],
        )

        print("  Step 5: Access the single package1 purchase link -> description page")
        open_single_package(cp_page, context, packages["package1"]["id"], "package1", token)

        print("  Step 6: Purchase package1 with the SAVED card (no popup)")
        purchase_package(cp_page, new_card=False)

        print("  Step 7: Purchased-packages page shows package1 + package2 (both active)")
        assert_purchased_packages(
            cp_page, context, token,
            [
                {"name": "package1", "used": "0", "total": "1",
                 "services": ["r2p_appointment", "s2p_appointment", "r2p_event"], "state": "active"},
                {"name": "package2", "used": "0", "total": "2",
                 "services": ["s2p_appointment"], "state": "active"},
            ],
        )
        print("  [OK] purchase_packages: new-card + saved-card purchases verified")
    finally:
        cp_context.close()
