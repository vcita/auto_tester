# Source: tests/payments/appointment_payments/custom_fee_service/custom_fee_service/script.md
# Migrated from automation-js/features/salsa/appointment-payments.feature (VCITA2-13857)

from playwright.sync_api import Page

from tests.salsa.payments.appointment_payments.appointment_payments_helpers import (
    pay_custom_fee_via_pos,
    search_payments,
)


def test_custom_fee_service(page: Page, context: dict) -> None:
    """Record a POS payment for a price-varies appointment ($90, 13% tax, 10%
    discount) and assert the sale payment shows in Payments Received."""
    print("  Step 1: Take POS payment $90 + 13% tax + 10% discount (price varies)")
    pay_custom_fee_via_pos(
        page, context,
        amount="90", tax_label="TStax (13%)",
        discount_value="10", discount_type="percentage",
        identifier="service",
    )

    print("  Step 2: Payments Received shows 'Payment for Sale #1 - service'")
    search_payments(page, context, "first", "Payment for Sale #1 - service", expected_count=1)

    print("  [OK] custom-fee POS appointment payment verified")
