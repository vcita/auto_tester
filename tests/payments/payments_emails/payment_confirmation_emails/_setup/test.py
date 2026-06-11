"""Setup for scenario 3 "payments confirmation emails" (isolated account).

Mirrors the feature Background + "denies point_of_sale", a suggest-to-pay $100
service, an API appointment, and a $10 product assigned to the client.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import deny_features
from tests.payments.payments_emails.payments_emails_api import (
    seed_client_service_appointment,
    seed_product_and_assign,
)


def setup_payment_confirmation_emails(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Deny point_of_sale (record dialog, not POS)")
    deny_features(context, "point_of_sale")

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 3: Seed client + suggest-to-pay $100 service + appointment api1 (API)")
    seed_client_service_appointment(context, payment_setting="suggest to pay",
                                    price=100, service_name="service", identifier="api1")

    print("  Setup Step 4: Create $10 product21 + assign to client (API)")
    seed_product_and_assign(context, name="product21", price=10,
                            description="description for payable item1")
    print("  [OK] setup complete - appointment api1 + assigned product21 for 'first last'")
