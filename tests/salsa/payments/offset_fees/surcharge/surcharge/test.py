"""Surcharge (default 3%).

Migrates automation-js features/salsa/offset-fees.feature (scenario: Surcharge).
"""

from playwright.sync_api import Page

from tests.salsa.payments.offset_fees.offset_fees_checkout import (
    assert_fee_badge,
    assert_processing_fee_line,
    assert_summary_fee_row,
    open_client_portal,
    open_past_meeting_payment,
    proceed_and_assert_success,
)
from tests.salsa.payments.offset_fees.offset_fees_helpers import (
    assert_back_office_payment,
    enable_surcharge,
)


def test_surcharge(page: Page, context: dict) -> None:
    service_name = context["offset_service_name"]

    print("  Step 1: Enable surcharge (default 3%)...")
    enable_surcharge(page, context)

    print("  Step 2: Open the client portal and pay the past appointment...")
    open_client_portal(page, context)
    open_past_meeting_payment(page, context)

    print("  Step 3: Verify the surcharge at checkout...")
    assert_fee_badge(page, "+ 3%")
    assert_summary_fee_row(page, "Surcharge", "$3.00")
    assert_processing_fee_line(page)

    print("  Step 4: Proceed to payment and verify the success total ($103)...")
    proceed_and_assert_success(page, "$103.00")

    print("  Step 5: Verify the Back Office payment page ($103.00, fee $3.00)...")
    assert_back_office_payment(page, context, amount="$103.00", fee="$3.00", items=[service_name])

    print("  [OK] Surcharge (3%) shown at checkout and reflected in Back Office")
