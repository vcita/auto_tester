"""Setup for the CP deny-payments-view scenario (API-only).

Creates the client (with its portal token) used to open the client portal. No UI login
is needed: the setting is changed via API and the portal is opened directly as the client.
"""

import time

from playwright.sync_api import Page

from tests.account_api import create_client


def setup_cp_deny_payments(page: Page, context: dict) -> None:
    print("  Setup Step 1: Create client via API (with portal token)")
    stamp = int(time.time() * 1000)
    email = f"client{stamp}@vmeetme.com"
    client = create_client(context, "first1", "last1", email)
    context["cp_client"] = client
    context["cp_client_token"] = client["token"]

    print(f"  [OK] cp_deny_payments setup complete - client '{client['full_name']}' ready")
