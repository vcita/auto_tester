# Source: tests/payments/appointment_payments/pay_for_appointment/pay_appt/script.md
# Migrated from automation-js/features/salsa/appointment-payments.feature (VCITA2-13857)

from playwright.sync_api import Page

from tests.payments.appointment_payments.appointment_payments_helpers import (
    assert_appt_payment_request,
    pay_for_appointment,
    search_payments,
)


def test_pay_appt(page: Page, context: dict) -> None:
    """Record a $10 payment (DUE $90.00 of $100.00) then a $90 payment
    (PAID $100.00), verifying Payments Received after each."""
    payment_title = "Payment for service"

    print("  Step 1: Pay $10 -> DUE $90.00 (out of $100.00)")
    pay_for_appointment(page, context, "10", identifier="service")
    assert_appt_payment_request(page, context, {
        "state": "DUE", "amount": "$90.00 (out of $100.00)",
        "client_full_name": "first last", "service_name": "service",
    }, identifier="service")
    search_payments(page, context, "first", payment_title, expected_count=1)

    print("  Step 2: Pay $90 -> PAID $100.00")
    pay_for_appointment(page, context, "90", identifier="service")
    assert_appt_payment_request(page, context, {
        "state": "PAID", "amount": "$100.00",
        "client_full_name": "first last", "service_name": "service",
    }, identifier="service")
    search_payments(page, context, "first", payment_title, expected_count=2)

    print("  [OK] pay-for-appointment partial + full verified")
