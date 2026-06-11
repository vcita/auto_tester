"""Setup for scenario 4 "payments confirmation emails via POS" (isolated account).

point_of_sale stays enabled (default). Seeds a require-to-pay $100 service, an API
appointment, and a $10 product assigned to the client. No gateway is connected
(the legacy scenario records offline Cash payments only).
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.payments.payments_emails.payments_emails_api import (
    seed_client_service_appointment,
    seed_product_and_assign,
)


def setup_payment_confirmation_emails_pos(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account (point_of_sale enabled)")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Seed client + require-to-pay $100 service + appointment api1 (API)")
    seed_client_service_appointment(context, payment_setting="require to pay",
                                    price=100, service_name="service", identifier="api1")

    print("  Setup Step 3: Create $10 product21 + assign to client (API)")
    seed_product_and_assign(context, name="product21", price=10,
                            description="description for payable item1")
    print("  [OK] setup complete - require-to-pay appointment api1 + product21 for 'first last'")
