# Source: tests/payments/appointment_payments/invoiced_appointment/invoiced_appointment/script.md
# Migrated from automation-js/features/salsa/appointment-payments.feature (VCITA2-13857)

from playwright.sync_api import Page

from tests.salsa.payments.appointment_payments.appointment_payments_helpers import (
    assert_appt_payment_request,
    invoice_appointment,
    pay_for_invoice,
    search_payments,
)

INVOICE_NAME = "appointment_invoice"
INVOICE_FULL = "appointment_invoice #0000001"


def test_invoiced_appointment(page: Page, context: dict) -> None:
    """Invoice the appointment, pay the invoice in full, and assert the
    appointment payment request becomes PAID $100.00."""
    print("  Step 1: Invoice the appointment")
    invoice_appointment(page, context, INVOICE_NAME, "blablablabla", identifier="service")

    print("  Step 2: Pay the invoice $100")
    pay_for_invoice(page, context, INVOICE_FULL, "100")

    print("  Step 3: Appointment payment request is PAID $100.00")
    assert_appt_payment_request(page, context, {
        "state": "PAID", "amount": "$100.00",
        "client_full_name": "first last", "service_name": "service",
    }, identifier="service")

    print(f"  Step 4: Payments Received shows 'Payment for {INVOICE_FULL}'")
    search_payments(page, context, "first", f"Payment for {INVOICE_FULL}", expected_count=1)

    print("  [OK] pay-for-invoiced-appointment verified")
