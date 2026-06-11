"""Setup for scenario 5 "Package assigned to client" (isolated account).

Mirrors the feature Background + a suggest-to-pay $100 service and a specific-service
package (created, not assigned - the assignment is the action under test).
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.salsa.payments.payments_emails.payments_emails_api import seed_client_and_service, seed_package


def setup_package_assigned(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Seed client + suggest-to-pay $100 service (API)")
    seed_client_and_service(context, payment_setting="suggest to pay", price=100,
                            service_name="service")

    print("  Setup Step 3: Create 'package' (specific, service, 2 credits, $150) (API)")
    seed_package(context, name="package", credits=2, price=150)
    print("  [OK] setup complete - package created for 'first last'")
