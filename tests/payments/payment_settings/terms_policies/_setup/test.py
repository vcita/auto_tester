"""Setup for the Terms and Policies scenario.

Mirrors the legacy precondition: log in to the isolated account and connect the mock
payment gateway (the terms & policies settings are exercised with a payment provider
connected, as in the legacy scenario).
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.payments.tips_settings.tips_gateway import connect_mock_gateway


def setup_terms_policies(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Connect the mock payment gateway (providers UI)")
    connect_mock_gateway(page, context)

    print("  [OK] terms_policies setup complete - logged in, mock gateway connected")
