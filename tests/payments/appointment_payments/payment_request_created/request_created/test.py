# Source: tests/payments/appointment_payments/payment_request_created/request_created/script.md
# Migrated from automation-js/features/salsa/appointment-payments.feature (VCITA2-13857)

from playwright.sync_api import Page

from tests.payments.appointment_payments.appointment_payments_helpers import (
    assert_appt_payment_request,
    cancel_appointment,
)


def test_request_created(page: Page, context: dict) -> None:
    """Assert the scheduled appointment's payment request is NOT YET DUE $100.00,
    cancel the appointment, then assert the request is CANCELLED $100.00."""
    print("  Step 1: Appointment payment request is NOT YET DUE $100.00")
    assert_appt_payment_request(page, context, {
        "state": "NOT YET DUE", "amount": "$100.00",
        "client_full_name": "first last", "service_name": "service",
    }, identifier="service")

    print("  Step 2: Cancel the appointment")
    cancel_appointment(page, context, identifier="service")

    print("  Step 3: Appointment payment request is CANCELLED $100.00")
    assert_appt_payment_request(page, context, {
        "state": "CANCELLED", "amount": "$100.00",
        "client_full_name": "first last", "service_name": "service",
        "meeting_identifier": "this",
    })

    print("  [OK] appointment payment request created then cancelled")
