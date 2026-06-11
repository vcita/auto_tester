# Source: tests/payments/payments_emails/payment_confirmation_emails/confirmation_emails/script.md
# Migrated from automation-js/features/salsa/payments-emails.feature (VCITA2-14027)

from playwright.sync_api import Page

from tests.email_api import wait_for_email_count
from tests.payments.payments_emails.payments_emails_confirm import (
    close_client_balance,
    pay_appointment_with_receipt,
)

PAYMENT_CONFIRMATION = "Payment Confirmation"


def test_confirmation_emails(page: Page, context: dict) -> None:
    """Paying the appointment and closing the client balance each send the client a
    Payment Confirmation email."""
    client_id = context["appointment_payments"]["client"]["id"]

    print("  Step 1: Pay $30 for appointment api1 -> Payment Confirmation email")
    pay_appointment_with_receipt(page, context, "30", "api1")
    wait_for_email_count(context, PAYMENT_CONFIRMATION, 1)

    print("  Step 2: Close client balance (record/ACH) -> 2nd Payment Confirmation email")
    close_client_balance(page, context, client_id, method="ACH")
    wait_for_email_count(context, PAYMENT_CONFIRMATION, 2)

    print("  [OK] payment confirmation emails verified")
