# Source: tests/payments/appointment_payments/edit_cancel_request/edit_cancel/script.md
# Migrated from automation-js/features/salsa/appointment-payments.feature (VCITA2-13857)

from playwright.sync_api import Page

from tests.salsa.payments.appointment_payments.appointment_payments_helpers import (
    assert_appt_payment_request,
    cancel_appt_payment_request,
    edit_appt_payment_amount,
)


def test_edit_cancel(page: Page, context: dict) -> None:
    """Edit the appointment payment request amount to $50 (NOT YET DUE $50.00),
    then cancel the payment request (CANCELLED $50.00)."""
    print("  Step 1: Edit payment request amount to $50")
    edit_appt_payment_amount(page, context, "50", identifier="service")
    assert_appt_payment_request(page, context, {
        "state": "NOT YET DUE", "amount": "$50.00",
        "client_full_name": "first last", "service_name": "service",
    }, identifier="service")

    print("  Step 2: Cancel the payment request")
    cancel_appt_payment_request(page, context, identifier="service")
    assert_appt_payment_request(page, context, {
        "state": "CANCELLED", "amount": "$50.00",
        "client_full_name": "first last", "service_name": "service",
    }, identifier="service")

    print("  [OK] appointment payment request edited then cancelled")
