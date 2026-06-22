"""Setup for scenario 2 "Send payment request emails via POS" (isolated account).

point_of_sale stays enabled (default) so take payment opens Point of Sale. Seeds a
require-to-pay $100 service, an API appointment, and connects the mock gateway.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.salsa.payments.payments_emails.payments_emails_api import seed_client_service_appointment
from tests.salsa.payments.tips_settings.tips_gateway import connect_mock_gateway


def setup_send_request_emails_pos(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account (point_of_sale enabled)")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Seed client + require-to-pay $100 service + appointment api1 (API)")
    seed_client_service_appointment(context, payment_setting="require to pay",
                                    price=100, service_name="service", identifier="api1")

    print("  Setup Step 3: Connect mock payment gateway")
    connect_mock_gateway(page, context)
    print("  [OK] setup complete - require-to-pay appointment api1 for 'first last'")
