# Source: tests/payments/payments_emails/send_request_emails/request_emails/script.md
# Migrated from automation-js/features/salsa/payments-emails.feature (VCITA2-14027)

from playwright.sync_api import Page

from tests.email_api import wait_for_email_count
from tests.payments.appointment_payments.appointment_payments_helpers import invoice_appointment
from tests.payments.payments_emails.payments_emails_helpers import (
    send_appointment_payment_link,
    send_invoice_payment_link,
)

PAYMENT_REQUEST = "New payment request from "
INVOICE = "New invoice from "


def test_request_emails(page: Page, context: dict) -> None:
    """Appointment send-link, invoice, and invoice send-link each send the client
    the expected email (2 payment-request + 1 invoice)."""
    client_id = context["appointment_payments"]["client"]["id"]

    print("  Step 1: Send appointment api1 payment-request link by email")
    send_appointment_payment_link(page, context, "api1")
    wait_for_email_count(context, PAYMENT_REQUEST, 1, match="prefix")

    print("  Step 2: Invoice appointment api1 -> New invoice email")
    invoice_appointment(page, context, "new_invoice", "blablablabla", identifier="service")
    wait_for_email_count(context, INVOICE, 1, match="prefix")

    print("  Step 3: Send invoice payment-request link by email -> 2nd request email")
    send_invoice_payment_link(page, context, client_id)
    wait_for_email_count(context, PAYMENT_REQUEST, 2, match="prefix")

    print("  [OK] payment-request + invoice emails verified")
