"""Convenience fee - flat ($1).

Migrates automation-js features/salsa/offset-fees.feature
(scenario: Convenience fee - flat fee).
"""

from playwright.sync_api import Page

from tests.payments.offset_fees.offset_fees_checkout import (
    assert_fee_badge,
    assert_processing_fee_line,
    assert_summary_fee_row,
    open_client_portal,
    open_past_meeting_payment,
    proceed_and_assert_success,
)
from tests.payments.offset_fees.offset_fees_helpers import (
    assert_back_office_payment,
    enable_convenience_fee,
)


def test_convenience_fee_flat(page: Page, context: dict) -> None:
    service_name = context["offset_service_name"]

    print("  Step 1: Enable a $1 flat convenience fee...")
    enable_convenience_fee(page, context, fee_format="flat", value="1")

    print("  Step 2: Open the client portal and pay the past appointment...")
    open_client_portal(page, context)
    open_past_meeting_payment(page, context)

    print("  Step 3: Verify the convenience fee at checkout...")
    assert_fee_badge(page, "+ $1.00")
    assert_summary_fee_row(page, "Convenience fee", "$1.00")
    assert_processing_fee_line(page)

    print("  Step 4: Proceed to payment and verify the success total ($101)...")
    proceed_and_assert_success(page, "$101.00")

    print("  Step 5: Verify the Back Office payment page ($101.00, fee $1.00)...")
    assert_back_office_payment(page, context, amount="$101.00", fee="$1.00", items=[service_name])

    print("  [OK] Convenience fee ($1 flat) shown at checkout and reflected in Back Office")
