# Auto-generated from script.md
# Source: tests/salsa/payments/packages/create_assign_exclude/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md
"""Create + assign a taxed package, assert the DUE total in tax-EXCLUDE mode + CP conversation.

Migrates automation-js features/salsa/packages.feature scenario
"Create and assign package, check payment request and conversation in CP".
"""

import time

from playwright.sync_api import Page

from tests.salsa.payments.packages.packages_helpers import (
    assert_client_package,
    assert_cp_conversation_title,
    assign_package_via_client_card,
    create_package,
    create_tax_via_api,
    get_client_package_id,
    make_client,
    track_for_cleanup,
)


def test_create_assign_exclude(page: Page, context: dict) -> None:
    seq = str(int(time.time() * 1000))
    tax1 = f"TS{seq}"
    tax2 = f"TS2{seq}"

    print("  Step 1: Create two taxes via API (13%, 13.13%)")
    create_tax_via_api(context, tax1, "13")
    create_tax_via_api(context, tax2, "13.13")

    print("  Step 2: Create a fresh client via API")
    client = make_client(context, seq)

    print("  Step 3: Create package 'package' (service, 2cr, $150, tax 13%) via UI")
    create_package(
        page, context, name="package", service_name="service", amount="2", price="150",
        package_type="specific", taxes=[{"name": tax1, "rate": "13"}],
    )

    print("  Step 4: Assign 'package' to the client via the client card (taxes 13% + 13.13%)")
    assign_package_via_client_card(
        page, context, client_id=client["id"], package_name="package",
        taxes=[{"name": tax1, "rate": "13"}, {"name": tax2, "rate": "13.13"}],
    )

    client_package_id = get_client_package_id(context, client["id"], "package")
    track_for_cleanup(context, client_package_id=client_package_id)

    print("  Step 5: Assert client-package request DUE $189.20 ($150.00 + Tax)")
    assert_client_package(
        page, context, client_package_id,
        {"state": "DUE", "amount": "$189.20 ($150.00 + Tax)",
         "client_full_name": "first last", "package_name": "package"},
    )

    print("  Step 6: Assert CP conversation includes 'Package added: package'")
    assert_cp_conversation_title(page, context, client["token"], "Package added: package")
