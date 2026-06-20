# Auto-generated from script.md
# Source: tests/salsa/payments/packages/create_edit_reorder/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md
"""Create, edit and reorder packages with product add-ons (core BO package management).

Migrates automation-js features/salsa/packages.feature scenario
"Create, edit and reorder packages with products".
"""

import time

from playwright.sync_api import Page

from tests.salsa.payments.packages.packages_helpers import (
    assert_packages_list_order,
    create_package,
    create_product_via_api,
    edit_package,
    make_client,
    reorder_packages_api,
)


def test_create_edit_reorder(page: Page, context: dict) -> None:
    seq = str(int(time.time() * 1000))

    print("  Step 1: Create product 'payable_item1' ($10) via API")
    create_product_via_api(context, "payable_item1", "10",
                           description="description for payable item1")

    print("  Step 2: Create a fresh client via API")
    make_client(context, seq)

    print("  Step 3: Create 'package_1' (service, 2cr, $150, product x2, add-ons) via UI")
    create_package(
        page, context, name="package_1", service_name="service", amount="2", price="150",
        package_type="specific", product_name="payable_item1", product_quantity="2",
    )

    print("  Step 4: Create 'package_2' (r2p_event, 3cr, $250, product x3, add-ons) via UI")
    create_package(
        page, context, name="package_2", package_type="any", service_list=["r2p_event"],
        amount="3", price="250", product_name="payable_item1", product_quantity="3",
    )

    print("  Step 5: Assert packages list order [package_1, package_2]")
    assert_packages_list_order(page, context, ["package_1", "package_2"])

    print("  Step 6: Edit 'package_1' -> rename 'package_3', disable add-ons")
    edit_package(page, context, name="package_1", new_name="package_3", disable_addons=True)

    print("  Step 7: Assert packages list order [package_3, package_2]")
    assert_packages_list_order(page, context, ["package_3", "package_2"])

    print("  Step 8: Reorder packages via API (reverse active order)")
    reorder_packages_api(context)

    print("  Step 9: Assert packages list order [package_2, package_3]")
    assert_packages_list_order(page, context, ["package_2", "package_3"])
