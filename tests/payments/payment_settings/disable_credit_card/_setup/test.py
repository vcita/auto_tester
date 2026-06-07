"""Setup for the disable-credit-card scenario.

Logs in to the isolated account (needed for the provider banner check + connecting the
mock gateway in the test) and creates the client used to open the make-payment form.
The gateway is connected in the test itself, after the provider banner is asserted (the
banner is only shown before a provider is connected, as in the legacy scenario).
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client


def setup_disable_credit_card(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Create client via API (with portal token)")
    stamp = int(time.time() * 1000)
    email = f"client{stamp}@vmeetme.com"
    client = create_client(context, "first1", "last1", email)
    context["cc_client"] = client
    context["cc_client_email"] = email

    print(f"  [OK] disable_credit_card setup complete - logged in, client '{client['full_name']}' ready")
