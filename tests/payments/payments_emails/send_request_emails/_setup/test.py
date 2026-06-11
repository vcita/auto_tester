"""Setup for scenario 1 "Send payment request emails" (isolated account).

Mirrors the feature Background + the scenario's "denies point_of_sale", a $100
appointment service, an API appointment, and the mock gateway connection.

The service is seeded as "require to pay" rather than the legacy "suggest to pay":
invoicing the appointment is POV-routed via the Billing & Invoicing order row, which
only exists for a DUE (require-to-pay) request (same established pattern as
appointment_payments/invoiced_appointment). The emails under test (payment-request
link, invoice, payment-request link) are identical for either charge type, so there
is no email-scope loss.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import deny_features
from tests.payments.payments_emails.payments_emails_api import seed_client_service_appointment
from tests.payments.tips_settings.tips_gateway import connect_mock_gateway


def setup_send_request_emails(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Deny point_of_sale (non-POS send-link dialog)")
    deny_features(context, "point_of_sale")

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 3: Seed client + require-to-pay $100 service + appointment api1 (API)")
    seed_client_service_appointment(context, payment_setting="require to pay",
                                    price=100, service_name="service", identifier="api1")

    print("  Setup Step 4: Connect mock payment gateway")
    connect_mock_gateway(page, context)
    print("  [OK] setup complete - appointment api1 for 'first last' on 'service'")
