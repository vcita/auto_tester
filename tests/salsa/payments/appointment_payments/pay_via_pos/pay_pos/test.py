# Source: tests/payments/appointment_payments/pay_via_pos/pay_pos/script.md
# Migrated from automation-js/features/salsa/appointment-payments.feature (VCITA2-13857)

from playwright.sync_api import Page

from tests.salsa.payments.appointment_payments.appointment_payments_helpers import (
    assert_appt_payment_request,
    record_appt_payment_via_pos,
    search_payments,
)


def test_pay_pos(page: Page, context: dict) -> None:
    """Record the appointment payment request through Point of Sale and assert it
    is PAID $100.00, with the resulting sale in Payments Received."""
    print("  Step 1: Record-payment via Point of Sale")
    record_appt_payment_via_pos(page, context, identifier="service-rtp")

    print("  Step 2: Appointment payment request is PAID $100.00")
    assert_appt_payment_request(page, context, {
        "state": "PAID", "amount": "$100.00",
        "client_full_name": "first last", "service_name": "service-rtp",
    }, identifier="service-rtp")

    print("  Step 3: Payments Received shows 'Payment for Sale #1 - service-rtp'")
    search_payments(page, context, "first", "Payment for Sale #1 - service-rtp", expected_count=1)

    print("  [OK] pay-for-appointment via POS verified")
