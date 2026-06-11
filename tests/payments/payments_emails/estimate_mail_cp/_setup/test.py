"""Setup for scenario 6 "Client receives estimate mail, and opens CP page".

Mirrors the feature Background client + the "creates products via api" Given. The
estimate is created in the test body (it is the action that sends the email).
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.payments.payments_emails.payments_emails_api import seed_client_and_product


def setup_estimate_mail_cp(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Seed client 'first last' + product21 ($10) (API)")
    seed_client_and_product(context, product_name="product21", price=10,
                            description="description for payable item21",
                            first="first", last="last")
    print("  [OK] setup complete - client + product21 ready")
