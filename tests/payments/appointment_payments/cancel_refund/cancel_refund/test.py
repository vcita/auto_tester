# Source: tests/payments/appointment_payments/cancel_refund/cancel_refund/script.md
# Migrated from automation-js/features/salsa/appointment-payments.feature (VCITA2-13857)

from playwright.sync_api import Page

from tests.payments.appointment_payments.appointment_payments_helpers import (
    assert_appt_payment_request,
    assert_payment_refunded,
    cancel_appointment,
    pay_for_appointment,
)


def test_cancel_refund(page: Page, context: dict) -> None:
    """Pay $100 in full, cancel the appointment with a refund, then assert the
    request is CANCELLED $100.00 and the payment was refunded."""
    print("  Step 1: Pay $100 in full")
    pay_for_appointment(page, context, "100", identifier="service")

    print("  Step 2: Cancel the appointment with a refund")
    cancel_appointment(page, context, identifier="service", refund=True)

    print("  Step 3: Appointment payment request is CANCELLED $100.00")
    assert_appt_payment_request(page, context, {
        "state": "CANCELLED", "amount": "$100.00",
        "client_full_name": "first last", "service_name": "service",
    }, identifier="service")

    print("  Step 4: Payment 'Payment for service' was refunded")
    assert_payment_refunded(page, context, "Payment for service", "first")

    print("  [OK] cancel & refund paid appointment verified")
