# Source: tests/payments/payments_emails/payment_confirmation_emails_pos/confirmation_emails_pos/script.md
# Migrated from automation-js/features/salsa/payments-emails.feature (VCITA2-14027)

from playwright.sync_api import Page

from tests.email_api import wait_for_email_count
from tests.payments.payments_emails.payments_emails_confirm import (
    record_appointment_via_pos,
    record_for_client_via_pos,
)

PAYMENT_CONFIRMATION = "Payment Confirmation"


def test_confirmation_emails_pos(page: Page, context: dict) -> None:
    """Recording the appointment request and the client's open requests via POS each
    send the client a Payment Confirmation email."""
    client_name = context["payments_emails"]["client_name"]

    print("  Step 1: POS record-payment for appointment api1 -> Payment Confirmation email")
    record_appointment_via_pos(page, context, "api1")
    wait_for_email_count(context, PAYMENT_CONFIRMATION, 1)

    print("  Step 2: POS record all open requests for client -> 2nd Payment Confirmation email")
    record_for_client_via_pos(page, context, client_name)
    wait_for_email_count(context, PAYMENT_CONFIRMATION, 2)

    print("  [OK] POS payment confirmation emails verified")
